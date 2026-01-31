**Simulation of a chain of coupled planar rotors**

# Goal:

create a visual and interactive simulation of a Hamiltonian dynamical system
consisting of $N$ planar rotors interacting via nearest neighbor couplings and
subject to a constant uniform external field. The rotors will be arranged in 
a linear chain with periodic boundary conditions, that is: the nearest neighbors 
of rotor $i$ are rotor $(i + 1) mod N$ and rotor $(i - 1) mod N$. The Hamiltonian
will be given by

$$
H = 1/2\sum_{i} \omega_i^2 - J\sum_{<ij>}(1 - \cos(\theta_i - \theta_j)) - M\sum_i \theta_i
$$

where the sum over $<ij>$ is over all nearest neighbor pairs (no double counting),
$\theta_i$ is the angle of the $i$-th rotor ($i = 0, \ldots N$), and $\omega_i$
is the momentum conjugate to $\theta_i$.

Use a quality numerical integrator to approximately solve the equations of motion.
For the prototype implementation use the initial conditions such that 
$\theta_0 = \pi - 0.01$ and the remaining angles and all momenta set to zero--this
will be generalized later, once the basic algorithm is proved to work.

# Implementation

This will be a prototype implemented in Python using NumPy and SciPy for computation,
and Pyqtgraph for visualization. 

Visualize the rotors as spinning "compass needles" arranged on a circle circumference.

# Tools

* Use `uv` for dependency management.
* Use _beads_ (`bd`) for planning and work tracking. Refer to the output of `bd prime` for further guidance.
* Set up a local git repository. Work on its _main_ branch.

# Workflow

* Create an implementation plan.
* Flesh it out as specific steps described by beads issues.
* Use issue dependency (`bd dep --help`) and issue descriptions to structure the plan.
* Pause for interactive verification by user as soon as there is a testable deliverable,
  not necessarily feature complete.
* Create and use unit tests for essential functionalities.

# Standards

* Use all modern python features as of version 3.13.
* Write well-organized, modular code with short, focused functions/methods.
* Type-annotate the code where it matters--where type inference won't suffice.
* Attach docstring to all public objects.
