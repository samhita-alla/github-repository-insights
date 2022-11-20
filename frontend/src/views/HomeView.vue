<template>
  <div class="container">
    <main>
      <div class="py-5 text-center">
        <img class="d-block mx-auto mb-4" src="../assets/logo.png" alt="" />
        <h2>Real-Time GitHub Stats</h2>
        <p class="lead">
          Generating real-time GitHub stats for your open-source projects is no
          more a fuss. Assess the daily, weekly, monthly growth graphs to
          understand how your project's faring.
        </p>
      </div>
      <!-- START FORM -->
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
            will be computed every 10 days.</small
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
            >Number of times Timedelta needs to be computed, e.g., if 2, growth
            will be computed for the last 10 days, and the 10 days before
            it.</small
          >
        </div>
        <div class="mb-3">
          <div class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="checkbox"
              value=""
              id="stargrowth-checkbox"
              v-model="form.starGrowthCheck"
              checked
            />
            <label class="form-check-label" for="stargrowth-checkbox">
              Star growth
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="checkbox"
              value=""
              id="openissuegrowth-checkbox"
              v-model="form.openIssueGrowthCheck"
            />
            <label class="form-check-label" for="openissuegrowth-checkbox">
              Open issue/PR growth
            </label>
          </div>
          <div
            class="form-check form-check-inline"
            v-if="form.openIssueGrowthCheck"
          >
            <input
              class="form-check-input"
              type="checkbox"
              value=""
              id="openissuestats-checkbox"
              v-model="form.issueTable"
            />
            <label class="form-check-label" for="openissuestats-checkbox">
              Issue Stats
            </label>
          </div>
        </div>
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="
            starGrowthProgress || openIssueGrowthProgress || !allowSubmit
          "
        >
          Gimme the Graphs and Numbers!
        </button>
      </form>
      <!-- END FORM -->
      <!-- START STAR GROWTH UI -->
      <div
        class="card my-5"
        v-if="starGrowthChartData || starGrowthError || starGrowthProgress"
      >
        <div class="card-header" id="headingStarGrowth">
          <h5 class="mb-0">Star Growth</h5>
        </div>
        <div>
          <!-- START STAR GROWTH ADD REPO UI -->
          <div
            class="my-5"
            v-if="
              starGrowthChartData && starGrowthChartData.datasets.length >= 1
            "
          >
            <img
              :src="imgSrcStarGrowth"
              @click="isAddRepoStarGrowth = !isAddRepoStarGrowth"
              role="button"
              class="d-block mx-auto mb-3"
            />
            <small>To add a new repo, click on the + button.</small>
          </div>
          <div class="card mx-3" v-if="isAddRepoStarGrowth">
            <div class="card-body">
              <form @submit.prevent="addRepoSubmitStarGrowth">
                <div class="form-group mb-3">
                  <label for="other-github-api-star-growth">GitHub Repo</label>
                  <input
                    type="text"
                    class="form-control"
                    id="other-github-api-star-growth"
                    placeholder="flyteorg/flyte"
                    v-model="otherGithubApiStarGrowth"
                    :disabled="
                      starGrowthChartData &&
                      starGrowthChartData.datasets.length >= 5
                    "
                    required
                  />
                  <small class="form-text text-muted"
                    >GitHub Repo has to be of the format
                    {organization/repo}.</small
                  >
                </div>
                <div class="form-group mb-3">
                  <label for="other-access-token">Access Token</label>
                  <input
                    type="text"
                    class="form-control"
                    id="other-access-token"
                    v-model="otherAccessToken"
                    :disabled="
                      starGrowthChartData &&
                      starGrowthChartData.datasets.length >= 2
                    "
                  />
                  <small class="form-text text-muted"
                    >Useful to circumvent the rate limit issue.</small
                  >
                </div>
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="
                    (starGrowthChartData &&
                      starGrowthChartData.datasets.length >= 5) ||
                    starGrowthProgress
                  "
                >
                  Add repository
                </button>
              </form>
            </div>
          </div>
          <!-- END STAR GROWTH ADD REPO UI -->
          <div aria-labelledby="headingStarGrowth">
            <div class="card-body">
              <div
                v-if="
                  starGrowthChartData && starGrowthChartData.datasets.length > 1
                "
                class="mt-3"
              >
                <span
                  v-for="(dataset, index) in starGrowthChartData.datasets"
                  :key="dataset.label"
                >
                  <div
                    v-if="index != 0"
                    class="btn btn-sm btn-secondary remove-tag-btn me-2"
                    @click="removeTag(index, 'stargrowth')"
                  >
                    <span>x</span>
                    {{ dataset.label }}
                  </div>
                </span>
              </div>
              <div class="my-5">
                <p id="progress-label" v-if="starGrowthProgress">
                  ⭐️ Crunching GitHub APIs ⭐️
                </p>
                <div v-if="starGrowthProgress" class="progress">
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
                v-if="
                  starGrowthChartData &&
                  starGrowthChartData.datasets.length >= 5
                "
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
                No more than 5 repositories can be added. Please remove a
                repository to continue.
                <button
                  type="button"
                  class="btn-close"
                  data-bs-dismiss="alert"
                  aria-label="Close"
                ></button>
              </div>
              <div
                v-if="starGrowthError"
                class="my-5 alert alert-warning alert-dismissible d-flex align-items-center"
                :class="starGrowthError ? 'show' : 'fade'"
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
                {{ starGrowthError }}
                <button
                  type="button"
                  class="btn-close"
                  aria-label="Close"
                  @click="starGrowthErrorButton()"
                ></button>
              </div>
              <div
                class="row justify-content-center"
                id="stargrowth-result"
                v-if="starGrowthChartData"
              >
                <div class="col-md-10 col-sm-12">
                  <h3>
                    Star growth every {{ form.timeDelta }} days, repeated
                    {{ form.timeDeltaFrequency }} times.
                  </h3>
                  <BarChartContainer
                    class="my-5"
                    :chart-data="starGrowthChartData"
                    label="Stars"
                  ></BarChartContainer>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- END STAR GROWTH UI -->
      <!-- START OPEN ISSUE/PR GROWTH UI -->
      <div
        class="card my-5"
        v-if="
          openIssueGrowthChartData ||
          openIssueGrowthError ||
          openIssueGrowthProgress
        "
      >
        <div class="card-header" id="headingOpenIssueGrowth">
          <h5 class="mb-0">Open Issue/PR Growth</h5>
        </div>
        <!-- START OPEN ISSUE GROWTH ADD REPO UI -->
        <div class="card">
          <div
            class="my-5"
            v-if="
              openIssueGrowthChartData &&
              openIssueGrowthChartData.datasets.length >= 1
            "
          >
            <img
              :src="imgSrcOpenIssueGrowth"
              @click="isAddRepoOpenIssueGrowth = !isAddRepoOpenIssueGrowth"
              role="button"
              class="d-block mx-auto mb-3"
            />
            <small>To add a new repo, click on the + button.</small>
          </div>
          <div class="card mx-3" v-if="isAddRepoOpenIssueGrowth">
            <div class="card-body">
              <form @submit.prevent="addRepoSubmitOpenIssueGrowth">
                <div class="form-group mb-3">
                  <label for="other-github-api-open-issue-growth"
                    >GitHub Repo</label
                  >
                  <input
                    type="text"
                    class="form-control"
                    id="other-github-api-open-issue-growth"
                    placeholder="flyteorg/flyte"
                    v-model="otherGithubApiOpenIssueGrowth"
                    :disabled="
                      openIssueGrowthChartData &&
                      openIssueGrowthChartData.datasets.length >= 5
                    "
                    required
                  />
                  <small class="form-text text-muted"
                    >GitHub Repo has to be of the format
                    {organization/repo}.</small
                  >
                </div>
                <div class="form-group mb-3">
                  <label for="other-access-token">Access Token</label>
                  <input
                    type="text"
                    class="form-control"
                    id="other-access-token"
                    v-model="otherAccessToken"
                    :disabled="
                      openIssueGrowthChartData &&
                      openIssueGrowthChartData.datasets.length >= 5
                    "
                  />
                  <small class="form-text text-muted"
                    >Useful to circumvent the rate limit issue.</small
                  >
                </div>
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="
                    (openIssueGrowthChartData &&
                      openIssueGrowthChartData.datasets.length >= 5) ||
                    openIssueGrowthProgress
                  "
                >
                  Add repository
                </button>
              </form>
            </div>
          </div>
          <!-- END OPEN ISSUE GROWTH ADD REPO UI -->
          <div aria-labelledby="headingOpenIssueGrowth">
            <div class="card-body">
              <div
                v-if="
                  openIssueGrowthChartData &&
                  openIssueGrowthChartData.datasets.length > 1
                "
                class="mt-3"
              >
                <span
                  v-for="(dataset, index) in openIssueGrowthChartData.datasets"
                  :key="dataset.label"
                >
                  <div
                    v-if="index != 0"
                    class="btn btn-sm btn-secondary remove-tag-btn me-2"
                    @click="removeTag(index, 'openissuegrowth')"
                  >
                    <span>x</span>
                    {{ dataset.label }}
                  </div>
                </span>
              </div>
              <div class="my-5">
                <p id="progress-label" v-if="openIssueGrowthProgress">
                  🛠 Crunching GitHub APIs 🛠
                </p>
                <div v-if="openIssueGrowthProgress" class="progress">
                  <div
                    class="progress-bar"
                    role="progressbar"
                    style="width: 0%"
                    id="openissuegrowth-progress"
                  >
                    0%
                  </div>
                </div>
              </div>
              <div
                v-if="
                  openIssueGrowthChartData &&
                  openIssueGrowthChartData.datasets.length >= 5
                "
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
                No more than 5 repositories can be added. Please remove a
                repository to continue.
                <button
                  type="button"
                  class="btn-close"
                  data-bs-dismiss="alert"
                  aria-label="Close"
                ></button>
              </div>
              <div
                v-if="openIssueGrowthError"
                class="my-5 alert alert-warning alert-dismissible d-flex align-items-center"
                :class="openIssueGrowthError ? 'show' : 'fade'"
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
                {{ openIssueGrowthError }}
                <button
                  type="button"
                  class="btn-close"
                  data-hide="alert"
                  aria-label="Close"
                  @click="openIssueGrowthErrorButton()"
                ></button>
              </div>
              <div
                class="row justify-content-center"
                id="openissuegrowth-result"
                v-if="openIssueGrowthChartData"
              >
                <div class="col-md-10 col-sm-12">
                  <h3>
                    Open Issue/PR growth every {{ form.timeDelta }} days,
                    repeated {{ form.timeDeltaFrequency }} times.
                  </h3>
                  <BarChartContainer
                    class="my-5"
                    :chart-data="openIssueGrowthChartData"
                    label="Open Issues/PRs"
                  ></BarChartContainer>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="card">
          <div
            class="row justify-content-center"
            id="openissuegrowth-table"
            v-if="issueTable"
          >
            <div class="col-md-10 col-sm-12 my-5">
              <table class="table">
                <thead>
                  <tr>
                    <th>Addressed Issues</th>
                    <th>Unaddressed Issues</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="text-left">
                      <ul class="list-group">
                        <a
                          class="list-group-item"
                          :href="value.url"
                          v-for="(value, index) in issueTable.addressed"
                          :key="index"
                        >
                          {{ value.title }}
                        </a>
                      </ul>
                    </td>
                    <td class="text-left">
                      <ul class="list-group">
                        <a
                          class="list-group-item"
                          :href="value.url"
                          v-for="(value, index) in issueTable.unaddressed"
                          :key="index"
                        >
                          {{ value.title }}
                        </a>
                      </ul>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      <!-- END OPEN ISSUE/PR GROWTH UI -->
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
        starGrowthCheck: true,
        openIssueGrowthCheck: false,
        issueTable: false,
      },
      starGrowthChartData: null,
      openIssueGrowthChartData: null,
      starGrowthProgress: null,
      openIssueGrowthProgress: null,
      starGrowthError: "",
      openIssueGrowthError: "",
      otherGithubApiStarGrowth: "",
      otherGithubApiOpenIssueGrowth: "",
      issueTable: false,
      isAddRepoStarGrowth: false,
      isAddRepoOpenIssueGrowth: false,
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
      entity_mapping: {
        stargrowth: {
          result_id: "stargrowth-result",
          progress_id: "stargrowth-progress",
          progress: "starGrowthProgress",
          chartdata: "starGrowthChartData",
          error: "starGrowthError",
          check: "starGrowthCheck",
          other_github_api: "otherGithubApiStarGrowth",
        },
        openissuegrowth: {
          result_id: "openissuegrowth-result",
          progress_id: "openissuegrowth-progress",
          progress: "openIssueGrowthProgress",
          chartdata: "openIssueGrowthChartData",
          error: "openIssueGrowthError",
          check: "openIssueGrowthCheck",
          issuetable: "issueTable",
          other_github_api: "otherGithubApiOpenIssueGrowth",
        },
      },
    };
  },
  computed: {
    imgSrcStarGrowth: function () {
      return this.isAddRepoStarGrowth
        ? require("../assets/icons8-close.svg")
        : require("../assets/icons8-plus-+.svg");
    },
    imgSrcOpenIssueGrowth: function () {
      return this.isAddRepoOpenIssueGrowth
        ? require("../assets/icons8-close.svg")
        : require("../assets/icons8-plus-+.svg");
    },
    allowSubmit: function () {
      return this.form.starGrowthCheck || this.form.openIssueGrowthCheck;
    },
    otherAccessToken: function () {
      return this.form.accessToken;
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
      if (
        (this.form.starGrowthCheck && this.starGrowthChartData) ||
        (this.form.openIssueGrowthCheck && this.openIssueGrowthChartData)
      ) {
        let message = "This will reset the chart(s). Continue?";
        if (confirm(message) == false) {
          return;
        }
      }
      for (let key in this.entity_mapping) {
        if (this.form[this.entity_mapping[key].check]) {
          var params = {
            github_api: this.form.githubApi,
            access_token: this.form.accessToken,
            timedelta: this.form.timeDelta,
            timedelta_frequency: this.form.timeDeltaFrequency,
          };
          if (key == "openissuegrowth") {
            params["issue_stats"] =
              this.form[this.entity_mapping[key].issuetable];
          }
          axios
            .post("/" + key, null, {
              params: params,
            })
            .then((res) => {
              this.getStatus(res.data.task_id, key);
              this[this.entity_mapping[key].progress] = true;
              this[this.entity_mapping[key].chartdata] = null;
              this[this.entity_mapping[key].error] = "";
            })
            .catch((error) => {
              console.error(error);
            });
        }
      }
    },
    getStatus(taskID, entity, addRepo = false) {
      axios
        .get(`/tasks/${taskID}`, {
          headers: {
            "Content-Type": "application/json",
          },
        })
        .then((res) => {
          const taskStatus = res.data.task_status;
          document.getElementById(
            this.entity_mapping[entity].progress_id
          ).innerText =
            Math.round(
              (res.data.progress["current"] * 100) / res.data.progress["total"]
            ) + "%";
          document.getElementById(
            this.entity_mapping[entity].progress_id
          ).style.width = `${Math.round(
            (res.data.progress["current"] * 100) / res.data.progress["total"]
          )}%`;

          if (taskStatus === "SUCCESS") {
            document.getElementById(
              this.entity_mapping[entity].progress_id
            ).innerText = "100%";
            document.getElementById(
              this.entity_mapping[entity].progress_id
            ).style.width = "100%";
            setTimeout(() => {
              this[this.entity_mapping[entity].progress] = false;
              if (addRepo) {
                this[this.entity_mapping[entity].chartdata].datasets.push({
                  label: this[this.entity_mapping[entity].other_github_api],
                  backgroundColor:
                    this.backgroundColor[
                      this[this.entity_mapping[entity].chartdata].datasets
                        .length
                    ],
                  borderColor:
                    this.borderColor[
                      this[this.entity_mapping[entity].chartdata].datasets
                        .length
                    ],
                  data: Object.values(res.data.task_result.graph_data),
                });
              } else {
                this[this.entity_mapping[entity].chartdata] = {
                  labels: Object.keys(res.data.task_result.graph_data),
                  datasets: [
                    {
                      label: this.form.githubApi,
                      backgroundColor: this.backgroundColor[0],
                      borderColor: this.borderColor[0],
                      data: Object.values(res.data.task_result.graph_data),
                    },
                  ],
                };
                if (this.form[this.entity_mapping[entity].issuetable]) {
                  this[this.entity_mapping[entity].issuetable] =
                    res.data.task_result.issue_map;
                }
              }
            }, 2000);
            setTimeout(() => {
              document
                .getElementById(this.entity_mapping[entity].result_id)
                .scrollIntoView({ behavior: "smooth", block: "end" });
            }, 4000);
            return true;
          } else if (taskStatus === "FAILED") {
            setTimeout(() => {
              this[this.entity_mapping[entity].progress] = false;
              this[this.entity_mapping[entity].error] = res.data.task_result;
            }, 2000);
            setTimeout(() => {
              document
                .getElementById(this.entity_mapping[entity].result_id)
                .scrollIntoView({ behavior: "smooth", block: "end" });
            }, 4000);
            return false;
          }
          setTimeout(() => {
            this.getStatus(res.data.task_id, entity, addRepo);
          }, 1000);
        })
        .catch((err) => {
          console.log(err);
        });
    },
    addRepoSubmitStarGrowth: function () {
      let key = "stargrowth";
      const checkLabel = (obj) => obj.label === this.otherGithubApiStarGrowth;
      if (this[this.entity_mapping[key].chartdata].datasets.some(checkLabel)) {
        this[this.entity_mapping[key].error] =
          "This repo has already been added.";
        return;
      }
      axios
        .post("/" + key, null, {
          params: {
            github_api: this.otherGithubApiStarGrowth,
            access_token: this.otherAccessToken,
            timedelta: this.form.timeDelta,
            timedelta_frequency: this.form.timeDeltaFrequency,
          },
        })
        .then((res) => {
          this.getStatus(res.data.task_id, key, true);
          this[this.entity_mapping[key].progress] = true;
          this[this.entity_mapping[key].error] = "";
        })
        .catch((error) => {
          console.error(error);
        });
    },
    addRepoSubmitOpenIssueGrowth: function () {
      let key = "openissuegrowth";
      const checkLabel = (obj) =>
        obj.label === this.otherGithubApiOpenIssueGrowth;
      if (this[this.entity_mapping[key].chartdata].datasets.some(checkLabel)) {
        this[this.entity_mapping[key].error] =
          "This repo has already been added.";
        return;
      }
      axios
        .post("/" + key, null, {
          params: {
            github_api: this.otherGithubApiOpenIssueGrowth,
            access_token: this.otherAccessToken,
            timedelta: this.form.timeDelta,
            timedelta_frequency: this.form.timeDeltaFrequency,
          },
        })
        .then((res) => {
          this.getStatus(res.data.task_id, key, true);
          this[this.entity_mapping[key].progress] = true;
          this[this.entity_mapping[key].error] = "";
        })
        .catch((error) => {
          console.error(error);
        });
    },
    removeTag: function (index, entity) {
      this[this.entity_mapping[entity].chartdata].datasets.splice(index, 1);
    },
    openIssueGrowthErrorButton: function () {
      this.openIssueGrowthError = false;
    },
    starGrowthErrorButton: function () {
      this.starGrowthError = false;
    },
  },
};
</script>
