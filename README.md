# Rotor Chain Simulation

An interactive simulation of a Hamiltonian dynamical system consisting of $N$ coupled planar rotors in a uniform external field.

## Physical Model

The system is a linear chain of $N$ rotors with periodic boundary conditions ($\theta_{N+1} \equiv \theta_1$). The dynamics are governed by the Hamiltonian:

$$H = \frac{1}{2}\sum_{i=1}^N \omega_i^2 + J\sum_{i=1}^N (1 - \cos(\theta_i - \theta_{i+1})) - M\sum_{i=1}^N \cos \theta_i$$

Where:
- $\theta_i$ is the angle of the $i$-th rotor.
- $\omega_i$ is the angular momentum (velocity).
- $J$ is the nearest-neighbor coupling constant.
- $M$ is the strength of the uniform external field.

The equations of motion are derived as:
- $\dot{\theta}_i = \omega_i$
- $\dot{\omega}_i = -J(\sin(\theta_i - \theta_{i+1}) + \sin(\theta_i - \theta_{i-1})) - M\sin \theta_i$

## Implementation

- **Core**: Python 3.13 with NumPy for numerical operations and a custom **Velocity Verlet** symplectic integrator for energy-conserving dynamics.
    - Uses sub-stepping (default 10x) per UI frame to maintain stability at high coupling strengths.
- **Visualization**: Pyqtgraph-based display representing rotors as compass needles on a circular chain.
    - Features a real-time mean direction (order parameter) indicator with magnitude scaling.
    - Includes a kinetic energy heatmap for real-time energy distribution monitoring.
- **UI**: PyQt6 interface providing:
    - Interactive sliders for $J$ and $M$.
    - Selection of initial condition presets:
        - **Random Angles**: High entropy start.
        - **Twisted**: Topological winding state (adjustable winding $k$).
        - **Domain Wall**: Relaxation from a split configuration.
        - **Single Kick**: Perturbation of a single rotor (adjustable index).
        - **Thermalized**: Random initial velocities (Maxwell-Boltzmann like).
    - Dynamic control of the number of rotors $N$ (optimized for seamless updates).
    - Real-time monitoring of energy per rotor and the order parameter history (10s window).
- **Testing**:
    - Unit tests for physics logic and energy conservation.
    - UI automation tests using `pytest-qt`.
    - Performance stress tests for large $N$.
- **Dependency Management**: Handled by `uv`.
- **Project Tracking**: Managed via `beads`.

## Usage

Ensure you have `uv` installed, then run:

```bash
uv run main.py
```

To run unit tests:

```bash
uv run pytest
```
