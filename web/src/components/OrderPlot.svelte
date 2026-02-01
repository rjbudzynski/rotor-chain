<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import uPlot from 'uplot';
  import 'uplot/dist/uPlot.min.css';

  export let data: [number[], number[]]; // [times, values]

  let container: HTMLDivElement;
  let chart: uPlot;

  onMount(() => {
    const opts: uPlot.Options = {
      width: 250,
      height: 150,
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
        { grid: { show: true, stroke: "#333" } },
        { grid: { show: true, stroke: "#333" } }
      ]
    };

    chart = new uPlot(opts, data, container);
  });

  onDestroy(() => {
    if (chart) chart.destroy();
  });

  $: if (chart && data) {
    chart.setData(data);
  }
</script>

<div bind:this={container}></div>

<style>
  div {
    background: black;
  }
</style>
