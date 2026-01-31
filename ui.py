import pyqtgraph as pg
import numpy as np
from PyQt6 import QtWidgets, QtCore, QtGui
from typing import Callable

class HelpDialog(QtWidgets.QDialog):
    """
    A custom dialog to display help content with rich text/Markdown support.
    """
    def __init__(self, content: str, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Rotor Chain Simulation Help")
        self.resize(600, 500)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        self.browser = QtWidgets.QTextBrowser()
        self.browser.setMarkdown(content)
        self.browser.setOpenExternalLinks(True)
        layout.addWidget(self.browser)
        
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        )
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

class ControlPanel(QtWidgets.QWidget):
    """
    Control panel for the Rotor Chain simulation.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMinimumWidth(250)
        self.layout = QtWidgets.QVBoxLayout(self)
        
        # Header with Help
        header_layout = QtWidgets.QHBoxLayout()
        self.help_button = QtWidgets.QPushButton("?")
        self.help_button.setFixedWidth(30)
        self.help_button.setToolTip("Show Help")
        header_layout.addStretch()
        header_layout.addWidget(self.help_button)
        self.layout.addLayout(header_layout)
        
        # Number of rotors control
        self.n_label = QtWidgets.QLabel("Number of Rotors (N):")
        self.n_spin = QtWidgets.QSpinBox()
        self.n_spin.setRange(2, 500)
        self.n_spin.setValue(50)
        self.layout.addWidget(self.n_label)
        self.layout.addWidget(self.n_spin)
        
        self.layout.addSpacing(10)
        
        # Initial Conditions Preset
        self.preset_label = QtWidgets.QLabel("Initial Condition Preset:")
        self.preset_combo = QtWidgets.QComboBox()
        # Ensure items are added clearly
        self.preset_combo.addItem("Random Angles")
        self.preset_combo.addItem("Twisted")
        self.preset_combo.addItem("Domain Wall")
        self.preset_combo.addItem("Single Kick")
        self.preset_combo.addItem("Thermalized")
        self.layout.addWidget(self.preset_label)
        self.layout.addWidget(self.preset_combo)
        
        # Winding number / Index for presets
        self.k_widget = QtWidgets.QWidget()
        self.k_layout = QtWidgets.QHBoxLayout(self.k_widget)
        self.k_layout.setContentsMargins(0, 0, 0, 0)
        self.k_label = QtWidgets.QLabel("Winding (k):")
        self.k_spin = QtWidgets.QSpinBox()
        self.k_spin.setRange(-250, 250)
        self.k_spin.setValue(1)
        self.k_layout.addWidget(self.k_label)
        self.k_layout.addWidget(self.k_spin)
        self.layout.addWidget(self.k_widget)
        
        # Initialize visibility
        self.k_widget.setVisible(False)
        
        # Connect internal visibility toggle
        self.preset_combo.currentIndexChanged.connect(self._handle_preset_ui_change)
        
        self.layout.addSpacing(10)
        
        # J coupling slider
        self.j_label = QtWidgets.QLabel("Coupling (J): 1.00")
        self.j_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.j_slider.setRange(0, 500)  # 0.0 to 5.0
        self.j_slider.setValue(100)
        self.j_slider.valueChanged.connect(self._on_j_changed)
        self.layout.addWidget(self.j_label)
        self.layout.addWidget(self.j_slider)
        
        # M field slider
        self.m_label = QtWidgets.QLabel("Field (M): 0.00")
        self.m_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.m_slider.setRange(0, 1000)  # 0.0 to 10.0
        self.m_slider.setValue(0)
        self.m_slider.valueChanged.connect(self._on_m_changed)
        self.layout.addWidget(self.m_label)
        self.layout.addWidget(self.m_slider)
        
        self.layout.addSpacing(20)
        
        # Buttons
        self.start_stop_button = QtWidgets.QPushButton("Start")
        self.start_stop_button.setCheckable(True)
        self.layout.addWidget(self.start_stop_button)
        
        self.reset_button = QtWidgets.QPushButton("Reset")
        self.layout.addWidget(self.reset_button)
        
        self.layout.addSpacing(20)
        
        # Energy monitor
        self.energy_label = QtWidgets.QLabel("Energy per Rotor: N/A")
        self.layout.addWidget(self.energy_label)
        
        self.layout.addSpacing(20)
        
        # Order parameter plot
        self.order_label = QtWidgets.QLabel("Order Parameter (r):")
        self.layout.addWidget(self.order_label)
        self.order_plot = pg.PlotWidget()
        self.order_plot.setBackground('k')
        self.order_plot.showGrid(x=True, y=True, alpha=0.3)
        self.order_plot.setYRange(0, 1.05)
        self.order_plot.setXRange(0, 10, padding=0)
        self.order_plot.setFixedHeight(150)
        
        # Configure axes
        font = QtGui.QFont()
        font.setPointSize(8)
        self.order_plot.getAxis('bottom').setTickFont(font)
        self.order_plot.getAxis('bottom').setTickSpacing(5, 5)
        self.order_plot.getAxis('left').setTickFont(font)
        self.order_plot.getAxis('left').setTickSpacing(0.5, 0.5)
        
        self.order_curve = self.order_plot.plot(pen=pg.mkPen('y', width=1.5))
        self.layout.addWidget(self.order_plot)
        
        # Kinetic energy heatmap
        self.heatmap_label = QtWidgets.QLabel("Kinetic Energy Heatmap:")
        self.layout.addWidget(self.heatmap_label)
        
        self.heatmap_plot = pg.PlotWidget()
        self.heatmap_plot.setFixedHeight(75)
        self.heatmap_plot.setMenuEnabled(False)
        self.heatmap_plot.showAxis('left', False)
        self.heatmap_plot.showAxis('bottom', False)
        self.heatmap_plot.setMouseEnabled(x=False, y=False)
        
        self.heatmap_image = pg.ImageItem()
        # Use 'inferno' colormap for heat
        colormap = pg.colormap.get('inferno')
        self.heatmap_image.setLookupTable(colormap.getLookupTable())
        self.heatmap_plot.addItem(self.heatmap_image)
        
        self.layout.addWidget(self.heatmap_plot)
        
        self.layout.addStretch()
        
        # Callbacks for external connection
        self.j_callback: Callable[[float], None] = lambda x: None
        self.m_callback: Callable[[float], None] = lambda x: None

    def _handle_preset_ui_change(self, index: int):
        # 1: "Twisted", 3: "Single Kick"
        if index == 1:
            self.k_label.setText("Winding (k):")
            self.k_widget.setVisible(True)
        elif index == 3:
            self.k_label.setText("Rotor Index:")
            self.k_widget.setVisible(True)
        else:
            self.k_widget.setVisible(False)

    def _on_j_changed(self, value: int):
        j = value / 100.0
        self.j_label.setText(f"Coupling (J): {j:.2f}")
        self.j_callback(j)

    def _on_m_changed(self, value: int):
        m = value / 100.0
        self.m_label.setText(f"Field (M): {m:.2f}")
        self.m_callback(m)

    def update_order_plot(self, times: list[float], values: list[float]):
        """Update the order parameter plot with new data."""
        self.order_curve.setData(times, values)
        if times:
            t_now = times[-1]
            if t_now > 10:
                self.order_plot.setXRange(t_now - 10, t_now, padding=0)
            else:
                self.order_plot.setXRange(0, 10, padding=0)
        else:
            self.order_plot.setXRange(0, 10, padding=0)

    def update_energy_heatmap(self, omega_sq: np.ndarray):
        """Update the kinetic energy heatmap."""
        # Reshape to Nx1 for a horizontal strip (width=N, height=1)
        # In pyqtgraph's default 'col-major' axisOrder, image data is (width, height)
        data = omega_sq.reshape(-1, 1)
        self.heatmap_image.setImage(data, autoLevels=True)
        # Set the plot range to match the number of rotors
        self.heatmap_plot.setXRange(0, omega_sq.shape[0], padding=0)
        self.heatmap_plot.setYRange(0, 1, padding=0)

    def set_j_callback(self, callback: Callable[[float], None]):
        self.j_callback = callback

    def set_m_callback(self, callback: Callable[[float], None]):
        self.m_callback = callback

    def set_simulation_running(self, running: bool):
        """Enable or disable controls that should not be changed during simulation."""
        self.n_spin.setEnabled(not running)
        self.preset_combo.setEnabled(not running)
        self.k_spin.setEnabled(not running)
