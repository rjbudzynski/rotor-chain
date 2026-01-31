import numpy as np
import pytest
from simulation import SimulationEngine, SimulationParams

def test_verlet_energy_conservation():
    """Verify that Velocity Verlet conserves energy better than RK45 (implicitly)."""
    # Using a high coupling and large-ish N to see if energy stays stable
    params = SimulationParams(n_rotors=20, j_coupling=2.0, m_field=0.5)
    engine = SimulationEngine(params)
    engine.substeps = 20 # More substeps for better stability
    
    # Random initial state
    np.random.seed(42)
    y0 = np.random.uniform(-np.pi, np.pi, 40)
    engine.set_state(y0)
    
    initial_energy = engine.get_energy()
    
    # Simulate for 100 steps of dt=0.02 (total 2.0s)
    for _ in range(100):
        engine.step(0.02)
        
    final_energy = engine.get_energy()
    
    # For a symplectic integrator, energy error should be small and non-accumulating
    # 1e-6 is a very tight tolerance for 2s of simulation with 100 frames
    assert np.isclose(final_energy, initial_energy, rtol=1e-6)

def test_verlet_field_energy_conservation():
    """Verify energy conservation with non-zero field M."""
    params = SimulationParams(n_rotors=10, j_coupling=1.0, m_field=1.0)
    engine = SimulationEngine(params)
    engine.substeps = 50
    
    y0 = np.zeros(20)
    y0[0] = 0.5 # perturb one rotor
    engine.set_state(y0)
    
    initial_energy = engine.get_energy()
    
    for _ in range(50):
        engine.step(0.02)
        
    final_energy = engine.get_energy()
    assert np.isclose(final_energy, initial_energy, rtol=1e-7)
