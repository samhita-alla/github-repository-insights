<template>
  <div class="px-5 pt-2 justify-content-end d-flex">
    <nav class="navbar navbar-expand-lg navbar-light bg-white">
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div id="navbarNav" class="collapse navbar-collapse">
        <ul class="navbar-nav">
          <li class="nav-item text-start">
            <button class="nav-link border-0 bg-transparent" data-bs-toggle="modal" data-bs-target="#accessTokenModal">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"
                class="___ref-icon mantine-t4fnek align-middle">
                <path
                  d="M16.555 3.843l3.602 3.602a2.877 2.877 0 0 1 0 4.069l-2.643 2.643a2.877 2.877 0 0 1 -4.069 0l-.301 -.301l-6.558 6.558a2 2 0 0 1 -1.239 .578l-.175 .008h-1.172a1 1 0 0 1 -.993 -.883l-.007 -.117v-1.172a2 2 0 0 1 .467 -1.284l.119 -.13l.414 -.414h2v-2h2v-2l2.144 -2.144l-.301 -.301a2.877 2.877 0 0 1 0 -4.069l2.643 -2.643a2.877 2.877 0 0 1 4.069 0z">
                </path>
                <path d="M15 9h.01"></path>
              </svg>
              <span class="align-middle ms-1">Access Token</span>
            </button>
          </li>
          <li class="nav-item text-start">
            <a class="nav-link" href="https://github.com/samhita-alla/github-repository-insights" target="_blank">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                class="tabler-icon tabler-icon-brand-github align-middle">
                <path
                  d="M9 19c-4.3 1.4 -4.3 -2.5 -6 -3m12 5v-3.5c0 -1 .1 -1.4 -.5 -2c2.8 -.3 5.5 -1.4 5.5 -6a4.6 4.6 0 0 0 -1.3 -3.2a4.2 4.2 0 0 0 -.1 -3.2s-1.1 -.3 -3.5 1.3a12.3 12.3 0 0 0 -6.2 0c-2.4 -1.6 -3.5 -1.3 -3.5 -1.3a4.2 4.2 0 0 0 -.1 3.2a4.6 4.6 0 0 0 -1.3 3.2c0 4.6 2.7 5.7 5.5 6c-.6 .6 -.6 1.2 -.5 2v3.5">
                </path>
              </svg>
              <span class="align-middle ms-1">Source Code</span>
            </a>
          </li>
        </ul>
      </div>
      <div v-if="alertVisible" class="position-fixed top-0 end-0 p-3">
        <div class="alert alert-success alert-dismissible fade show" role="alert">
          <strong>Success!</strong> You have successfully updated your access token.
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" @click="alertHide"></button>
        </div>
      </div>
    </nav>
  </div>
  <div class="container px-5">
    <main>
      <!-- Modal -->
      <div id="accessTokenModal" class="modal fade" style="text-align: left !important;" tabindex="-1"
        aria-labelledby="accessTokenModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 id="accessTokenModalLabel" class="modal-title">Access Token</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <h4>🔑 Enter your GitHub access token</h4>
              <p>Your access token is stored locally on your browser and sent securely to the configured backend.</p>
              <div class="mb-3">
                <label for="access-token" class="col-form-label">Access Token</label>
                <input id="access-token" v-model="accessToken" type="password" class="form-control"
                  placeholder="xxxxxxxxxxxxxxxx">
              </div>
              <p>
                → Obtain your access token by visiting
                <a href="https://github.com/settings/tokens/new" target="_blank">GitHub</a>. No
                scope is required.
              </p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              <button type="button" class="btn btn-dark" data-bs-dismiss="modal" @click="storeAccessToken">
                Save changes
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="py-5 text-center">
        <h1>GitHub Repository Insights</h1>
        <p class="lead">
          Generate real-time GitHub insights for your open-source projects and stay informed on how your
          project is progressing.
        </p>
      </div>
      <!-- START FORM -->
      <form class="mb-5" @submit.prevent="submit">
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
            <input id="openissuegrowth-checkbox" v-model="form.openIssueGrowthCheck" class="form-check-input"
              type="checkbox" value="" />
            <label class="form-check-label" for="openissuegrowth-checkbox">
              Open Issue/Pull Request Growth
            </label>
          </div>
          <div v-if="form.openIssueGrowthCheck" class="form-check form-check-inline">
            <input id="issueoverview-checkbox" v-model="form.issueTable" class="form-check-input" type="checkbox"
              value="" />
            <label class="form-check-label" for="issueoverview-checkbox">
              Issue Overview
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input id="closedissuegrowth-checkbox" v-model="form.closedIssueGrowthCheck" class="form-check-input"
              type="checkbox" value="" />
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

        <div>
          <button type="submit" class="btn btn-dark" :disabled="
            starGrowthProgress || openIssueGrowthProgress || closedIssueGrowthProgress || contributorGrowthProgress || !allowSubmit
          ">
            View Graph
          </button>
          <svg id="coldstarticon" aria-describedby="tooltip" class="align-middle ms-2" fill="currentColor" version="1.1"
            xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="18px" height="18px"
            viewBox="0 0 490.318 490.318" xml:space="preserve">
            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
            <g id="SVGRepo_iconCarrier">
              <g>
                <g>
                  <g>
                    <path
                      d="M245.148,0C109.967,0,0.009,109.98,0.009,245.162c0,135.182,109.958,245.156,245.139,245.156 c135.186,0,245.162-109.978,245.162-245.156C490.31,109.98,380.333,0,245.148,0z M245.148,438.415 c-106.555,0-193.234-86.698-193.234-193.253c0-106.555,86.68-193.258,193.234-193.258c106.559,0,193.258,86.703,193.258,193.258 C438.406,351.717,351.706,438.415,245.148,438.415z">
                    </path>
                    <path
                      d="M270.036,221.352h-49.771c-8.351,0-15.131,6.78-15.131,15.118v147.566c0,8.352,6.78,15.119,15.131,15.119h49.771 c8.351,0,15.131-6.77,15.131-15.119V236.471C285.167,228.133,278.387,221.352,270.036,221.352z">
                    </path>
                    <path
                      d="M245.148,91.168c-24.48,0-44.336,19.855-44.336,44.336c0,24.484,19.855,44.34,44.336,44.34 c24.485,0,44.342-19.855,44.342-44.34C289.489,111.023,269.634,91.168,245.148,91.168z">
                    </path>
                  </g>
                </g>
              </g>
            </g>
          </svg>
          <div id="tooltip" role="tooltip">
            Please note that the cold start time may take around 1 minute.
            <div id="arrow" data-popper-arrow></div>
          </div>
        </div>
      </form>
      <!-- END FORM -->
      <!-- START STAR GROWTH UI -->
      <MetricComponentContainer v-model:otherGithubApi="otherGithubApiStarGrowth" :chart-data="starGrowthChartData"
        :growth-error="starGrowthError" :growth-progress="starGrowthProgress" :is-add-repo="isAddRepoStarGrowth"
        :time-delta-frequency="timeDeltaStr" heading="stargrowth" title="Star Growth" label="Stars"
        @add-repo-growth="addRepoGrowth" @remove-tag="removeTag" @growth-error-button="starGrowthErrorButton">
      </MetricComponentContainer>
      <!-- END STAR GROWTH UI -->
      <!-- START OPEN ISSUE/PR GROWTH UI -->
      <MetricComponentContainer v-model:otherGithubApi="otherGithubApiOpenIssueGrowth"
        :chart-data="openIssueGrowthChartData" :growth-error="openIssueGrowthError"
        :growth-progress="openIssueGrowthProgress" :is-add-repo="isAddRepoOpenIssueGrowth" :issue-table="issueTable"
        :time-delta-frequency="timeDeltaStr" heading="openissuegrowth" title="Open Issue/Pull Request Growth"
        label="Open Issues/PRs" @add-repo-growth="addRepoGrowth" @growth-error-button="openIssueGrowthErrorButton"
        @remove-tag="removeTag">
      </MetricComponentContainer>
      <!-- END OPEN ISSUE/PR GROWTH UI -->
      <!-- START CLOSED ISSUE/PR GROWTH UI -->
      <MetricComponentContainer v-model:otherGithubApi="otherGithubApiClosedIssueGrowth"
        :chart-data="closedIssueGrowthChartData" :growth-error="closedIssueGrowthError"
        :growth-progress="closedIssueGrowthProgress" :is-add-repo="isAddRepoClosedIssueGrowth"
        :time-delta-frequency="timeDeltaStr" heading="closedissuegrowth" title="Closed Issue/Pull Request Growth"
        label="Closed Issues/PRs" @add-repo-growth="addRepoGrowth" @growth-error-button="closedIssueGrowthErrorButton"
        @remove-tag="removeTag">
      </MetricComponentContainer>
      <!-- END CLOSED ISSUE/PR GROWTH UI -->
      <!-- START CONTRIBUTOR GROWTH UI -->
      <MetricComponentContainer v-model:otherGithubApi="otherGithubApiContributorGrowth"
        :chart-data="contributorGrowthChartData" :growth-error="contributorGrowthError"
        :growth-progress="contributorGrowthProgress" :is-add-repo="isAddRepoContributorGrowth"
        :time-delta-frequency="timeDeltaStr" heading="contributorgrowth" title="Contributor Growth" label="Contributors"
        @add-repo-growth="addRepoGrowth" @growth-error-button="contributorGrowthErrorButton" @remove-tag="removeTag">
      </MetricComponentContainer>
      <!-- END CONTRIBUTOR GROWTH UI -->
    </main>
  </div>
