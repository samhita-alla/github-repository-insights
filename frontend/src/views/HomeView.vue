<template>
  <div class="container">
    <main>
      <div class="py-5 text-center">
        <img
          class="d-block mx-auto mb-4"
          src="../assets/logo.png"
          alt=""
        />
        <h2>Real-Time GitHub Stats</h2>
        <p class="lead">
          Generating real-time GitHub stats for your open-source projects is no
          more a fuss. Assess the daily, weekly, monthly growth graphs to
          understand how your project's faring.
        </p>
      </div>
      <form @submit.prevent="submit">
        <div class="form-group mb-3">
          <label for="github-api">GitHub Repo</label>
          <input
            type="text"
            class="form-control"
            id="github-api"
            placeholder="flyteorg/flyte"
            v-model="form.githubApi"
            required
          />
          <small class="form-text text-muted"
            >GitHub Repo has to be of the format {organization/repo}.</small
          >
        </div>
        <div class="form-group mb-3">
          <label for="access-token">Access Token</label>
          <input
            type="text"
            class="form-control"
            id="access-token"
            v-model="form.accessToken"
          />
          <small class="form-text text-muted"
            >Useful to circumvent the rate limit issue.</small
          >
        </div>
        <div class="form-group mb-3">
          <label for="timedelta"
            >Timedelta (<span id="timedelta-rangeval">7</span>)</label
          >
          <input
            type="range"
            class="form-range"
            id="timedelta"
            min="1"
            max="90"
            v-model="form.timeDelta"
            onInput="document.getElementById('timedelta-rangeval').innerText = document.getElementById('timedelta').value"
          />
          <small class="form-text text-muted"
            >Number of days to consider as the base index, e.g., if 10, growth
            will be computed for every 10 days.</small
          >
        </div>
        <div class="form-group mb-3">
          <label for="timedelta-frequency"
            >Frequency (<span id="timedelta-frequency-rangeval">2</span>)</label
          >
          <input
            type="range"
            class="form-range"
            id="timedelta-frequency"
            min="2"
            max="30"
            v-model="form.timeDeltaFrequency"
            onInput="document.getElementById('timedelta-frequency-rangeval').innerText = document.getElementById('timedelta-frequency').value"
          />
          <small class="form-text text-muted"
            >Number of times Timedelta has to be computed, e.g., if 2, growth
            will be computed for the last 10 days, and the 10 days before
            it.</small
          >
        </div>
        <button type="submit" class="btn btn-primary" :disabled="progress">
          Gimme the Graphs!
        </button>
      </form>
      <div class="my-5" v-if="chartData && chartData.datasets.length >= 1">
        <img
          :src="imgSrc"
          @click="isAddRepo = !isAddRepo"
          role="button"
          class="d-block mx-auto mb-3"
        />
        <small>To add a new repo, click on the + button.</small>
      </div>
      <div class="card" v-if="isAddRepo">
        <div class="card-body">
          <form @submit.prevent="addRepoSubmit">
            <div class="form-group mb-3">
              <label for="other-github-api">GitHub Repo</label>
              <input
                type="text"
                class="form-control"
                id="other-github-api"
                placeholder="flyteorg/flyte"
                v-model="otherGithubApi"
                :disabled="chartData && chartData.datasets.length >= 5"
                required
              />
              <small class="form-text text-muted"
                >GitHub Repo has to be of the format {organization/repo}.</small
              >
            </div>
            <div class="form-group mb-3">
              <label for="other-access-token">Access Token</label>
              <input
                type="text"
                class="form-control"
                id="other-access-token"
                v-model="otherAccessToken"
                :disabled="chartData && chartData.datasets.length >= 5"
              />
              <small class="form-text text-muted"
                >Useful to circumvent the rate limit issue.</small
              >
            </div>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="
                (chartData && chartData.datasets.length >= 5) || progress
              "
            >
              Add a repository
            </button>
          </form>
        </div>
      </div>
      <div
        v-if="chartData && chartData.datasets.length >= 5"
        class="alert alert-warning alert-dismissible fade show d-flex align-items-center"
        role="alert"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="currentColor"
          class="bi bi-exclamation-triangle-fill flex-shrink-0 me-2"
          viewBox="0 0 16 16"
          role="img"
          aria-label="Warning:"
        >
          <path
            d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
          />
        </svg>
        No more than 5 repositories are accepted. Please remove one of your
        added repositories to continue.
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="alert"
          aria-label="Close"
        ></button>
      </div>
      <div v-if="chartData && chartData.datasets.length > 1" class="mt-3">
        <div
          v-for="(dataset, index) in chartData.datasets"
          :key="dataset.label"
        >
          <div
            v-if="index != 0"
            class="btn btn-sm btn-secondary remove-tag-btn"
            @click="removeTag(index)"
          >
            <span>x</span>
            {{ dataset.label }}
          </div>
        </div>
      </div>
      <div class="my-5">
        <p id="progress-label" v-if="progress">Crunching GitHub APIs</p>
        <div v-if="progress" class="progress">
          <div
            class="progress-bar"
            role="progressbar"
            style="width: 0%"
            id="stargrowth-progress"
          >
            0%
          </div>
        </div>
      </div>
      <div
        v-if="stargrowthError"
        class="my-5 alert alert-warning alert-dismissible fade show d-flex align-items-center"
        role="alert"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="currentColor"
          class="bi bi-exclamation-triangle-fill flex-shrink-0 me-2"
          viewBox="0 0 16 16"
          role="img"
          aria-label="Warning:"
        >
          <path
            d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
          />
        </svg>
        {{ stargrowthError }}
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="alert"
          aria-label="Close"
        ></button>
      </div>
      <div
        class="row justify-content-center"
        id="stargrowth-result"
        v-if="chartData"
      >
        <div class="col-10">
          <h3>
            Star growth for every {{ form.timeDelta }} days, repeated
            {{ form.timeDeltaFrequency }} times.
          </h3>
          <BarChartContainer
            class="my-5"
            :chart-data="chartData"
          ></BarChartContainer>
        </div>
      </div>
    </main>
  </div>
