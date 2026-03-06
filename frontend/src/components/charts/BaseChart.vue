<template>
  <div ref="chartRef" class="chart" />
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from "vue";
import * as echarts from "echarts/core";
import { LineChart, BarChart, PieChart, LinesChart, EffectScatterChart } from "echarts/charts";
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent, GeoComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  GeoComponent,
  LineChart,
  BarChart,
  PieChart,
  LinesChart,
  EffectScatterChart,
  CanvasRenderer
]);

type EChartsOption = echarts.EChartsOption;

const props = defineProps<{
  option: EChartsOption;
}>();

const chartRef = ref<HTMLDivElement>();
let instance: echarts.ECharts | null = null;

function initChart() {
  if (!chartRef.value) {
    return;
  }
  instance = echarts.init(chartRef.value);
  instance.setOption(props.option);
}

function disposeChart() {
  if (instance) {
    instance.dispose();
    instance = null;
  }
}

onMounted(() => {
  initChart();
  window.addEventListener("resize", resizeChart);
});

onBeforeUnmount(() => {
  disposeChart();
  window.removeEventListener("resize", resizeChart);
});

function resizeChart() {
  instance?.resize();
}

watch(
  () => props.option,
  (option) => {
    if (!instance) {
      initChart();
    } else {
      instance.setOption(option, true);
    }
  },
  { deep: true }
);
</script>

<style scoped>
.chart {
  width: 100%;
  height: 320px;
}
</style>
