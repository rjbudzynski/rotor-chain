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

    def get_acceleration(self, theta: np.ndarray) -> np.ndarray:
        """
        Calculate the acceleration (d_omega/dt) for given angles.
        """
        theta_plus = np.roll(theta, -1)
        theta_minus = np.roll(theta, 1)
        
        accel = (-self.params.j_coupling * (np.sin(theta - theta_plus) + np.sin(theta - theta_minus)) 
                 - self.params.m_field * np.sin(theta))
        return accel

    def equations_of_motion(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Calculate the time derivatives of the state vector.
        
        The equations of motion are derived from the Hamiltonian:
        d_theta_i/dt = omega_i
        d_omega_i/dt = -dH/d_theta_i
        
        For H = 1/2*sum(omega_i^2) + J*sum(1 - cos(theta_i - theta_{i+1})) - M*sum(cos(theta_i)):
        d_omega_i/dt = -J * (sin(theta_i - theta_{i+1}) + sin(theta_i - theta_{i-1})) - M * sin(theta_i)
        
        Args:
            t: Current time.
            y: State vector [theta_0, ..., theta_{n-1}, omega_0, ..., omega_{n-1}].
            
        Returns:
            Derivatives [d_theta_0, ..., d_omega_{n-1}].
        """
        n = self.params.n_rotors
        theta = y[:n]
        omega = y[n:]
        
        d_theta = omega
        d_omega = self.get_acceleration(theta)
        
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
        Run the simulation using solve_ivp (RK45).
        
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

class OrderParameter(NamedTuple):
    """Result of the phase order parameter calculation."""
    r: float
    mean_cos: float
    mean_sin: float

class SimulationEngine:
    """
    Manages the physical state and integration of the rotor chain simulation.
    """
    
    def __init__(self, params: SimulationParams):
        self.params = params
        self.chain = RotorChain(params)
        self.y = np.zeros(2 * params.n_rotors)
        self.t = 0.0
        # Sub-stepping parameters
        self.substeps = 10
        
    def set_state(self, y: np.ndarray, t: float = 0.0):
        """Set the current state of the simulation."""
        self.y = y.copy()
        self.t = t
        
    def update_params(self, j: float = None, m: float = None):
        """Update simulation parameters without resetting the state."""
        n = self.params.n_rotors
        j = j if j is not None else self.params.j_coupling
        m = m if m is not None else self.params.m_field
        self.params = SimulationParams(n_rotors=n, j_coupling=j, m_field=m)
        self.chain.params = self.params

    def verlet_step(self, dt: float):
        """
        Perform a single Velocity Verlet step.
        """
        n = self.params.n_rotors
        theta = self.y[:n]
        omega = self.y[n:]
        
        # 1. v(t + dt/2) = v(t) + a(t) * dt/2
        accel_t = self.chain.get_acceleration(theta)
        omega_mid = omega + accel_t * (dt / 2.0)
        
        # 2. x(t + dt) = x(t) + v(t + dt/2) * dt
        theta_new = theta + omega_mid * dt
        
        # 3. v(t + dt) = v(t + dt/2) + a(t + dt) * dt/2
        accel_new = self.chain.get_acceleration(theta_new)
        omega_new = omega_mid + accel_new * (dt / 2.0)
        
        self.y[:n] = theta_new
        self.y[n:] = omega_new
        self.t += dt

    def step(self, dt: float) -> bool:
        """Advance the simulation by dt using sub-stepping with Verlet."""
        sub_dt = dt / self.substeps
        for _ in range(self.substeps):
            self.verlet_step(sub_dt)
        return True

    @property
    def theta(self) -> np.ndarray:
        return self.y[:self.params.n_rotors]

    @property
    def omega(self) -> np.ndarray:
        return self.y[self.params.n_rotors:]
    
    def get_energy(self) -> float:
        """Calculate total energy of the current state."""
        return self.chain.hamiltonian(self.y)
    
    def get_order_parameter(self) -> OrderParameter:
        """Calculate the phase order parameter r and its components."""
        theta = self.theta
        mean_cos = np.mean(np.cos(theta))
        mean_sin = np.mean(np.sin(theta))
        r = np.sqrt(mean_cos**2 + mean_sin**2)
        return OrderParameter(r, mean_cos, mean_sin)

