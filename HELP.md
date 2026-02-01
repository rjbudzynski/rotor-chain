# Rotor Chain Simulation - Help

This application simulates a linear chain of coupled planar rotors subjected to a uniform external field.

## Physics Overview

The system consists of $N$ rotors arranged in a circle. Each rotor interacts with its two nearest neighbors via a coupling constant $J$ and responds to an external field $M$.

- **Coupling (J)**: Determines how strongly rotors want to align with their neighbors.
- **Field (M)**: Determines how strongly rotors want to align with the vertical downward direction.
- **Order Parameter (r)**: Measures the synchronization of the system. A value of 1.0 means all rotors are perfectly aligned.

## Controls

### Simulation Parameters
- **Number of Rotors (N)**: Adjust the total number of rotors. (Changeable only when paused).
- **Initial Condition Preset**: Choose a starting configuration:
    - **Random Angles**: High entropy start.
    - **Twisted**: Creates a topological winding state. Use **Winding (k)** to set the number of full rotations.
    - **Domain Wall**: Split configuration to observe relaxation.
    - **Single Kick**: One rotor is given an initial velocity. Use **Velocity (\u03c9)** to set the magnitude.
    - **Thermalized**: Random velocities (Maxwell-Boltzmann like) assigned to rotors at zero angle.
- **Coupling (J)**: Real-time slider for neighbor interaction strength.
- **Field (M)**: Real-time slider for external field strength.

### Controls & Monitors
- **Start/Stop**: Runs or pauses the integration.
- **Reset**: Restores initial conditions and stops the timer.
- **Energy per Rotor**: Monitors numerical stability. In a closed system ($M=0$ or constant parameters), this should be conserved.
- **Order Parameter Plot**: Shows the history of system synchronization over the last 10 seconds.
- **Kinetic Energy Heatmap**: A real-time visualization of the energy distribution across the chain. Each rectangle represents a rotor, colored by its speed squared.

## Visualization
- **White Needles**: Individual rotors.
- **Red Dots**: Indicate the "north pole" or orientation of each rotor.
- **Yellow Arrow**: Points in the mean direction of the system; its length represents the synchronization level (r).
- **Grey Circle**: Path of the rotor centers.
- **Yellow Circle**: Reference for maximum synchronization (r=1).
- **Heatmap strip**: Brighter colors (using the 'inferno' scale) indicate higher kinetic energy for that specific rotor.
