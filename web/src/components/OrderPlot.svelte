<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import uPlot from 'uplot';
  import 'uplot/dist/uPlot.min.css';

  export let data: [number[], number[]]; // [times, values]
  export let xRange: [number, number];

  let container: HTMLDivElement;
  let chart: uPlot;

  onMount(() => {
    const opts: uPlot.Options = {
      width: 250,
      height: 120,
      padding: [8, 12, 0, 0],
      cursor: { show: false },
      legend: { show: false },
      scales: {
        x: { time: false },
        y: { range: [0, 1.05] }
      },
      series: [
        {},
        {
          stroke: "yellow",
          width: 2,
        }
      ],
      axes: [
        { 
          side: 2,
          stroke: "#ccc",
          grid: { show: true, stroke: "#333" },
          font: "10px sans-serif",
          size: 22,
        },
        { 
          side: 3,
          stroke: "#ccc",
          grid: { show: true, stroke: "#333" },
          font: "10px sans-serif",
          size: 30,
          values: (self, ticks) => ticks.map(v => v.toFixed(1)),
          splits: [0, 0.5, 1.0],
        }
      ]
    };

    chart = new uPlot(opts, data, container);
  });

  onDestroy(() => {
    if (chart) chart.destroy();
  });

  $: if (chart && data && xRange) {
    chart.setData(data);
    chart.setScale("x", { min: xRange[0], max: xRange[1] });
  }
</script>

<div bind:this={container}></div>

<style>
  div {
    background: black;
  }
</style>
