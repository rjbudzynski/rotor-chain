<script lang="ts">
  import OrderPlot from './OrderPlot.svelte';
  import Heatmap from './Heatmap.svelte';

  // Constants
  const MIN_ROTORS = 2;
  const MAX_ROTORS = 500;
  const MIN_J = 0;
  const MAX_J = 5;
  const MIN_M = 0;
  const MAX_M = 10;
  const MIN_TIME_SCALE = 0.1;
  const MAX_TIME_SCALE = 5;
  const STEP_J = 0.01;
  const STEP_M = 0.01;
  const STEP_TIME = 0.1;

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
    onReinit,
    onHelp 
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
    onHelp?: () => void;
  }>();

  const presets = ["Random Angles", "Twisted", "Domain Wall", "Single Kick", "Thermalized"];
  
  // Validation state
  let nRotorsError = $state("");
  let kValueError = $state("");

  let kLabel = $derived(selectedPreset === "Twisted" ? "Winding (k):" : (selectedPreset === "Single Kick" ? "Velocity (ω):" : ""));
  
  function validateAndUpdateNRotors(value: string): boolean {
    const parsed = parseInt(value, 10);
    if (isNaN(parsed)) {
      nRotorsError = "Must be a valid number";
      return false;
    }
    if (parsed < MIN_ROTORS || parsed > MAX_ROTORS) {
      nRotorsError = `Must be between ${MIN_ROTORS} and ${MAX_ROTORS}`;
      return false;
    }
    nRotorsError = "";
    n_rotors = parsed;
    return true;
  }
  
  function validateAndUpdateKValue(value: string): boolean {
    const parsed = parseFloat(value);
    if (isNaN(parsed)) {
      kValueError = "Must be a valid number";
      return false;
    }
    kValueError = "";
    kValue = parsed;
    return true;
  }
</script>

<div class="control-panel">
  <div class="header">
    <button class="help-btn" onclick={onHelp} title="Show Help">?</button>
  </div>

  <div class="group">
    <label>
      Number of Rotors (N):
      <input 
        type="number" 
        value={n_rotors} 
        min={MIN_ROTORS}
        max={MAX_ROTORS}
        disabled={running} 
        class:invalid={nRotorsError}
        onchange={(e) => { 
          if (validateAndUpdateNRotors(e.currentTarget.value)) {
            onReinit(); 
          }
        }} 
      />
      {#if nRotorsError}
        <span class="error">{nRotorsError}</span>
      {/if}
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
        <input 
          type="number" 
          value={kValue}
          step={selectedPreset === "Twisted" ? 1 : 0.1} 
          disabled={running} 
          class:invalid={kValueError}
          onchange={(e) => {
            if (validateAndUpdateKValue(e.currentTarget.value)) {
              onReinit();
            }
          }} 
        />
        {#if kValueError}
          <span class="error">{kValueError}</span>
        {/if}
      </label>
    </div>
  {/if}

  <div class="group">
    <label>
      Coupling (J): {j_coupling.toFixed(2)}
      <input type="range" bind:value={j_coupling} min={MIN_J} max={MAX_J} step={STEP_J} />
    </label>
  </div>

  <div class="group">
    <label>
      Field (M): {m_field.toFixed(2)}
      <input type="range" bind:value={m_field} min={MIN_M} max={MAX_M} step={STEP_M} />
    </label>
  </div>

  <div class="group">
    <label>
      Time Scale: {time_scale.toFixed(1)}x
      <input type="range" bind:value={time_scale} min={MIN_TIME_SCALE} max={MAX_TIME_SCALE} step={STEP_TIME} />
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
  .header {
    display: flex;
    justify-content: flex-end;
  }
  .help-btn {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #444;
    color: #fff;
    border: none;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    flex: none;
  }
  .help-btn:hover {
    background: #555;
  }
  .group label {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    font-size: 0.85rem;
  }
  
  input.invalid {
    border-color: #f44;
    background-color: #422;
  }
  
  span.error {
    color: #f44;
    font-size: 0.75rem;
    margin-top: 0.2rem;
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