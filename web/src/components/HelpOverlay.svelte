<script lang="ts">
  let { isOpen = $bindable(), onClose }: { isOpen: boolean; onClose: () => void } = $props();
</script>

{#if isOpen}
  <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
  <div 
    class="overlay-backdrop" 
    role="button" 
    tabindex="0" 
    aria-label="Close help"
    onclick={onClose}
    onkeydown={(e) => e.key === 'Enter' && onClose()}
  >
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div 
      class="overlay-content" 
      tabindex="-1"
      onclick={(e) => e.stopPropagation()}
    >
      <div class="overlay-header">
        <h2 id="help-title">Rotor Chain Simulation - Help</h2>
        <button class="close-btn" onclick={onClose}>×</button>
      </div>
      <div class="overlay-body">
        <section>
          <h3>Physics Overview</h3>
          <p>
            The system consists of <em>N</em> rotors arranged in a circle. Each rotor interacts 
            with its two nearest neighbors via a coupling constant <em>J</em> and responds to an 
            external field <em>M</em>.
          </p>
          <ul>
            <li><strong>Coupling (J)</strong>: Determines how strongly rotors want to align with their neighbors.</li>
            <li><strong>Field (M)</strong>: Determines how strongly rotors want to align with the vertical downward direction.</li>
            <li><strong>Order Parameter (r)</strong>: Measures the synchronization of the system. A value of 1.0 means all rotors are perfectly aligned.</li>
          </ul>
        </section>

        <section>
          <h3>Controls</h3>
          
          <h4>Simulation Parameters</h4>
          <ul>
            <li>
              <strong>Number of Rotors (N)</strong>: Adjust the total number of rotors. 
              (Changeable only when paused).
            </li>
            <li>
              <strong>Initial Condition Preset</strong>: Choose a starting configuration:
              <ul>
                <li><strong>Random Angles</strong>: High entropy start.</li>
                <li><strong>Twisted</strong>: Creates a topological winding state. Use <strong>Winding (k)</strong> to set the number of full rotations.</li>
                <li><strong>Domain Wall</strong>: Split configuration to observe relaxation.</li>
                <li><strong>Single Kick</strong>: One rotor is given an initial velocity. Use <strong>Velocity (ω)</strong> to set the magnitude.</li>
                <li><strong>Thermalized</strong>: Random velocities (Maxwell-Boltzmann like) assigned to rotors at zero angle.</li>
              </ul>
            </li>
            <li><strong>Coupling (J)</strong>: Real-time slider for neighbor interaction strength.</li>
            <li><strong>Field (M)</strong>: Real-time slider for external field strength.</li>
          </ul>

          <h4>Controls & Monitors</h4>
          <ul>
            <li><strong>Start/Stop</strong>: Runs or pauses the integration.</li>
            <li><strong>Reset</strong>: Restores initial conditions and stops the timer.</li>
            <li><strong>Energy per Rotor</strong>: Monitors numerical stability. In a closed system (<em>M=0</em> or constant parameters), this should be conserved.</li>
            <li><strong>Order Parameter Plot</strong>: Shows the history of system synchronization over the last 10 seconds.</li>
            <li><strong>Kinetic Energy Heatmap</strong>: A real-time visualization of the energy distribution across the chain. Each rectangle represents a rotor, colored by its speed squared.</li>
          </ul>
        </section>

        <section>
          <h3>Visualization</h3>
          <ul>
            <li><strong>White Needles</strong>: Individual rotors.</li>
            <li><strong>Red Dots</strong>: Indicate the "north pole" or orientation of each rotor.</li>
            <li><strong>Yellow Arrow</strong>: Points in the mean direction of the system; its length represents the synchronization level (r).</li>
            <li><strong>Grey Circle</strong>: Path of the rotor centers.</li>
            <li><strong>Yellow Circle</strong>: Reference for maximum synchronization (r=1).</li>
            <li><strong>Heatmap strip</strong>: Brighter colors (using the 'inferno' scale) indicate higher kinetic energy for that specific rotor.</li>
          </ul>
        </section>
      </div>
    </div>
  </div>
{/if}

<style>
  .overlay-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .overlay-content {
    background: #1a1a1a;
    color: #eee;
    border-radius: 8px;
    max-width: 700px;
    max-height: 85vh;
    width: 90%;
    display: flex;
    flex-direction: column;
    border: 1px solid #444;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  }

  .overlay-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #444;
  }

  .overlay-header h2 {
    margin: 0;
    font-size: 1.25rem;
    color: #fff;
  }

  .close-btn {
    background: none;
    border: none;
    color: #888;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0 0.25rem;
    line-height: 1;
  }

  .close-btn:hover {
    color: #fff;
  }

  .overlay-body {
    padding: 1.5rem;
    overflow-y: auto;
    font-size: 0.9rem;
    line-height: 1.6;
  }

  section {
    margin-bottom: 1.5rem;
  }

  section:last-child {
    margin-bottom: 0;
  }

  h3 {
    color: #4af;
    margin: 0 0 0.75rem 0;
    font-size: 1.1rem;
    border-bottom: 1px solid #333;
    padding-bottom: 0.25rem;
  }

  h4 {
    color: #8af;
    margin: 1rem 0 0.5rem 0;
    font-size: 1rem;
  }

  p {
    margin: 0.5rem 0;
  }

  ul {
    margin: 0.5rem 0;
    padding-left: 1.25rem;
  }

  li {
    margin: 0.25rem 0;
  }

  li ul {
    margin-top: 0.25rem;
  }

  strong {
    color: #ddd;
  }

  em {
    font-style: italic;
    color: #aaa;
  }
</style>
