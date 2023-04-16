<template>
  <Bar :data="chartData" :style="myStyles" :options="chartOptions" :key="watchKeyChange" />
</template>

<script>
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
);

export default {
  name: "BarChartContainer",
  components: { Bar },
  props: { chartComponentData: { type: Object, required: true }, label: { type: String, required: true } },
  data() {
    return {
      watchKeyChange: 0,
      options: {
        responsive: true,
        scales: {
          y: {
            ticks: {
              beginAtZero: true,
              precision: 0,
            },
            gridLines: {
              color: "#F5F5F5",
            },
            title: {
              display: true,
              text: this.label,
            }
          },
          x: {
            gridLines: { display: false },
          },
        },
        plugins: {
          datalabels: {
            font: { weight: "bold" },
            align: "end",
            anchor: "end",
          },
        },
        legend: {
          display: true,
          position: "top",
        },
        layout: { padding: { top: 20 } },
      },
    };
  },
  computed: {
    chartData() {
      return this.chartComponentData;
    },
    chartOptions() {
      return this.options;
    },
    myStyles() {
      return {
        position: "relative",
      };
    },
  },
  watch: {
    chartComponentData: {
      handler(n, o) {
        this.watchKeyChange += 1;
      },
      deep: true
    }
  }
};
</script>
