import numpy as np
import pyqtgraph as pg
from PyQt6 import QtCore

class RotorVisualizer(pg.GraphicsLayoutWidget):
    """
    Visualizes a chain of rotors using pyqtgraph as an embeddable widget.
    """

    def __init__(self, n_rotors: int, parent=None):
        super().__init__(parent=parent)
        
        # Configure the plot
        self.plot = self.addPlot()
        self.plot.setAspectLocked(True)
        self.plot.showAxis('left', False)
        self.plot.showAxis('bottom', False)
        self.plot.setMenuEnabled(False)
        
        # Positions of the rotor centers on a circle of radius R
        self.r_circle = 10.0
        # Rotate the whole picture: offset by -pi/2
        self.rotation_offset = -np.pi / 2
        self.mean_max_radius = 5.0
        
        # Stabilization: Fix the range so the circle doesn't jump
        padding = 3.0
        self.plot.setXRange(-self.r_circle - padding, self.r_circle + padding)
        self.plot.setYRange(-self.r_circle - padding, self.r_circle + padding)
        self.plot.setMouseEnabled(x=False, y=False)
        
        # --- Reference Circles ---
        
        center_circle_phi = np.linspace(0, 2 * np.pi, 200)
        
        # 1. Circle through the centers of the rotor needles
        self.plot.plot(
            self.r_circle * np.cos(center_circle_phi), 
            self.r_circle * np.sin(center_circle_phi), 
            pen=pg.mkPen(color=(80, 80, 80), width=1),
            antialias=True
        )

        # 2. Concentric circles for mean orientation magnitude
        # Intermediate circles (r=0.25, 0.5, 0.75) - faint
        for r_factor in [0.25, 0.5, 0.75]:
            radius = self.mean_max_radius * r_factor
            self.plot.plot(
                radius * np.cos(center_circle_phi), 
                radius * np.sin(center_circle_phi), 
                pen=pg.mkPen(color=(60, 60, 0), width=1),
                antialias=True
            )

        # Main circle (r=1)
        self.plot.plot(
            self.mean_max_radius * np.cos(center_circle_phi), 
            self.mean_max_radius * np.sin(center_circle_phi), 
            pen=pg.mkPen(color=(150, 150, 0), width=1.5),
            antialias=True
        )

        # --- Dynamic Elements ---

        # Rotor needles
        self.needles = pg.PlotCurveItem()
        self.plot.addItem(self.needles)
        
        # Colored dots at the tips
        self.tips = pg.ScatterPlotItem(pen=None, brush='r')
        self.plot.addItem(self.tips)
        
        # Mean direction needle (centered at origin)
        self.mean_needle = pg.PlotCurveItem(pen=pg.mkPen('y', width=3))
        self.plot.addItem(self.mean_needle)
        
        # Arrowhead for mean direction
        self.mean_arrow = pg.ArrowItem(angle=0, tipAngle=30, baseAngle=20, headLen=15, tailLen=0, brush='y', pen=None)
        self.plot.addItem(self.mean_arrow)

        self.set_n_rotors(n_rotors)

    def set_n_rotors(self, n_rotors: int):
        """Update the number of rotors and rebuild dependent geometry."""
        self.n_rotors = n_rotors
        
        # Internal phi (spacing)
        self.phi_internal = np.linspace(0, 2 * np.pi, n_rotors, endpoint=False)
        # Plot phi (rotated)
        self.phi_plot = self.phi_internal + self.rotation_offset
        
        self.centers_x = self.r_circle * np.cos(self.phi_plot)
        self.centers_y = self.r_circle * np.sin(self.phi_plot)

        # Length of the "compass needles" scales with N to fill space without overlap
        self.needle_length = min(3.5, (np.pi * self.r_circle) / n_rotors)
        
        # Scale needle width and tip size
        self.needles.setPen(pg.mkPen('w', width=max(1, min(3, 100 // n_rotors))))
        tip_size = max(3, min(12, 250 // n_rotors))
        self.tips.setSize(tip_size)

    def update_rotors(self, theta: np.ndarray):
        """
        Update the visualization with new rotor angles.
        
        Args:
            theta: Array of rotor angles.
        """
        # Absolute angle in the plot: theta=0 is radial + rotation offset
        angle = self.phi_plot + theta
        
        # Calculate start and end points of each needle
        dx = (self.needle_length / 2) * np.cos(angle)
        dy = (self.needle_length / 2) * np.sin(angle)
        
        x0 = self.centers_x - dx
        y0 = self.centers_y - dy
        x1 = self.centers_x + dx
        y1 = self.centers_y + dy
        
        # Create an array of (x, y) coordinates for pairs of points
        plot_x = np.empty(2 * self.n_rotors)
        plot_y = np.empty(2 * self.n_rotors)
        
        plot_x[0::2] = x0
        plot_x[1::2] = x1
        
        plot_y[0::2] = y0
        plot_y[1::2] = y1
        
        self.needles.setData(plot_x, plot_y, connect='pairs')
        
        # Update tips
        self.tips.setData(x1, y1)

        # Update mean direction
        # 1. The length represents the internal order parameter
        mean_theta_x = np.mean(np.cos(theta))
        mean_theta_y = np.mean(np.sin(theta))
        r = np.sqrt(mean_theta_x**2 + mean_theta_y**2)
        mean_theta = np.arctan2(mean_theta_y, mean_theta_x)
        
        # 2. Visual mean direction (rotated)
        # If mean_theta=0, it points vertical down. 
        # Standard angle for 'down' is -pi/2.
        # So visual_angle = mean_theta - pi/2
        visual_mean_angle = mean_theta + self.rotation_offset
        
        m_len = self.mean_max_radius * r
        mx_end = m_len * np.cos(visual_mean_angle)
        my_end = m_len * np.sin(visual_mean_angle)
        
        self.mean_needle.setData(np.array([0, mx_end]), np.array([0, my_end]))
        
        # Update mean arrow
        self.mean_arrow.setPos(mx_end, my_end)
        self.mean_arrow.setStyle(angle=180 - np.degrees(visual_mean_angle))