<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  let { n_rotors, theta, r, meanCos, meanSin } = $props<{
    n_rotors: number;
    theta: Float64Array;
    r: number;
    meanCos: number;
    meanSin: number;
  }>();

  let canvas = $state<HTMLCanvasElement>();
  let container = $state<HTMLDivElement>();
  let ctx = $state<CanvasRenderingContext2D | null>(null);

  let width = $state(0);
  let height = $state(0);

  let size = $derived(Math.min(width, height));
  let R_CIRCLE = $derived(size * 0.4);
  let MEAN_MAX_RADIUS = $derived(R_CIRCLE * 0.5);
  
  const ROTATION_OFFSET = Math.PI / 2;

  let needleLength = $derived(Math.min(size * 0.1, (Math.PI * R_CIRCLE) / n_rotors));
  let phiInternal = $derived(Array.from({ length: n_rotors }, (_, i) => (2 * Math.PI * i) / n_rotors));
  let phiPlot = $derived(phiInternal.map(p => p + ROTATION_OFFSET));

  let resizeObserver: ResizeObserver;

  onMount(() => {
    if (canvas) {
      ctx = canvas.getContext('2d');
    }
    
    if (container) {
      resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
          width = entry.contentRect.width;
          height = entry.contentRect.height;
        }
      });
      resizeObserver.observe(container);
    }
  });

  onDestroy(() => {
    if (resizeObserver) resizeObserver.disconnect();
  });

  function draw() {
    if (!ctx || !canvas || size <= 0) return;

    const centerX = width / 2;
    const centerY = height / 2;

    ctx.clearRect(0, 0, width, height);
    ctx.save();
    ctx.translate(centerX, centerY);

    // 1. Reference Circles
    ctx.strokeStyle = '#505050';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(0, 0, R_CIRCLE, 0, 2 * Math.PI);
    ctx.stroke();

    // Concentric circles for mean orientation
    ctx.strokeStyle = '#3c3c00';
    [0.25, 0.5, 0.75].forEach(factor => {
      ctx.beginPath();
      ctx.arc(0, 0, MEAN_MAX_RADIUS * factor, 0, 2 * Math.PI);
      ctx.stroke();
    });

    ctx.strokeStyle = '#969600';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(0, 0, MEAN_MAX_RADIUS, 0, 2 * Math.PI);
    ctx.stroke();

    // 2. Rotor Needles
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = Math.max(1, Math.min(3, (size * 0.15) / n_rotors));
    const tipSize = Math.max(1, Math.min(6, (size * 0.25) / n_rotors));

    // Guard against out-of-sync theta length
    const count = Math.min(n_rotors, theta.length);
    for (let i = 0; i < count; i++) {
      const p = phiPlot[i];
      const angle = p + theta[i];
      
      const cx = R_CIRCLE * Math.cos(p);
      const cy = R_CIRCLE * Math.sin(p);

      const dx = (needleLength / 2) * Math.cos(angle);
      const dy = (needleLength / 2) * Math.sin(angle);

      ctx.beginPath();
      ctx.moveTo(cx - dx, cy - dy);
      ctx.lineTo(cx + dx, cy + dy);
      ctx.stroke();

      ctx.fillStyle = '#ff0000';
      ctx.beginPath();
      ctx.arc(cx + dx, cy + dy, tipSize, 0, 2 * Math.PI);
      ctx.fill();
    }

    // 3. Mean Direction
    const meanTheta = Math.atan2(meanSin, meanCos);
    const visualMeanAngle = meanTheta + ROTATION_OFFSET;
    const mLen = MEAN_MAX_RADIUS * r;
    const mxEnd = mLen * Math.cos(visualMeanAngle);
    const myEnd = mLen * Math.sin(visualMeanAngle);

    ctx.strokeStyle = '#ffff00';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(mxEnd, myEnd);
    ctx.stroke();

    drawArrowhead(ctx, mxEnd, myEnd, visualMeanAngle);

    ctx.restore();
  }

  function drawArrowhead(ctx: CanvasRenderingContext2D, x: number, y: number, angle: number) {
    const headlen = Math.max(5, size * 0.02);
    ctx.fillStyle = '#ffff00';
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x - headlen * Math.cos(angle - Math.PI / 6), y - headlen * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(x - headlen * Math.cos(angle + Math.PI / 6), y - headlen * Math.sin(angle + Math.PI / 6));
    ctx.closePath();
    ctx.fill();
  }

  $effect(() => {
    // Explicitly track dependencies
    theta; n_rotors; r; meanCos; meanSin; width; height; ctx;
    draw();
  });
</script>

<div class="visualizer-container" bind:this={container}>
  <canvas
    bind:this={canvas}
    {width}
    {height}
    class="visualizer-canvas"
  ></canvas>
</div>

<style>
  .visualizer-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }
  .visualizer-canvas {
    background-color: #000;
    display: block;
  }
</style>