</template>

<style>
.remove-tag-btn:hover {
  text-decoration: line-through;
}
</style>

<script>
import axios from "axios";
import BarChartContainer from "../components/ChartComponent.vue";

export default {
  name: "HomeView",
  components: { BarChartContainer },
  data() {
    return {
      form: {
        githubApi: "flyteorg/flyte",
        accessToken: "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",
        timeDelta: 7,
        timeDeltaFrequency: 2,
      },
      chartData: null,
      progress: null,
      stargrowthError: "",
      otherGithubApi: "",
      otherAccessToken: "",
      isAddRepo: false,
      toggle: false,
      backgroundColor: [
        "rgba(255, 99, 132, 0.2)",
        "rgba(255, 159, 64, 0.2)",
        "rgba(255, 205, 86, 0.2)",
        "rgba(75, 192, 192, 0.2)",
        "rgba(54, 162, 235, 0.2)",
        "rgba(153, 102, 255, 0.2)",
        "rgba(201, 203, 207, 0.2)",
      ],
      borderColor: [
        "rgb(255, 99, 132)",
        "rgb(255, 159, 64)",
        "rgb(255, 205, 86)",
        "rgb(75, 192, 192)",
        "rgb(54, 162, 235)",
        "rgb(153, 102, 255)",
        "rgb(201, 203, 207)",
      ],
    };
  },
  computed: {
    imgSrc: function () {
      return this.isAddRepo
        ? require("../assets/icons8-close.svg")
        : require("../assets/icons8-plus-+.svg");
    },
  },
  mounted() {
    this.form = JSON.parse(localStorage.getItem("form")) || this.form;
    document.getElementById("timedelta-rangeval").innerText =
      this.form.timeDelta;
    document.getElementById("timedelta-frequency-rangeval").innerText =
      this.form.timeDeltaFrequency;
  },
  watch: {
    form: {
      handler: function () {
        localStorage.setItem("form", JSON.stringify(this.form));
      },
      deep: true,
    },
  },
  methods: {
    submit: function () {
      if (this.chartData) {
        let message = "This will reset the chart. Continue?";
        if (confirm(message) == false) {
          return;
        }
      }
      axios
        .post("/stargrowth", null, {
          params: {
            github_api: this.form.githubApi,
            access_token: this.form.accessToken,
            timedelta: this.form.timeDelta,
            timedelta_frequency: this.form.timeDeltaFrequency,
          },
        })
        .then((res) => {
          this.getStatus(res.data.task_id);
          this.progress = true;
          this.chartData = null;
          this.stargrowthError = "";
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getStatus(taskID, addRepo = false) {
      axios
        .get(`/tasks/${taskID}`, {
          headers: {
            "Content-Type": "application/json",
          },
        })
        .then((res) => {
          const taskStatus = res.data.task_status;

          document.getElementById("stargrowth-progress").innerText =
            Math.round(
              (res.data.progress["current"] * 100) / res.data.progress["total"]
            ) + "%";
          document.getElementById(
            "stargrowth-progress"
          ).style.width = `${Math.round(
            (res.data.progress["current"] * 100) / res.data.progress["total"]
          )}%`;

          if (taskStatus === "SUCCESS") {
            document.getElementById("stargrowth-progress").innerText = "100%";
            document.getElementById("stargrowth-progress").style.width = "100%";
            setTimeout(() => {
              this.progress = false;
              if (addRepo) {
                this.chartData.datasets.push({
                  label: this.otherGithubApi,
                  backgroundColor:
                    this.backgroundColor[this.chartData.datasets.length],
                  borderColor: this.borderColor[this.chartData.datasets.length],
                  data: Object.values(res.data.task_result),
                });
              } else {
                this.chartData = {
                  labels: Object.keys(res.data.task_result),
                  datasets: [
                    {
                      label: this.form.githubApi,
                      backgroundColor: this.backgroundColor[0],
                      borderColor: this.borderColor[0],
                      data: Object.values(res.data.task_result),
                    },
                  ],
                };
              }
            }, 2000);
            setTimeout(() => {
              document
                .getElementById("stargrowth-result")
                .scrollIntoView({ behavior: "smooth", block: "end" });
            }, 4000);
            return true;
          } else if (taskStatus === "FAILED") {
            setTimeout(() => {
              this.progress = false;
              this.stargrowthError = res.data.task_result;
            }, 2000);
            setTimeout(() => {
              document
                .getElementById("stargrowth-result")
                .scrollIntoView({ behavior: "smooth", block: "end" });
            }, 4000);
            return false;
          }
          setTimeout(() => {
            this.getStatus(res.data.task_id, addRepo);
          }, 1000);
        })
        .catch((err) => {
          console.log(err);
        });
    },
    addRepoSubmit: function () {
      const checkLabel = (obj) => obj.label === this.otherGithubApi;
      if (this.chartData.datasets.some(checkLabel)) {
        this.stargrowthError = "This repo has already been added.";
        return;
      }
      axios
        .post("/stargrowth", null, {
          params: {
            github_api: this.otherGithubApi,
            access_token: this.otherAccessToken,
            timedelta: this.form.timeDelta,
            timedelta_frequency: this.form.timeDeltaFrequency,
          },
        })
        .then((res) => {
          this.getStatus(res.data.task_id, true);
          this.progress = true;
          this.stargrowthError = "";
        })
        .catch((error) => {
          console.error(error);
        });
    },
    removeTag: function (index) {
      this.chartData.datasets.splice(index, 1);
    },
  },
};
</script>
