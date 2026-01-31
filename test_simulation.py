import numpy as np
import pytest
from simulation import RotorChain, SimulationParams

def test_energy_conservation():
    """Verify that energy is conserved when M=0."""
    params = SimulationParams(n_rotors=10, j_coupling=1.0, m_field=0.0)
    chain = RotorChain(params)
    
    # Initial conditions
    y0 = np.zeros(20)
    y0[0] = np.pi - 0.01  # theta_0
    # No initial momenta, so energy is purely potential initially
    
    initial_energy = chain.hamiltonian(y0)
    
    # Simulate for a while
    t_span = (0, 10.0)
    t_eval = np.linspace(0, 10.0, 100)
    sol = chain.simulate(y0, t_span, t_eval)
    
    # Check energy at each step
    energies = [chain.hamiltonian(sol.y[:, i]) for i in range(sol.y.shape[1])]
    
    # Energy should be conserved to within integrator tolerance
    # Initial RK45 with default tolerances might have some drift, 
    # but for 10s it should be small.
    for energy in energies:
        assert np.isclose(energy, initial_energy, rtol=1e-5)

def test_periodic_boundary_conditions():
    """Verify that neighbors are correctly handled at boundaries."""
    params = SimulationParams(n_rotors=3, j_coupling=1.0, m_field=0.0)
    chain = RotorChain(params)
    
    # theta = [0.1, 0.2, 0.3], omega = [0, 0, 0]
    y = np.array([0.1, 0.2, 0.3, 0.0, 0.0, 0.0])
    dy = chain.equations_of_motion(0, y)
    
    # d_omega_0 = J * (sin(theta_0 - theta_1) + sin(theta_0 - theta_2))
    # d_omega_0 = 1.0 * (sin(0.1 - 0.2) + sin(0.1 - 0.3))
    expected_d_omega_0 = (np.sin(0.1 - 0.2) + np.sin(0.1 - 0.3))
    assert np.isclose(dy[3], expected_d_omega_0)
    
    # d_omega_2 = J * (sin(theta_2 - theta_0) + sin(theta_2 - theta_1))
    # d_omega_2 = 1.0 * (sin(0.3 - 0.1) + sin(0.3 - 0.2))
    expected_d_omega_2 = (np.sin(0.3 - 0.1) + np.sin(0.3 - 0.2))
    assert np.isclose(dy[5], expected_d_omega_2)

def test_external_field():
    """Verify that external field M affects d_omega correctly."""
    m_val = 0.5
    params = SimulationParams(n_rotors=2, j_coupling=0.0, m_field=m_val)
    chain = RotorChain(params)
    
    y = np.array([0.1, 0.2, 0.0, 0.0])
    dy = chain.equations_of_motion(0, y)
    
    # With J=0, d_omega should be exactly M
    assert np.allclose(dy[2:], m_val)

def test_initial_conditions_prototype():
    """Check the specific initial conditions mentioned in the prompt."""
    n = 5
    params = SimulationParams(n_rotors=n, j_coupling=1.0, m_field=0.0)
    chain = RotorChain(params)
    
    y0 = np.zeros(2 * n)
    y0[0] = np.pi - 0.01
    
    sol = chain.simulate(y0, (0, 1.0))
    assert sol.success
    assert sol.y.shape[0] == 2 * n
