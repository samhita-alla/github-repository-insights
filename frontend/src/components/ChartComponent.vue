<script>
import { Bar } from "vue-chartjs";
import ChartJsPluginDataLabels from "chartjs-plugin-datalabels";
import _ from "lodash";

export default {
  name: "BarChartContainer",
  extends: Bar,
  props: ["chartData", "label"],
  watch: {
    chartData: {
      handler() {
        const clone = _.cloneDeep(this.chartData);
        this.renderChart(clone, this.options);
      },
      deep: true,
    },
  },
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
  mounted() {
    this.addPlugin(ChartJsPluginDataLabels);
    this.renderChart(this.chartData, this.options);
  },
};
</script>
