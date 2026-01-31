import sys
import os
import numpy as np
from PyQt6 import QtWidgets, QtCore, QtGui
from simulation import RotorChain, SimulationParams
from visualizer import RotorVisualizer
from ui import ControlPanel

class MainWindow(QtWidgets.QMainWindow):
    """
    Main window for the Rotor Chain simulation application.
    """
    
    def __init__(self, n_rotors: int):
        super().__init__()
        self.setWindowTitle("Rotor Chain Simulation")
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        
        # Simulation parameters
        self.n_rotors = n_rotors
        self.j_coupling = 1.0
        self.m_field = 0.0
        
        self.params = SimulationParams(n_rotors=n_rotors, j_coupling=self.j_coupling, m_field=self.m_field)
        self.chain = RotorChain(self.params)
        
        # State
        self.current_time = 0.0
        self.dt = 0.02
        self.order_history: list[tuple[float, float]] = []
        
        # UI
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QHBoxLayout(self.central_widget)
        
        self.visualizer = RotorVisualizer(n_rotors)
        self.layout.addWidget(self.visualizer, stretch=4)
        
        self.controls = ControlPanel()
        self.layout.addWidget(self.controls, stretch=1)
        
        # Connect controls
        self.controls.n_spin.valueChanged.connect(self.reinit_simulation)
        self.controls.preset_combo.currentIndexChanged.connect(lambda: self.reinit_simulation(self.n_rotors))
        self.controls.k_spin.valueChanged.connect(lambda: self.reinit_simulation(self.n_rotors))
        self.controls.set_j_callback(self.update_j)
        self.controls.set_m_callback(self.update_m)
        self.controls.start_stop_button.toggled.connect(self.toggle_simulation)
        self.controls.reset_button.clicked.connect(self.reset_simulation)
        self.controls.help_button.clicked.connect(self.show_help)
        
        # Timer for simulation loop
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.simulation_step)
        
        # Initial draw
        self.y0 = self.get_initial_state()
        self.current_state = self.y0.copy()
        self.visualizer.update_rotors(self.current_state[:n_rotors])
        self.update_energy_display()

    def get_initial_state(self) -> np.ndarray:
        """Generate initial state based on the selected preset."""
        n = self.n_rotors
        y0 = np.zeros(2 * n)
        
        preset = self.controls.preset_combo.currentText()
        
        if preset == "Random Angles":
            # theta_i from [-pi, pi)
            y0[:n] = np.random.uniform(-np.pi, np.pi, n)
        elif preset == "Twisted":
            # theta_i = 2*pi*k*i/N
            k = self.controls.k_spin.value()
            y0[:n] = (2 * np.pi * k * np.arange(n)) / n
        elif preset == "Domain Wall":
            # Half at 0, half at pi
            half = n // 2
            y0[:half] = 0.0
            y0[half:n] = np.pi
            # Tiny velocity perturbation to break unstable equilibrium
            y0[n] = 1e-6
        elif preset == "Single Kick (Prototype)":
            y0[0] = np.pi - 0.01
            
        return y0

    def reinit_simulation(self, n_rotors: int):
        """Re-initialize the simulation with a new number of rotors or preset."""
        self.n_rotors = n_rotors
        self.params = SimulationParams(n_rotors=n_rotors, j_coupling=self.j_coupling, m_field=self.m_field)
        self.chain = RotorChain(self.params)
        
        # Reset state based on current preset
        self.y0 = self.get_initial_state()
        
        # Re-initialize visualizer
        self.layout.removeWidget(self.visualizer)
        self.visualizer.deleteLater()
        self.visualizer = RotorVisualizer(n_rotors)
        self.layout.insertWidget(0, self.visualizer, stretch=4)
        
        self.reset_simulation()

    def update_j(self, j: float):
        self.j_coupling = j
        self.chain.params = SimulationParams(n_rotors=self.n_rotors, j_coupling=self.j_coupling, m_field=self.m_field)

    def update_m(self, m: float):
        self.m_field = m
        self.chain.params = SimulationParams(n_rotors=self.n_rotors, j_coupling=self.j_coupling, m_field=self.m_field)

    def toggle_simulation(self, started: bool):
        self.controls.set_simulation_running(started)
        if started:
            self.controls.start_stop_button.setText("Stop")
            self.timer.start(int(1000 / 60))
        else:
            self.controls.start_stop_button.setText("Start")
            self.timer.stop()

    def show_help(self):
        """Display the help dialog with content from HELP.md."""
        import os
        from ui import HelpDialog
        help_path = os.path.join(os.path.dirname(__file__), "HELP.md")
        try:
            with open(help_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            dialog = HelpDialog(content, self)
            dialog.exec()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not load HELP.md: {e}")

    def reset_simulation(self):
        # Stop simulation if it is running
        if self.controls.start_stop_button.isChecked():
            self.controls.start_stop_button.setChecked(False)
            # This will trigger toggle_simulation(False) and stop the timer
        
        self.current_state = self.y0.copy()
        self.current_time = 0.0
        self.order_history = []
        self.visualizer.update_rotors(self.current_state[:self.n_rotors])
        # Update energy display on reset
        self.update_energy_display()
        # Update order plot on reset
        self.controls.update_order_plot([], [])

    def update_energy_display(self):
        energy = self.chain.hamiltonian(self.current_state)
        mean_energy = energy / self.n_rotors
        self.controls.energy_label.setText(f"Energy per Rotor: {mean_energy:.4f}")

    def simulation_step(self):
        t_span = (self.current_time, self.current_time + self.dt)
        sol = self.chain.simulate(self.current_state, t_span)
        
        if sol.success:
            self.current_state = sol.y[:, -1]
            self.current_time += self.dt
            
            # Calculate order parameter r
            theta = self.current_state[:self.n_rotors]
            r = np.sqrt(np.mean(np.cos(theta))**2 + np.mean(np.sin(theta))**2)
            self.order_history.append((self.current_time, r))
            
            # Prune history to 10s window
            while self.order_history and self.order_history[0][0] < self.current_time - 10:
                self.order_history.pop(0)
            
            # Update visualization
            self.visualizer.update_rotors(theta)
            self.update_energy_display()
            
            # Update order parameter plot
            times = [h[0] for h in self.order_history]
            values = [h[1] for h in self.order_history]
            self.controls.update_order_plot(times, values)

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("RotorChainSimulation")
    app.setApplicationDisplayName("Rotor Chain Simulation")
    app.setOrganizationName("RotorChainProject")
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), "icon.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QtGui.QIcon(icon_path))
    
    n_rotors = 50
    window = MainWindow(n_rotors)
    window.resize(1000, 700)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
