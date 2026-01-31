# Gemini Handoff - Rotor Chain Simulation

This document provides a summary of the project state and guidance for future AI agents.

## Project Overview

**Rotor Chain Simulation** is a Python-based interactive tool for simulating a Hamiltonian system of $N$ coupled planar rotors in a uniform external field.

### Core Features
- **High-Fidelity Physics**: Uses SciPy's `solve_ivp` (RK45) to integrate the equations of motion.
- **Interactive UI**: Real-time control over coupling strength ($J$), external field ($M$), and the number of rotors ($N$).
- **Dynamic Visualization**: Visualizes rotors as compass needles on a circular chain with a mean direction (order parameter) indicator.
- **Real-time Monitoring**: Tracks energy per rotor stability and displays a 10-second history of the order parameter.

## Current State

The prototype is substantially complete and functional.
- **Completed**: Core simulation, visual scaling, UI controls, initial condition presets, help dialog, and custom icon.
- **Outstanding**: A placeholder epic `rotor-chain-5uf` exists for future UI enhancements.

## Instructions for Agents

Future agents working on this project **MUST** follow the instructions in [AGENTS.md](./AGENTS.md). 

### Key Commands
- `uv run main.py`: Start the application.
- `uv run pytest`: Run unit tests.
- `bd ready`: Check for available tasks in the Beads tracker.

## Architecture Notes
- `simulation.py`: Contains the `RotorChain` class with physics logic.
- `visualizer.py`: Contains the `RotorVisualizer` class (Pyqtgraph-based).
- `ui.py`: Contains `ControlPanel` and `HelpDialog` classes (PyQt6-based).
- `main.py`: Integrates simulation, UI, and visualization into the `MainWindow`.
- `icon.svg`: The application's visual identity.
