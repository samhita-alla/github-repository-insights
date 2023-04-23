<template>
  <div class="px-5 pt-2 justify-content-end d-flex">
    <nav class="navbar navbar-expand-lg navbar-light bg-white">
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav">
          <li class="nav-item">
            <a class="nav-link"
              :href="'https://github.com/login/oauth/authorize?client_id=' + gitHubClientId + '&state=' + gitHubState"
              target="_blank"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"
                class="___ref-icon mantine-t4fnek">
                <path
                  d="M16.555 3.843l3.602 3.602a2.877 2.877 0 0 1 0 4.069l-2.643 2.643a2.877 2.877 0 0 1 -4.069 0l-.301 -.301l-6.558 6.558a2 2 0 0 1 -1.239 .578l-.175 .008h-1.172a1 1 0 0 1 -.993 -.883l-.007 -.117v-1.172a2 2 0 0 1 .467 -1.284l.119 -.13l.414 -.414h2v-2h2v-2l2.144 -2.144l-.301 -.301a2.877 2.877 0 0 1 0 -4.069l2.643 -2.643a2.877 2.877 0 0 1 4.069 0z">
                </path>
                <path d="M15 9h.01"></path>
              </svg>
              Access Token
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="https://github.com/samhita-alla/github-stats" target="_blank"><svg
                xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                class="tabler-icon tabler-icon-brand-github">
                <path
                  d="M9 19c-4.3 1.4 -4.3 -2.5 -6 -3m12 5v-3.5c0 -1 .1 -1.4 -.5 -2c2.8 -.3 5.5 -1.4 5.5 -6a4.6 4.6 0 0 0 -1.3 -3.2a4.2 4.2 0 0 0 -.1 -3.2s-1.1 -.3 -3.5 1.3a12.3 12.3 0 0 0 -6.2 0c-2.4 -1.6 -3.5 -1.3 -3.5 -1.3a4.2 4.2 0 0 0 -.1 3.2a4.6 4.6 0 0 0 -1.3 3.2c0 4.6 2.7 5.7 5.5 6c-.6 .6 -.6 1.2 -.5 2v3.5">
                </path>
              </svg>
              Source Code
            </a>
          </li>
        </ul>
      </div>
    </nav>
  </div>
  <div class="container px-5">
    <main>
      <div class="py-5 text-center">
        <h1>GitHub Repository Insights</h1>
        <p class="lead">
          Generate real-time GitHub insights for your open-source projects and stay informed on how your
          project is progressing.
        </p>
      </div>
      <!-- START FORM -->
      <form @submit.prevent="submit">
        <div class="form-group mb-3">
          <label for="github-api">GitHub Repo</label>
          <input id="github-api" v-model="form.githubApi" type="text" class="form-control" placeholder="flyteorg/flyte"
            required />
          <small class="form-text text-muted">GitHub Repo has to be of the format {organization/repo}.</small>
        </div>
        <div class="form-group mb-3">
          <label for="timedelta">Timedelta (<span id="timedelta-rangeval">7</span>)</label>
          <input id="timedelta" v-model="form.timeDelta" type="range" class="form-range" min="1" max="30"
            oninput="document.getElementById('timedelta-rangeval').innerText = document.getElementById('timedelta').value" />
          <small class="form-text text-muted">Number of days to consider as the base index. For example, if set to 10,
            growth will be computed every 10 days.</small>
        </div>
        <div class="form-group mb-3">
          <label for="timedelta-frequency">Frequency (<span id="timedelta-frequency-rangeval">2</span>)</label>
          <input id="timedelta-frequency" v-model="form.timeDeltaFrequency" type="range" class="form-range" min="2"
            max="20"
            oninput="document.getElementById('timedelta-frequency-rangeval').innerText = document.getElementById('timedelta-frequency').value" />
          <small class="form-text text-muted">Number of times Timedelta needs to be computed. For example, if set to 2,
            growth will be calculated for the past 10 days as well as the 10 days before that.</small>
        </div>
        <div class="mb-3">
          <div class="form-check form-check-inline">
            <input id="stargrowth-checkbox" v-model="form.starGrowthCheck" class="form-check-input" type="checkbox"
              value="" checked />
            <label class="form-check-label" for="stargrowth-checkbox">
              Star Growth
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input id="openissuegrowth-checkbox" v-model="form.openIssueGrowthCheck" class="form-check-input" type="checkbox"
              value="" />
            <label class="form-check-label" for="openissuegrowth-checkbox">
              Open Issue/Pull Request Growth
            </label>
          </div>
          <div v-if="form.openIssueGrowthCheck" class="form-check form-check-inline">
            <input id="issuestats-checkbox" v-model="form.issueTable" class="form-check-input" type="checkbox" value="" />
            <label class="form-check-label" for="issuestats-checkbox">
              Issue Stats
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input id="closedissuegrowth-checkbox" v-model="form.closedIssueGrowthCheck" class="form-check-input" type="checkbox"
              value="" />
            <label class="form-check-label" for="closedissuegrowth-checkbox">
              Closed Issue/Pull Request Growth
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input id="contributorgrowth-checkbox" v-model="form.contributorGrowthCheck" class="form-check-input"
              type="checkbox" value="" />
            <label class="form-check-label" for="contributorgrowth-checkbox">
              Contributor Growth
            </label>
          </div>
        </div>

        <button type="submit" class="btn btn-dark" :disabled="
          starGrowthProgress || openIssueGrowthProgress || closedIssueGrowthProgress || contributorGrowthProgress || !allowSubmit
        ">
          View Graph
        </button>
      </form>
      <!-- END FORM -->
      <!-- START STAR GROWTH UI -->
      <SubComponentContainer v-model:otherGithubApi="otherGithubApiStarGrowth" :chart-data="starGrowthChartData"
        :growth-error="starGrowthError" :growth-progress="starGrowthProgress" :img-src="imgSrcStarGrowth"
        :is-add-repo="isAddRepoStarGrowth" :time-delta-frequency="timeDeltaStr" heading="stargrowth" title="Star Growth"
        label="Stars" @add-repo-growth="addRepoGrowth" @remove-tag="removeTag"
        @growth-error-button="starGrowthErrorButton">
      </SubComponentContainer>
      <!-- END STAR GROWTH UI -->
      <!-- START OPEN ISSUE/PR GROWTH UI -->
      <SubComponentContainer v-model:otherGithubApi="otherGithubApiOpenIssueGrowth" :chart-data="openIssueGrowthChartData"
        :growth-error="openIssueGrowthError" :growth-progress="openIssueGrowthProgress" :img-src="imgSrcOpenIssueGrowth"
        :is-add-repo="isAddRepoOpenIssueGrowth" :issue-table="issueTable" :time-delta-frequency="timeDeltaStr"
        heading="openissuegrowth" title="Open Issue/Pull Request Growth" label="Open Issues/PRs"
        @add-repo-growth="addRepoGrowth" @growth-error-button="openIssueGrowthErrorButton" @remove-tag="removeTag">
      </SubComponentContainer>
      <!-- END OPEN ISSUE/PR GROWTH UI -->
      <!-- START CLOSED ISSUE/PR GROWTH UI -->
      <SubComponentContainer v-model:otherGithubApi="otherGithubApiClosedIssueGrowth"
        :chart-data="closedIssueGrowthChartData" :growth-error="closedIssueGrowthError"
        :growth-progress="closedIssueGrowthProgress" :img-src="imgSrcClosedIssueGrowth"
        :is-add-repo="isAddRepoClosedIssueGrowth" :time-delta-frequency="timeDeltaStr" heading="closedissuegrowth"
        title="Closed Issue/Pull Request Growth" label="Closed Issues/PRs" @add-repo-growth="addRepoGrowth"
        @growth-error-button="closedIssueGrowthErrorButton" @remove-tag="removeTag">
      </SubComponentContainer>
      <!-- END CLOSED ISSUE/PR GROWTH UI -->
      <!-- START CONTRIBUTOR GROWTH UI -->
      <SubComponentContainer v-model:otherGithubApi="otherGithubApiContributorGrowth"
        :chart-data="contributorGrowthChartData" :growth-error="contributorGrowthError"
        :growth-progress="contributorGrowthProgress" :img-src="imgSrcContributorGrowth"
        :is-add-repo="isAddRepoContributorGrowth" :time-delta-frequency="timeDeltaStr" heading="contributorgrowth"
        title="Contributor Growth" label="Contributors" @add-repo-growth="addRepoGrowth"
        @growth-error-button="contributorGrowthErrorButton" @remove-tag="removeTag">
      </SubComponentContainer>
      <!-- END CONTRIBUTOR GROWTH UI -->
    </main>
  </div>
