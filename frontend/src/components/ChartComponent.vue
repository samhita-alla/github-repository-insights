<template>
  <Bar :data="chartData" :style="myStyles" />
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
  data() {
    return {
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          yAxes: [
            {
              ticks: {
                beginAtZero: true,
              },
              gridLines: {
                color: "#F5F5F5",
              },
              scaleLabel: {
                display: true,
                labelString: this.label,
              },
            },
          ],
          xAxes: [
            {
              gridLines: { display: false },
              scaleLabel: { display: true, labelString: "Date" },
            },
          ],
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
      return this.chartData;
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
};
</script>
