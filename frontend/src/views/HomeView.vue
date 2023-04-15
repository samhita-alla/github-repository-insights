<template>
  <div class="container px-5 pt-5">
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
          <label for="access-token">Access Token</label>
          <input id="access-token" v-model="form.accessToken" type="text" class="form-control" />
          <small class="form-text text-muted">Useful to circumvent the rate limit issue.</small>
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
              Star growth
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input id="issuegrowth-checkbox" v-model="form.issueGrowthCheck" class="form-check-input" type="checkbox"
              value="" />
            <label class="form-check-label" for="issuegrowth-checkbox">
              Issue/pull request growth
            </label>
          </div>
          <div v-if="form.issueGrowthCheck" class="form-check form-check-inline">
            <input id="issuestats-checkbox" v-model="form.issueTable" class="form-check-input" type="checkbox" value="" />
            <label class="form-check-label" for="issuestats-checkbox">
              Issue stats
            </label>
          </div>

          <div class="form-check form-check-inline">
            <input id="contributorgrowth-checkbox" v-model="form.contributorGrowthCheck" class="form-check-input"
              type="checkbox" value="" />
            <label class="form-check-label" for="contributorgrowth-checkbox">
              Contributor growth
            </label>
          </div>
        </div>
        <button type="submit" class="btn btn-dark" :disabled="
          starGrowthProgress || issueGrowthProgress || contributorGrowthProgress || !allowSubmit
        ">
          View Graph
        </button>
      </form>
      <!-- END FORM -->
      <!-- START STAR GROWTH UI -->
      <SubComponentContainer v-model:otherGithubApi="otherGithubApiStarGrowth" :chart-data="starGrowthChartData"
        :growth-error="starGrowthError" :growth-progress="starGrowthProgress" :img-src="imgSrcStarGrowth"
        :is-add-repo="isAddRepoStarGrowth" :time-delta-frequency=timeDeltaStr heading="stargrowth" title="Star Growth"
        label="Stars" @add-repo-growth="addRepoGrowth" @remove-tag="removeTag"
        @growth-error-button="starGrowthErrorButton">
      </SubComponentContainer>
      <!-- END STAR GROWTH UI -->
      <!-- START ISSUE/PR GROWTH UI -->
      <SubComponentContainer v-model:otherGithubApi="otherGithubApiIssueGrowth" :chart-data="openIssueGrowthChartData"
        :growth-error="issueGrowthError" :growth-progress="issueGrowthProgress" :img-src="imgSrcIssueGrowth"
        :is-add-repo="isAddRepoIssueGrowth" :issue-table="issueTable" :time-delta-frequency=timeDeltaStr
        heading="issuegrowth" title="Issue/Pull Request Growth" label="Open Issues/PRs"
        :chart-data-closed-issues="closedIssueGrowthChartData" closed-issues-label="Closed Issues/PRs"
        @add-repo-growth="addRepoGrowth" @growth-error-button="issueGrowthErrorButton" @remove-tag="removeTag">
      </SubComponentContainer>
      <!-- END ISSUE/PR GROWTH UI -->
      <!-- START CONTRIBUTOR GROWTH UI -->
      <SubComponentContainer v-model:otherGithubApi="otherGithubApiContributorGrowth"
        :chart-data="contributorGrowthChartData" :growth-error="contributorGrowthError"
        :growth-progress="contributorGrowthProgress" :img-src="imgSrcContributorGrowth"
        :is-add-repo="isAddRepoContributorGrowth" :time-delta-frequency=timeDeltaStr heading="contributorgrowth"
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
        accessToken: "",
        timeDelta: 7,
        timeDeltaFrequency: ref(''),
        starGrowthCheck: true,
        issueGrowthCheck: false,
        contributorGrowthCheck: false,
        issueTable: null,
      },
      timeDeltaStr: "",
      starGrowthChartData: null,
      openIssueGrowthChartData: null,
      closedIssueGrowthChartData: null,
      contributorGrowthChartData: null,
      starGrowthProgress: null,
      issueGrowthProgress: null,
      contributorGrowthProgress: null,
      starGrowthError: "",
      issueGrowthError: "",
      contributorGrowthError: "",
      otherGithubApiStarGrowth: "",
      otherGithubApiIssueGrowth: "",
      otherGithubApiContributorGrowth: "",
      issueTable: null,
      isAddRepoStarGrowth: false,
      isAddRepoIssueGrowth: false,
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
        issuegrowth: {
          result_id: "issuegrowth-result",
          progress_id: "issuegrowth-progress",
          progress: "issueGrowthProgress",
          chartdata: "openIssueGrowthChartData",
          error: "issueGrowthError",
          check: "issueGrowthCheck",
          issuetable: "issueTable",
          closed_issues_chart_data: "closedIssueGrowthChartData",
          other_github_api: "otherGithubApiIssueGrowth",
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
    imgSrcIssueGrowth: function () {
      return this.isAddRepoIssueGrowth
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
        this.form.issueGrowthCheck ||
        this.form.contributorGrowthCheck
      );
    },
  },
  watch: {
    form: {
      handler: function () {
        localStorage.setItem("form", JSON.stringify(this.form));
        this.timeDeltaStr = converter.toWords(this.form.timeDeltaFrequency);
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
        (this.form.issueGrowthCheck && this.openIssueGrowthChartData && this.closedIssueGrowthChartData) ||
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
            access_token: this.form.accessToken,
            timedelta: this.form.timeDelta,
            timedelta_frequency: this.form.timeDeltaFrequency,
          };
          if (key == "issuegrowth") {
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
        .get(`/tasks/${taskID}/`, {
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
                if (entity == "issuegrowth") {
                  this[this.entity_mapping[entity].closed_issues_chart_data].datasets.push({
                    label: this[this.entity_mapping[entity].other_github_api],
                    backgroundColor: currentColor,
                    borderColor: currentColor,
                    data: Object.values(res.data.task_result.graph_data_closed_issues),
                  });
                };
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
                if (entity == "issuegrowth") {
                  this[this.entity_mapping[entity].closed_issues_chart_data] = {
                    labels: Object.keys(res.data.task_result.graph_data_closed_issues),
                    datasets: [
                      {
                        label: this.form.githubApi,
                        backgroundColor: currentColor,
                        borderColor: currentColor,
                        data: Object.values(res.data.task_result.graph_data_closed_issues),
                      },
                    ],
                  };
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
            access_token: this.form.accessToken,
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
      if (entity == "issuegrowth") {
        this[this.entity_mapping[entity].closed_issues_chart_data].datasets.splice(index, 1);
      }
    },
    issueGrowthErrorButton: function () {
      this.issueGrowthError = false;
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