</template>

<script>
import axios from "axios";
import SubComponentContainer from "../components/SubComponent.vue";
import { ref } from "vue";

var converter = require("number-to-words");

export default {
  name: "HomeView",
  components: { SubComponentContainer },
  data() {
    return {
      form: {
        githubApi: "flyteorg/flyte",
        timeDelta: 7,
        timeDeltaFrequency: ref(''),
        starGrowthCheck: true,
        openIssueGrowthCheck: false,
        closedIssueGrowthCheck: false,
        contributorGrowthCheck: false,
        issueTable: null,
      },
      gitHubClientId: process.env.VUE_APP_GITHUB_CLIENT_ID,
      gitHubState: Math.random().toString(36).slice(2),
      timeDeltaStr: "",
      starGrowthChartData: null,
      openIssueGrowthChartData: null,
      closedIssueGrowthChartData: null,
      contributorGrowthChartData: null,
      starGrowthProgress: null,
      openIssueGrowthProgress: null,
      closedIssueGrowthProgress: null,
      contributorGrowthProgress: null,
      starGrowthError: "",
      openIssueGrowthError: "",
      closedIssueGrowthError: "",
      contributorGrowthError: "",
      otherGithubApiStarGrowth: "",
      otherGithubApiOpenIssueGrowth: "",
      otherGithubApiClosedIssueGrowth: "",
      otherGithubApiContributorGrowth: "",
      issueTable: null,
      isAddRepoStarGrowth: false,
      isAddRepoOpenIssueGrowth: false,
      isAddRepoClosedIssueGrowth: false,
      isAddRepoContributorGrowth: false,
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
      entity_mapping: {
        stargrowth: {
          result_id: "stargrowth-result",
          progress_id: "stargrowth-progress",
          progress: "starGrowthProgress",
          chartdata: "starGrowthChartData",
          error: "starGrowthError",
          check: "starGrowthCheck",
          other_github_api: "otherGithubApiStarGrowth",
          usedColors: [],
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
          usedColors: [],
        },
        closedissuegrowth: {
          result_id: "closedissuegrowth-result",
          progress_id: "closedissuegrowth-progress",
          progress: "closedIssueGrowthProgress",
          chartdata: "closedIssueGrowthChartData",
          error: "closedIssueGrowthError",
          check: "closedIssueGrowthCheck",
          other_github_api: "otherGithubApiClosedIssueGrowth",
          usedColors: [],
        },
        contributorgrowth: {
          result_id: "contributorgrowth-result",
          progress_id: "contributorgrowth-progress",
          progress: "contributorGrowthProgress",
          chartdata: "contributorGrowthChartData",
          error: "contributorGrowthError",
          check: "contributorGrowthCheck",
          other_github_api: "otherGithubApiContributorGrowth",
          usedColors: [],
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
    imgSrcClosedIssueGrowth: function () {
      return this.isAddRepoClosedIssueGrowth
        ? require("../assets/icons8-close.svg")
        : require("../assets/icons8-plus-+.svg");
    },
    imgSrcContributorGrowth: function () {
      return this.isAddRepoContributorGrowth
        ? require("../assets/icons8-close.svg")
        : require("../assets/icons8-plus-+.svg");
    },
    allowSubmit: function () {
      return (
        this.form.starGrowthCheck ||
        this.form.openIssueGrowthCheck ||
        this.form.closedIssueGrowthCheck ||
        this.form.contributorGrowthCheck
      );
    },
  },
  watch: {
    form: {
      handler: function () {
        localStorage.setItem("form", JSON.stringify(this.form));
        if (this.form.timeDeltaFrequency) {
          this.timeDeltaStr = converter.toWords(this.form.timeDeltaFrequency);
        }
      },
      deep: true,
    },
  },
  mounted() {
    this.form = JSON.parse(localStorage.getItem("form")) || this.form;
    document.getElementById("timedelta-rangeval").innerText =
      this.form.timeDelta;
    document.getElementById("timedelta-frequency-rangeval").innerText =
      this.form.timeDeltaFrequency;
  },
  methods: {
    submit: function () {
      if (
        (this.form.starGrowthCheck && this.starGrowthChartData) ||
        (this.form.openIssueGrowthCheck && this.openIssueGrowthChartData) ||
        (this.form.closedIssueGrowthCheck && this.closedIssueGrowthChartData) ||
        (this.form.contributorGrowthCheck && this.contributorGrowthChartData)
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
              this[this.entity_mapping[key].progress] = true;
              this[this.entity_mapping[key].chartdata] = null;
              this[this.entity_mapping[key].error] = "";
              this.getStatus(res.data.task_id, key);
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
                var unusedColors = this.backgroundColor.filter(x => !this.entity_mapping[entity].usedColors.includes(x));
                var currentColor = unusedColors[Math.floor(Math.random() * unusedColors.length)];
                this.entity_mapping[entity].usedColors.push(currentColor);
                this[this.entity_mapping[entity].chartdata].datasets.push({
                  label: this[this.entity_mapping[entity].other_github_api],
                  backgroundColor: currentColor,
                  borderColor: currentColor,
                  data: Object.values(res.data.task_result.graph_data),
                });
              } else {
                var currentColor = this.backgroundColor[0]
                this.entity_mapping[entity].usedColors = [currentColor];
                this[this.entity_mapping[entity].chartdata] = {
                  labels: Object.keys(res.data.task_result.graph_data),
                  datasets: [
                    {
                      label: this.form.githubApi,
                      backgroundColor: currentColor,
                      borderColor: currentColor,
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
            return false;
          }
          setTimeout(() => {
            this.getStatus(res.data.task_id, entity, addRepo);
          }, 1000);
        })
        .catch((err) => {
          console.error(err);
        });
    },
    addRepoGrowth: function (entity) {
      const checkLabel = (obj) =>
        obj.label === this[this.entity_mapping[entity].other_github_api];

      if (this[this.entity_mapping[entity].chartdata].datasets.some(checkLabel)) {
        this[this.entity_mapping[entity].error] =
          "This repo has already been added.";
        return;
      }
      axios
        .post("/" + entity, null, {
          params: {
            github_api: this[this.entity_mapping[entity].other_github_api],
            timedelta: this.form.timeDelta,
            timedelta_frequency: this.form.timeDeltaFrequency,
          },
        })
        .then((res) => {
          this.getStatus(res.data.task_id, entity, true);
          this[this.entity_mapping[entity].progress] = true;
          this[this.entity_mapping[entity].error] = "";
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
    closedIssueGrowthErrorButton: function () {
      this.closedIssueGrowthError = false;
    },
    starGrowthErrorButton: function () {
      this.starGrowthError = false;
    },
    contributorGrowthErrorButton: function () {
      this.contributorGrowthError = false;
    }
  },
};
</script>

