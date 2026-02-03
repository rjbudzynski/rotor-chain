<script lang="ts">
  import { onMount, onDestroy, untrack } from 'svelte';
  import { SimulationEngine } from './physics/SimulationEngine';
  import Visualizer from './components/Visualizer.svelte';
  import ControlPanel from './components/ControlPanel.svelte';

  // UI state
  let n_rotors = $state(50);
  let j_coupling = $state(1.0);
  let m_field = $state(0.0);
  let time_scale = $state(1.0);
  let running = $state(false);
  let selectedPreset = $state("Random Angles");
  let kValue = $state(1.0);

  // Simulation engine
  const engine = new SimulationEngine({ n_rotors: 50, j_coupling: 1.0, m_field: 0.0 });
  
  // Tracked state
  let theta = $state(engine.y.subarray(0, 50));
  let omegaSq = $state(engine.getKineticEnergies());
  let r = $state(0);
  let meanCos = $state(1);
  let meanSin = $state(0);
  let energyPerRotor = $state(0);
  let xRange = $state<[number, number]>([0, 10]);

  let frameId: number;
  const DT = 0.02;
  const HISTORY_CAPACITY = 600; // 10 seconds at 60 FPS

  // Circular buffer for order history to reduce GC pressure
  const timesBuffer = new Float64Array(HISTORY_CAPACITY);
  const valuesBuffer = new Float64Array(HISTORY_CAPACITY);
  let bufferHead = 0;
  let bufferCount = 0;
  let orderHistory = $state<[number[], number[]]>([[], []]);

  function getOrderHistory(): [number[], number[]] {
    const times: number[] = new Array(bufferCount);
    const values: number[] = new Array(bufferCount);
    for (let i = 0; i < bufferCount; i++) {
      const idx = (bufferHead - bufferCount + i + HISTORY_CAPACITY) % HISTORY_CAPACITY;
      times[i] = timesBuffer[idx];
      values[i] = valuesBuffer[idx];
    }
    return [times, values];
  }

  function initSimulation() {
    engine.setParams({ n_rotors, j_coupling, m_field });
    
    const initialTheta = new Float64Array(n_rotors);
    const initialOmega = new Float64Array(n_rotors);

    if (selectedPreset === "Random Angles") {
      for (let i = 0; i < n_rotors; i++) initialTheta[i] = (Math.random() * 2 - 1) * Math.PI;
    } else if (selectedPreset === "Twisted") {
      for (let i = 0; i < n_rotors; i++) initialTheta[i] = (2 * Math.PI * kValue * i) / n_rotors;
    } else if (selectedPreset === "Domain Wall") {
      const half = Math.floor(n_rotors / 2);
      for (let i = 0; i < n_rotors; i++) initialTheta[i] = i < half ? 0 : Math.PI;
      initialOmega[0] = 1e-6; // perturbation
    } else if (selectedPreset === "Single Kick") {
      initialOmega[0] = kValue;
    } else if (selectedPreset === "Thermalized") {
      for (let i = 0; i < n_rotors; i++) {
        const u1 = Math.random();
        const u2 = Math.random();
        initialOmega[i] = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
      }
    }

    engine.setState(initialTheta, initialOmega);
    engine.t = 0;
    updateStateVars();
    bufferHead = 0;
    bufferCount = 0;
    orderHistory = [[], []];
    xRange = [0, 10];
  }

  function updateStateVars() {
    // Re-assign to trigger reactivity
    theta = engine.y.subarray(0, engine.params.n_rotors);
    omegaSq = engine.getKineticEnergies();
    
    const op = engine.getOrderParameter();
    r = op.r;
    meanCos = op.meanCos;
    meanSin = op.meanSin;
    energyPerRotor = engine.getEnergy() / engine.params.n_rotors;
  }

  function toggleSimulation() {
    running = !running;
    if (running) {
      loop();
    } else {
      cancelAnimationFrame(frameId);
    }
  }

  function resetSimulation() {
    running = false;
    cancelAnimationFrame(frameId);
    initSimulation();
  }

  function loop() {
    if (!running) return;
    
    engine.setParams({ j_coupling, m_field });
    engine.substeps = Math.ceil(10 * time_scale);
    engine.step(DT * time_scale);
    updateStateVars();
    
    // Add to circular buffer
    timesBuffer[bufferHead] = engine.t;
    valuesBuffer[bufferHead] = r;
    bufferHead = (bufferHead + 1) % HISTORY_CAPACITY;
    if (bufferCount < HISTORY_CAPACITY) {
      bufferCount++;
    }

    // Remove old data (older than 10 seconds)
    while (bufferCount > 0 && timesBuffer[(bufferHead - bufferCount + HISTORY_CAPACITY) % HISTORY_CAPACITY] < engine.t - 10) {
      bufferCount--;
    }

    orderHistory = getOrderHistory();

    if (engine.t > 10) {
      xRange = [engine.t - 10, engine.t];
    } else {
      xRange = [0, 10];
    }

    frameId = requestAnimationFrame(loop);
  }

  onMount(() => {
    initSimulation();
  });

  onDestroy(() => {
    cancelAnimationFrame(frameId);
  });
</script>

<main>
  <div class="container">
    <div class="viz-container">
      <Visualizer {n_rotors} {theta} {r} {meanCos} {meanSin} />
    </div>
    <ControlPanel
      bind:n_rotors
      bind:j_coupling
      bind:m_field
      bind:time_scale
      bind:selectedPreset
      bind:kValue
      {running}
      {energyPerRotor}
      {orderHistory}
      {xRange}
      {omegaSq}
      onToggle={toggleSimulation}
      onReset={resetSimulation}
      onReinit={initSimulation}
    />
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    background: #111;
    overflow: hidden;
  }
  .container {
    display: flex;
    height: 100vh;
  }
  .viz-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #000;
    min-width: 0;
    min-height: 0;
  }
</style>
