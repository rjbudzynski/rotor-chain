<script lang="ts">
  import { onMount } from 'svelte';

  export let n_rotors: number;
  export let theta: Float64Array;
  export let r: number;
  export let meanCos: number;
  export let meanSin: number;

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null = null;

  const R_CIRCLE = 100; // Visual radius
  const ROTATION_OFFSET = -Math.PI / 2;
  const MEAN_MAX_RADIUS = 50;
  const PADDING = 40;

  $: needleLength = Math.min(35, (Math.PI * R_CIRCLE) / n_rotors);
  $: phiInternal = Array.from({ length: n_rotors }, (_, i) => (2 * Math.PI * i) / n_rotors);
  $: phiPlot = phiInternal.map(p => p + ROTATION_OFFSET);

  onMount(() => {
    ctx = canvas.getContext('2d');
    draw();
  });

  export function draw() {
    if (!ctx || !canvas) return;

    const width = canvas.width;
    const height = canvas.height;
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
    ctx.lineWidth = Math.max(1, Math.min(3, 100 / n_rotors));
    const tipSize = Math.max(1.5, Math.min(6, 125 / n_rotors));

    for (let i = 0; i < n_rotors; i++) {
      const p = phiPlot[i];
      const angle = p + theta[i];
      
      const cx = R_CIRCLE * Math.cos(p);
      const cy = R_CIRCLE * Math.sin(p);

      const dx = (needleLength / 2) * Math.cos(angle);
      const dy = (needleLength / 2) * Math.sin(angle);

      // Draw needle
      ctx.beginPath();
      ctx.moveTo(cx - dx, cy - dy);
      ctx.lineTo(cx + dx, cy + dy);
      ctx.stroke();

      // Draw tip
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

    // Mean Arrowhead
    drawArrowhead(ctx, mxEnd, myEnd, visualMeanAngle);

    ctx.restore();
  }

  function drawArrowhead(ctx: CanvasRenderingContext2D, x: number, y: number, angle: number) {
    const headlen = 10;
    ctx.fillStyle = '#ffff00';
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x - headlen * Math.cos(angle - Math.PI / 6), y - headlen * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(x - headlen * Math.cos(angle + Math.PI / 6), y - headlen * Math.sin(angle + Math.PI / 6));
    ctx.closePath();
    ctx.fill();
  }

  $: if (theta) {
    draw();
  }
</script>

<canvas
  bind:this={canvas}
  width={2 * R_CIRCLE + 2 * PADDING}
  height={2 * R_CIRCLE + 2 * PADDING}
  class="visualizer-canvas"
></canvas>

<style>
  .visualizer-canvas {
    background-color: #000;
    display: block;
    margin: auto;
  }
</style>
