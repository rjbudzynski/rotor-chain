import numpy as np
from simulation import RotorChain, SimulationParams
from visualizer import RotorVisualizer
import time

def main():
    # Parameters
    n_rotors = 50
    j_coupling = 1.0
    m_field = 0.0  # Set to 0 for the initial prototype
    
    params = SimulationParams(n_rotors=n_rotors, j_coupling=j_coupling, m_field=m_field)
    chain = RotorChain(params)
    
    # Initial conditions: theta_0 = pi - 0.01, others 0
    y0 = np.zeros(2 * n_rotors)
    y0[0] = np.pi - 0.01
    
    current_state = y0
    current_time = 0.0
    dt = 0.02  # Time step for each frame
    
    viz = RotorVisualizer(n_rotors)
    
    # Performance tracking
    last_time = time.time()
    
    def update():
        nonlocal current_state, current_time, last_time
        
        # Advance simulation
        t_span = (current_time, current_time + dt)
        sol = chain.simulate(current_state, t_span)
        
        if sol.success:
            current_state = sol.y[:, -1]
            current_time += dt
            
            # Update visualization
            viz.update_rotors(current_state[:n_rotors])
        
        # Optional: Print real-time info
        # now = time.time()
        # fps = 1.0 / (now - last_time)
        # last_time = now
        # print(f"Time: {current_time:.2f}, FPS: {fps:.1f}", end='\r')

    print("Starting simulation...")
    print(f"N={n_rotors}, J={j_coupling}, M={m_field}")
    print("Initial condition: theta_0 = pi - 0.01, others 0.")
    
    viz.start(update, fps=60)

if __name__ == "__main__":
    main()