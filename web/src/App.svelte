<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { SimulationEngine } from './physics/SimulationEngine';
  import Visualizer from './components/Visualizer.svelte';
  import ControlPanel from './components/ControlPanel.svelte';

  let n_rotors = 50;
  let j_coupling = 1.0;
  let m_field = 0.0;
  let time_scale = 1.0;
  let running = false;
  let selectedPreset = "Random Angles";
  let kValue = 1.0;

  let engine = new SimulationEngine({ n_rotors, j_coupling, m_field });
  let theta = engine.y.subarray(0, n_rotors);
  let omegaSq = engine.getKineticEnergies();
  let r = 0;
  let meanCos = 1;
  let meanSin = 0;
  let energyPerRotor = 0;
  let orderHistory: [number[], number[]] = [[], []];

  let frameId: number;
  const DT = 0.02;

  function initSimulation() {
    engine.setParams({ n_rotors, j_coupling, m_field });
    theta = engine.y.subarray(0, n_rotors);
    
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
        // Box-Muller for normal distribution
        const u1 = Math.random();
        const u2 = Math.random();
        initialOmega[i] = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
      }
    }

    engine.setState(initialTheta, initialOmega);
    updateStateVars();
    orderHistory = [[], []];
  }

  function updateStateVars() {
    theta = engine.y.subarray(0, n_rotors);
    omegaSq = engine.getKineticEnergies();
    const op = engine.getOrderParameter();
    r = op.r;
    meanCos = op.meanCos;
    meanSin = op.meanSin;
    energyPerRotor = engine.getEnergy() / n_rotors;
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
    
    // Update history
    const newTimes = [...orderHistory[0], engine.t];
    const newValues = [...orderHistory[1], r];
    
    // Prune to 10s window
    while (newTimes.length > 0 && newTimes[0] < engine.t - 10) {
      newTimes.shift();
      newValues.shift();
    }
    orderHistory = [newTimes, newValues];

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
  }
</style>