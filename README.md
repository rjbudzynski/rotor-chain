# Rotor Chain Simulation

An interactive simulation of a Hamiltonian dynamical system consisting of $N$ coupled planar rotors in a uniform external field.

## Physical Model

The system is a linear chain of $N$ rotors with periodic boundary conditions ($\theta_{N+1} \equiv \theta_1$). The dynamics are governed by the Hamiltonian:

$$H = \frac{1}{2}\sum_{i=1}^N \omega_i^2 - J\sum_{i=1}^N (1 - \cos(\theta_i - \theta_{i+1})) - M\sum_{i=1}^N \cos \theta_i$$

Where:
- $\theta_i$ is the angle of the $i$-th rotor.
- $\omega_i$ is the angular momentum (velocity).
- $J$ is the nearest-neighbor coupling constant.
- $M$ is the strength of the uniform external field.

The equations of motion are derived as:
- $\dot{\theta}_i = \omega_i$
- $\dot{\omega}_i = J(\sin(\theta_i - \theta_{i+1}) + \sin(\theta_i - \theta_{i-1})) - M\sin \theta_i$

## Implementation

- **Core**: Python 3.13 with NumPy for numerical operations and SciPy (`solve_ivp` with RK45) for high-quality integration.
- **Visualization**: Pyqtgraph-based display representing rotors as compass needles on a circular chain.
    - Features a real-time mean direction (order parameter) indicator with magnitude scaling.
    - Includes visual aids like reference circles for alignment levels.
- **UI**: PyQt6 interface providing:
    - Interactive sliders for $J$ and $M$.
    - Selection of initial condition presets (Random, Twisted, Domain Wall, Single Kick).
    - Dynamic control of the number of rotors $N$.
    - Real-time monitoring of energy per rotor and the order parameter history (10s window).
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
