<script lang="ts">
  import OrderPlot from './OrderPlot.svelte';
  import Heatmap from './Heatmap.svelte';

  let { 
    n_rotors = $bindable(), 
    j_coupling = $bindable(), 
    m_field = $bindable(), 
    time_scale = $bindable(), 
    selectedPreset = $bindable(), 
    kValue = $bindable(),
    running, 
    energyPerRotor, 
    orderHistory, 
    xRange, 
    omegaSq, 
    onToggle, 
    onReset, 
    onReinit 
  } = $props<{
    n_rotors: number;
    j_coupling: number;
    m_field: number;
    time_scale: number;
    selectedPreset: string;
    kValue: number;
    running: boolean;
    energyPerRotor: number;
    orderHistory: [number[], number[]];
    xRange: [number, number];
    omegaSq: Float64Array;
    onToggle: () => void;
    onReset: () => void;
    onReinit: () => void;
  }>();

  const presets = ["Random Angles", "Twisted", "Domain Wall", "Single Kick", "Thermalized"];

  let kLabel = $derived(selectedPreset === "Twisted" ? "Winding (k):" : (selectedPreset === "Single Kick" ? "Velocity (ω):" : ""));
</script>

<div class="control-panel">
  <div class="group">
    <label>
      Number of Rotors (N):
      <input 
        type="number" 
        value={n_rotors} 
        min="2" 
        max="500" 
        disabled={running} 
        onchange={(e) => { n_rotors = parseInt(e.currentTarget.value); onReinit(); }} 
      />
    </label>
  </div>

  <div class="group">
    <label>
      Initial Condition Preset:
      <select bind:value={selectedPreset} disabled={running} onchange={onReinit}>
        {#each presets as preset}
          <option value={preset}>{preset}</option>
        {/each}
      </select>
    </label>
  </div>

  {#if kLabel}
    <div class="group">
      <label>
        {kLabel}
        <input type="number" bind:value={kValue} step={selectedPreset === "Twisted" ? 1 : 0.1} disabled={running} onchange={onReinit} />
      </label>
    </div>
  {/if}

  <div class="group">
    <label>
      Coupling (J): {j_coupling.toFixed(2)}
      <input type="range" bind:value={j_coupling} min="0" max="5" step="0.01" />
    </label>
  </div>

  <div class="group">
    <label>
      Field (M): {m_field.toFixed(2)}
      <input type="range" bind:value={m_field} min="0" max="10" step="0.01" />
    </label>
  </div>

  <div class="group">
    <label>
      Time Scale: {time_scale.toFixed(1)}x
      <input type="range" bind:value={time_scale} min="0.1" max="5" step="0.1" />
    </label>
  </div>

  <div class="actions">
    <button onclick={onToggle} class:running>{running ? 'Stop' : 'Start'}</button>
    <button onclick={onReset}>Reset</button>
  </div>

  <div class="stats">
    <p>Energy per Rotor: {energyPerRotor.toFixed(4)}</p>
  </div>

  <div class="plots">
    <span>Order Parameter (r):</span>
    <OrderPlot data={orderHistory} {xRange} />
    
    <span>Kinetic Energy Heatmap:</span>
    <Heatmap {omegaSq} />
  </div>
</div>

<style>
  .control-panel {
    width: 280px;
    padding: 1rem;
    background: #222;
    color: #eee;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    height: 100vh;
    overflow-y: auto;
    box-sizing: border-box;
  }
  .group label {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    font-size: 0.85rem;
  }
  input[type="range"] {
    width: 100%;
  }
  .actions {
    display: flex;
    gap: 0.5rem;
  }
  button {
    flex: 1;
    padding: 0.5rem;
    cursor: pointer;
    background: #444;
    color: white;
    border: none;
    border-radius: 4px;
  }
  button.running {
    background: #a44;
  }
  .stats p {
    font-family: monospace;
    font-size: 0.9rem;
    margin: 0;
  }
  .plots {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  .plots span {
    font-size: 0.85rem;
  }
</style>