<template>
  <div v-if="chartData || growthError || growthProgress" class="card my-5">
    <div :id="'heading'" class="card-header">
      <h5 class="mb-0">{{ title }}</h5>
    </div>
    <div>
      <div v-if="chartData && chartData.datasets.length >= 1" class="my-5">
        <img :src="imgSrc" role="button" class="d-block mx-auto mb-3" @click="mutableIsAddRepo = !mutableIsAddRepo" />
        <small>To add a new repo, click on the + button.</small>
      </div>
      <div v-if="mutableIsAddRepo" class="card mx-3">
        <div class="card-body">
          <form @submit.prevent="$emit('addRepoGrowth', heading)">
            <div class="form-group mb-3">
              <label :for="'other-github-api-' + heading">GitHub Repo</label>
              <input :id="'other-github-api-' + heading" type="text" class="form-control" placeholder="flyteorg/flyte"
                :value="otherGithubApi" :disabled="chartData && chartData.datasets.length >= 5" required
                @input="$emit('update:otherGithubApi', $event.target.value)" />
              <small class="form-text text-muted">GitHub Repo has to be of the format {organization/repo}.</small>
            </div>
            <div class="form-group mb-3">
              <label for="other-access-token">Access Token</label>
              <input id="other-access-token" type="text" class="form-control"
                :disabled="chartData && chartData.datasets.length >= 2"
                @input="$emit('update:otherAccessToken', $event.target.value)" />
              <small class="form-text text-muted">Useful to circumvent the rate limit issue.</small>
            </div>
            <button type="submit" class="btn btn-primary" :disabled="
              (chartData && chartData.datasets.length >= 5) || growthProgress
            ">
              Add repository
            </button>
          </form>
        </div>
      </div>
      <div :aria-labelledby="'heading'">
        <div class="card-body">
          <div v-if="chartData && chartData.datasets.length > 1" class="mt-3">
            <span v-for="(dataset, index) in chartData.datasets" :key="dataset.label">
              <div v-if="index != 0" class="btn btn-sm btn-secondary remove-tag-btn me-2" @click="$emit('removeTag',
                index, heading)">
                <span>x</span>
                {{ dataset.label }}
              </div>
            </span>
          </div>
          <div class="my-5">
            <p v-if="growthProgress" id="progress-label">
              ⭐️ Crunching GitHub APIs ⭐️
            </p>
            <div v-if="growthProgress" class="progress">
              <div :id="heading + '-progress'" class="progress-bar" role="progressbar" style="width: 0%">
                0%
              </div>
            </div>
          </div>
          <div v-if="chartData && chartData.datasets.length >= 5"
            class="alert alert-warning alert-dismissible fade show d-flex align-items-center" role="alert">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor"
              class="bi bi-exclamation-triangle-fill flex-shrink-0 me-2" viewBox="0 0 16 16" role="img"
              aria-label="Warning:">
              <path
                d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z" />
            </svg>
            No more than 5 repositories can be added. Please remove a repository
            to continue.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
          </div>
          <div v-if="growthError" class="my-5 alert alert-warning alert-dismissible d-flex align-items-center"
            :class="growthError ? 'show' : 'fade'" role="alert">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor"
              class="bi bi-exclamation-triangle-fill flex-shrink-0 me-2" viewBox="0 0 16 16" role="img"
              aria-label="Warning:">
              <path
                d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z" />
            </svg>
            {{ growthError }}
            <button type="button" class="btn-close" aria-label="Close" @click="$emit('growthErrorButton')"></button>
          </div>
          <div v-if="chartData" :id="heading + '-result'" class="row justify-content-center">
            <div class="chart-container col-md-10 col-sm-12">
              <h3>
                {{ title }} observed over {{ timedeltaf }} {{ $parent.form.timeDelta }}-day periods.
              </h3>
              <BarChartContainer :chart-component-data="chartData" :label="label"></BarChartContainer>
              <div v-if="issueTable" id="openissuegrowth-table" class="card row justify-content-center my-5">
                <div class="flex h-screen table-wrapper">
                  <table class="table m-auto">
                    <thead class="sticky-top bg-white">
                      <tr>
                        <th>
                          Recently Addressed Issues ({{ issueTable.addressed.length }})
                        </th>
                        <th>
                          New Unaddressed Issues ({{
                            issueTable.unaddressed.length
                          }})
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td class="text-left">
                          <ul class="list-group">
                            <a v-for="(value, index) in issueTable.addressed" :key="index" class="list-group-item"
                              :href="value.url">
                              {{ value.title }}
                            </a>
                          </ul>
                        </td>
                        <td class="text-left">
                          <ul class="list-group">
                            <a v-for="(value, index) in issueTable.unaddressed" :key="index" class="list-group-item"
                              :href="value.url">
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
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BarChartContainer from "./ChartComponent.vue";

var converter = require("number-to-words");

export default {
  name: "SubComponentContainer",
  components: { BarChartContainer },
  props: {
    chartData: { type: [Object, null], required: true },
    growthError: { type: String, required: true },
    growthProgress: { type: [Boolean, null], required: true },
    imgSrc: { type: String, required: true },
    isAddRepo: { type: Boolean, required: true },
    heading: { type: String, required: true },
    title: { type: String, required: true },
    label: { type: String, required: true },
    otherGithubApi: { type: String, required: true },
    issueTable: { type: Boolean, required: false },
    timeDeltaFrequency: { type: Number, required: true }
  },
  emits: ["update:otherGithubApi", "addRepoGrowth", "removeTag", "update:otherAccessToken", "growthErrorButton"],
  data() {
    return {
      mutableIsAddRepo: this.isAddRepo,
      timedeltaf: "",
    };
  },
  mounted() {
    this.timedeltaf = converter.toWords(this.timeDeltaFrequency);
  }
};
</script>

<style>
.chart-container {
  position: relative;
  margin: auto;
}

.remove-tag-btn:hover {
  text-decoration: line-through;
}

.table-wrapper {
  max-height: 500px;
  overflow: auto;
  display: inline-block;
}
</style>
