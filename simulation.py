import numpy as np
from scipy.integrate import solve_ivp
from typing import NamedTuple, Tuple

class SimulationParams(NamedTuple):
    """Parameters for the rotor chain simulation."""
    n_rotors: int
    j_coupling: float
    m_field: float

class RotorChain:
    """
    Represents a chain of coupled planar rotors.
    
    The Hamiltonian is given by:
    H = 1/2 * sum(omega_i^2) + J * sum(1 - cos(theta_i - theta_{i+1})) - M * sum(cos(theta_i))
    """

    def __init__(self, params: SimulationParams):
        """
        Initialize the rotor chain with given parameters.
        
        Args:
            params: The physical parameters of the system.
        """
        self.params = params

    def equations_of_motion(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Calculate the time derivatives of the state vector.
        
        Args:
            t: Current time.
            y: State vector [theta_0, ..., theta_{n-1}, omega_0, ..., omega_{n-1}].
            
        Returns:
            Derivatives [d_theta_0, ..., d_omega_{n-1}].
        """
        n = self.params.n_rotors
        theta = y[:n]
        omega = y[n:]
        
        # d_omega = -dH/d_theta
        # dH/d_theta = J * sin(theta_i - theta_{i+1}) - J * sin(theta_{i-1} - theta_i) - M
        #            = J * sin(theta_i - theta_{i+1}) + J * sin(theta_i - theta_{i-1}) - M
        # So d_omega = -J * sin(theta_i - theta_{i+1}) - J * sin(theta_i - theta_{i-1}) + M
        # Wait, I previously had this same formula. Let's re-verify the derivative.
        
        # H = 0.5 * sum(omega^2) - J * sum(1 - cos(theta_i - theta_{i+1})) - M * sum(theta_i)
        # dH/d_theta_i = -J * d/d_theta_i [ (1 - cos(theta_i - theta_{i+1})) + (1 - cos(theta_{i-1} - theta_i)) ] - M
        # d/d_theta_i [1 - cos(theta_i - theta_{i+1})] = sin(theta_i - theta_{i+1})
        # d/d_theta_i [1 - cos(theta_{i-1} - theta_i)] = -sin(theta_{i-1} - theta_i) = sin(theta_i - theta_{i-1})
        # So dH/d_theta_i = -J * (sin(theta_i - theta_{i+1}) + sin(theta_i - theta_{i-1})) - M
        # d_omega_i = -dH/d_theta_i = J * (sin(theta_i - theta_{i+1}) + sin(theta_i - theta_{i-1})) + M
        
        # H_field = -M * sum(cos(theta_i))
        # dH/d_theta_i = M * sin(theta_i)
        # d_omega_i = -dH/d_theta_i = -M * sin(theta_i)
        
        theta_plus = np.roll(theta, -1)
        theta_minus = np.roll(theta, 1)
        
        d_theta = omega
        d_omega = (-self.params.j_coupling * (np.sin(theta - theta_plus) + np.sin(theta - theta_minus)) 
                   - self.params.m_field * np.sin(theta))
        
        return np.concatenate([d_theta, d_omega])

    def hamiltonian(self, y: np.ndarray) -> float:
        """
        Calculate the Hamiltonian (total energy) of the system.
        
        Args:
            y: State vector.
            
        Returns:
            The total energy.
        """
        n = self.params.n_rotors
        theta = y[:n]
        omega = y[n:]
        
        kinetic = 0.5 * np.sum(omega**2)
        
        theta_plus = np.roll(theta, -1)
        # Potential term: J * sum(1 - cos(theta_i - theta_{i+1}))
        # With J > 0, this has a minimum (0) at alignment (theta_i = theta_{i+1})
        potential = self.params.j_coupling * np.sum(1 - np.cos(theta - theta_plus))
        
        # Field term: -M * sum(cos(theta_i))
        field = -self.params.m_field * np.sum(np.cos(theta))
        
        return kinetic + potential + field

    def simulate(self, y0: np.ndarray, t_span: Tuple[float, float], t_eval: np.ndarray = None) -> np.ndarray:
        """
        Run the simulation.
        
        Args:
            y0: Initial state vector.
            t_span: Time interval (t_start, t_end).
            t_eval: Times at which to store the computed solution.
            
        Returns:
            The solution object from solve_ivp.
        """
        sol = solve_ivp(
            self.equations_of_motion,
            t_span,
            y0,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-8,
            atol=1e-10
        )
        return sol
