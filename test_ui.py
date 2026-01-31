import pytest
import numpy as np
from PyQt6 import QtCore
from main import MainWindow

@pytest.fixture
def app(qtbot):
    window = MainWindow(n_rotors=10)
    qtbot.addWidget(window)
    return window

def test_initial_state(app):
    """Verify initial window state."""
    assert app.windowTitle() == "Rotor Chain Simulation"
    assert app.n_rotors == 10
    assert not app.timer.isActive()

def test_toggle_simulation(app, qtbot):
    """Verify that clicking Start/Stop toggles the timer."""
    # Start
    qtbot.mouseClick(app.controls.start_stop_button, QtCore.Qt.MouseButton.LeftButton)
    assert app.timer.isActive()
    assert app.controls.start_stop_button.text() == "Stop"
    
    # Stop
    qtbot.mouseClick(app.controls.start_stop_button, QtCore.Qt.MouseButton.LeftButton)
    assert not app.timer.isActive()
    assert app.controls.start_stop_button.text() == "Start"

def test_j_slider_updates_engine(app, qtbot):
    """Verify that moving the J slider updates the engine parameters."""
    initial_j = app.engine.params.j_coupling
    # Slider range is 0-500, value 100 means J=1.0
    # Let's set it to 200 (J=2.0)
    app.controls.j_slider.setValue(200)
    assert app.engine.params.j_coupling == 2.0
    assert app.controls.j_label.text() == "Coupling (J): 2.00"

def test_m_slider_updates_engine(app, qtbot):
    """Verify that moving the M slider updates the engine parameters."""
    app.controls.m_slider.setValue(50) # M = 0.5
    assert app.engine.params.m_field == 0.5
    assert app.controls.m_label.text() == "Field (M): 0.50"

def test_preset_change_updates_state(app, qtbot):
    """Verify that changing the preset re-initializes the simulation."""
    # Default is Random Angles. Change to Twisted.
    # index 1 is Twisted
    with qtbot.waitSignal(app.controls.preset_combo.currentIndexChanged):
        app.controls.preset_combo.setCurrentIndex(1)
    
    # After change, reset_simulation is called, and y0 is updated.
    # For Twisted with k=1, N=10, y should be [0, 2pi/10, 4pi/10, ...]
    expected_theta = (2 * np.pi * 1 * np.arange(10)) / 10
    assert np.allclose(app.engine.theta, expected_theta)
