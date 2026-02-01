<script lang="ts">
  import OrderPlot from './OrderPlot.svelte';
  import Heatmap from './Heatmap.svelte';

  export let n_rotors: number;
  export let j_coupling: number;
  export let m_field: number;
  export let time_scale: number;
  export let running: boolean;
  export let energyPerRotor: number;
  export let orderHistory: [number[], number[]];
  export let omegaSq: Float64Array;
  export let selectedPreset: string;
  export let kValue: number;

  export let onToggle: () => void;
  export let onReset: () => void;
  export let onReinit: () => void;

  const presets = ["Random Angles", "Twisted", "Domain Wall", "Single Kick", "Thermalized"];

  $: kLabel = selectedPreset === "Twisted" ? "Winding (k):" : (selectedPreset === "Single Kick" ? "Velocity (ω):" : "");
</script>

<div class="control-panel">
  <div class="group">
    <label>
      Number of Rotors (N):
      <input type="number" bind:value={n_rotors} min="2" max="500" disabled={running} on:change={onReinit} />
    </label>
  </div>

  <div class="group">
    <label>
      Initial Condition Preset:
      <select bind:value={selectedPreset} disabled={running} on:change={onReinit}>
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
        <input type="number" bind:value={kValue} step={selectedPreset === "Twisted" ? 1 : 0.1} disabled={running} on:change={onReinit} />
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
    <button on:click={onToggle} class:running>{running ? 'Stop' : 'Start'}</button>
    <button on:click={onReset}>Reset</button>
  </div>

  <div class="stats">
    <p>Energy per Rotor: {energyPerRotor.toFixed(4)}</p>
  </div>

  <div class="plots">
    <span>Order Parameter (r):</span>
    <OrderPlot data={orderHistory} />
    
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