</template>

<script>
import axios from "axios";
import MetricComponentContainer from "../components/MetricComponent.vue";
import { createPopper } from '@popperjs/core';

var converter = require("number-to-words");

export default {
  name: "HomeView",
  components: { MetricComponentContainer },
  data() {
    return {
      form: {
        githubApi: "flyteorg/flyte",
        timeDelta: 7,
        timeDeltaFrequency: 2,
        starGrowthCheck: true,
        openIssueGrowthCheck: false,
        closedIssueGrowthCheck: false,
        contributorGrowthCheck: false,
        issueTable: null,
      },
      accessToken: "",
      alertVisible: false,
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
    if (this.form.timeDeltaFrequency) {
      this.timeDeltaStr = converter.toWords(this.form.timeDeltaFrequency);
    }
    this.accessToken = localStorage.getItem("accessToken") || "";

    // popover start
    const coldstarticon = document.querySelector('#coldstarticon');
    const tooltip = document.querySelector('#tooltip');

    const popperInstance = createPopper(coldstarticon, tooltip, {
      placement: 'right',
      modifiers: [
        {
          name: 'offset',
          options: {
            offset: [0, 8],
          },
        },
      ],
    });

    function show() {
      // Make the tooltip visible
      tooltip.setAttribute('data-show', '');

      // Enable the event listeners
      popperInstance.setOptions((options) => ({
        ...options,
        modifiers: [
          ...options.modifiers,
          { name: 'eventListeners', enabled: true },
        ],
      }));

      // Update its position
      popperInstance.update();
    }

    function hide() {
      // Hide the tooltip
      tooltip.removeAttribute('data-show');

      // Disable the event listeners
      popperInstance.setOptions((options) => ({
        ...options,
        modifiers: [
          ...options.modifiers,
          { name: 'eventListeners', enabled: false },
        ],
      }));
    }

    const showEvents = ['mouseenter', 'focus'];
    const hideEvents = ['mouseleave', 'blur'];

    showEvents.forEach((event) => {
      coldstarticon.addEventListener(event, show);
    });

    hideEvents.forEach((event) => {
      coldstarticon.addEventListener(event, hide);
    });
    // popover end
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
            params["issue_overview"] =
              this.form[this.entity_mapping[key].issuetable];
          }
          var headers = this.accessToken ? { 'Authorization': 'Bearer ' + this.accessToken } : null;
          axios
            .get("/" + key, {
              headers: headers,
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
      var headers = this.accessToken ? { 'Authorization': 'Bearer ' + this.accessToken } : null;
      axios
        .get("/" + entity, {
          headers: headers,
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
    storeAccessToken: function () {
      localStorage.setItem("accessToken", this.accessToken);
      this.alertShow();
    },
    alertShow() {
      this.alertVisible = true;
      setTimeout(() => {
        this.alertHide();
      }, 3000); // hide the alert after 5 seconds (5000ms)
    },
    alertHide() {
      this.alertVisible = false;
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


<style>
#tooltip {
  background-color: #333;
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 13px;
  display: none;
}

#tooltip[data-show] {
  display: block;
}

#arrow,
#arrow::before {
  position: absolute;
  width: 8px;
  height: 8px;
  background: inherit;
}

#arrow {
  visibility: hidden;
}

#arrow::before {
  visibility: visible;
  content: '';
  transform: rotate(45deg);
}

#tooltip[data-popper-placement^='right']>#arrow {
  left: -4px;
}
</style>