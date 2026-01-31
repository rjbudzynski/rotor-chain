import numpy as np
import pytest
from simulation import SimulationEngine, SimulationParams

def test_engine_init():
    params = SimulationParams(n_rotors=10, j_coupling=1.0, m_field=0.5)
    engine = SimulationEngine(params)
    assert engine.params == params
    assert len(engine.y) == 20
    assert engine.t == 0.0

def test_engine_set_state():
    params = SimulationParams(n_rotors=5, j_coupling=1.0, m_field=0.0)
    engine = SimulationEngine(params)
    y_new = np.random.rand(10)
    engine.set_state(y_new, t=1.5)
    assert np.allclose(engine.y, y_new)
    assert engine.t == 1.5

def test_engine_step():
    params = SimulationParams(n_rotors=10, j_coupling=1.0, m_field=0.0)
    engine = SimulationEngine(params)
    y0 = np.zeros(20)
    y0[0] = 0.1
    engine.set_state(y0)
    
    success = engine.step(0.1)
    assert success
    assert engine.t == pytest.approx(0.1)
    assert not np.allclose(engine.y, y0)

def test_engine_update_params():
    params = SimulationParams(n_rotors=10, j_coupling=1.0, m_field=0.0)
    engine = SimulationEngine(params)
    engine.update_params(j=2.0, m=0.3)
    assert engine.params.j_coupling == 2.0
    assert engine.params.m_field == 0.3
    assert engine.params.n_rotors == 10
    assert engine.chain.params.j_coupling == 2.0

def test_engine_get_order_parameter():
    params = SimulationParams(n_rotors=10, j_coupling=1.0, m_field=0.0)
    engine = SimulationEngine(params)
    # All at 0 => r = 1
    engine.set_state(np.zeros(20))
    assert engine.get_order_parameter() == pytest.approx(1.0)
    
    # Spread out => r < 1
    y = np.zeros(20)
    y[:10] = np.linspace(0, 2*np.pi, 10, endpoint=False)
    engine.set_state(y)
    assert engine.get_order_parameter() == pytest.approx(0.0)
