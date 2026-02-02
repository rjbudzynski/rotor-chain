<script lang="ts">
  let { omegaSq } = $props<{
    omegaSq: Float64Array;
  }>();

  let canvas = $state<HTMLCanvasElement>();

  function getColor(val: number, max: number) {
    const normalized = Math.min(1, val / (max || 1));
    const r = Math.min(255, normalized * 512);
    const g = Math.min(255, Math.max(0, normalized * 512 - 255));
    const b = Math.min(255, Math.max(0, normalized * 512 - 510));
    return `rgb(${r},${g},${b})`;
  }

  $effect(() => {
    if (canvas && omegaSq) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        const n = omegaSq.length;
        const w = canvas.width;
        const h = canvas.height;
        const rw = w / n;
        
        let maxKe = 0;
        for (let i = 0; i < n; i++) if (omegaSq[i] > maxKe) maxKe = omegaSq[i];

        ctx.clearRect(0, 0, w, h);
        for (let i = 0; i < n; i++) {
          ctx.fillStyle = getColor(omegaSq[i], maxKe);
          ctx.fillRect(i * rw, 0, rw, h);
        }
      }
    }
  });
</script>

<canvas bind:this={canvas} width="248" height="40"></canvas>

<style>
  canvas {
    background: #000;
    width: 100%;
  }
</style>