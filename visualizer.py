import numpy as np
import pyqtgraph as pg
from PyQt6 import QtCore, QtWidgets
from typing import Optional, Callable
from simulation import RotorChain

class RotorVisualizer:
    """
    Visualizes a chain of rotors using pyqtgraph.
    """

    def __init__(self, n_rotors: int):
        self.n_rotors = n_rotors
        self.app = QtWidgets.QApplication.instance()
        if self.app is None:
            self.app = QtWidgets.QApplication([])
            
        self.win = pg.GraphicsLayoutWidget(show=True, title="Rotor Chain Simulation")
        self.plot = self.win.addPlot()
        self.plot.setAspectLocked(True)
        
        # Positions of the rotor centers on a circle of radius R
        self.r_circle = 10.0
        self.phi = np.linspace(0, 2 * np.pi, n_rotors, endpoint=False)
        self.centers_x = self.r_circle * np.cos(self.phi)
        self.centers_y = self.r_circle * np.sin(self.phi)
        
        # Length of the "compass needles"
        self.needle_length = 1.5
        
        # We will use a single PlotCurveItem to draw all needles as separate segments
        # To draw multiple segments in one call, we can use NaN to separate them.
        self.needles = pg.PlotCurveItem(pen=pg.mkPen('w', width=2))
        self.plot.addItem(self.needles)
        
        # Add a unit circle for reference
        circle_phi = np.linspace(0, 2 * np.pi, 100)
        self.plot.plot(self.r_circle * np.cos(circle_phi), self.r_circle * np.sin(circle_phi), pen=pg.mkPen(0.3, 0.3, 0.3))

        self.timer = QtCore.QTimer()
        self.update_callback: Optional[Callable[[], None]] = None

    def update_rotors(self, theta: np.ndarray):
        """
        Update the visualization with new rotor angles.
        
        Args:
            theta: Array of rotor angles.
        """
        # Calculate start and end points of each needle
        dx = (self.needle_length / 2) * np.cos(theta)
        dy = (self.needle_length / 2) * np.sin(theta)
        
        x0 = self.centers_x - dx
        y0 = self.centers_y - dy
        x1 = self.centers_x + dx
        y1 = self.centers_y + dy
        
        # Create an array of (x, y) coordinates with NaNs between segments
        # Each segment has 2 points. Total 3 points per rotor including NaN.
        plot_x = np.empty(3 * self.n_rotors)
        plot_y = np.empty(3 * self.n_rotors)
        
        plot_x[0::3] = x0
        plot_x[1::3] = x1
        plot_x[2::3] = np.nan
        
        plot_y[0::3] = y0
        plot_y[1::3] = y1
        plot_y[2::3] = np.nan
        
        self.needles.setData(plot_x, plot_y)

    def start(self, callback: Callable[[], None], fps: int = 60):
        """
        Start the animation loop.
        
        Args:
            callback: Function to call on each frame.
            fps: Desired frames per second.
        """
        self.update_callback = callback
        self.timer.timeout.connect(self.update_callback)
        self.timer.start(int(1000 / fps))
        self.app.exec()
