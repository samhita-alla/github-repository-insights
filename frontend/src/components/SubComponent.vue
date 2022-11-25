<template>
  <div class="card my-5" v-if="chartData || growthError || growthProgress">
    <div class="card-header" :id="'heading'">
      <h5 class="mb-0">Star Growth</h5>
    </div>
    <div>
      <div class="my-5" v-if="chartData && chartData.datasets.length >= 1">
        <img
          :src="imgSrc"
          @click="mutableIsAddRepo = !mutableIsAddRepo"
          role="button"
          class="d-block mx-auto mb-3"
        />
        <small>To add a new repo, click on the + button.</small>
      </div>
      <div class="card mx-3" v-if="mutableIsAddRepo">
        <div class="card-body">
          <form @submit.prevent="addRepoGrowth((entity = 'stargrowth'))">
            <div class="form-group mb-3">
              <label :for="other - github - api - +'heading'"
                >GitHub Repo</label
              >
              <input
                type="text"
                class="form-control"
                :id="other - github - api - +'heading'"
                placeholder="flyteorg/flyte"
                :value="otherGithubApi"
                @input="$emit('update:otherGithubApi', $event.target.value)"
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
                :disabled="chartData && chartData.datasets.length >= 2"
              />
              <small class="form-text text-muted"
                >Useful to circumvent the rate limit issue.</small
              >
            </div>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="
                (chartData && chartData.datasets.length >= 5) || growthProgress
              "
            >
              Add repository
            </button>
          </form>
        </div>
      </div>
      <div :aria-labelledby="'heading'">
        <div class="card-body">
          <div v-if="chartData && chartData.datasets.length > 1" class="mt-3">
            <span
              v-for="(dataset, index) in chartData.datasets"
              :key="dataset.label"
            >
              <div
                v-if="index != 0"
                class="btn btn-sm btn-secondary remove-tag-btn me-2"
                @click="removeTag(index, 'heading')"
              >
                <span>x</span>
                {{ dataset.label }}
              </div>
            </span>
          </div>
          <div class="my-5">
            <p id="progress-label" v-if="growthProgress">
              ⭐️ Crunching GitHub APIs ⭐️
            </p>
            <div v-if="growthProgress" class="progress">
              <div
                class="progress-bar"
                role="progressbar"
                style="width: 0%"
                :id="'heading' + -progress"
              >
                0%
              </div>
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
            No more than 5 repositories can be added. Please remove a repository
            to continue.
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="alert"
              aria-label="Close"
            ></button>
          </div>
          <div
            v-if="growthError"
            class="my-5 alert alert-warning alert-dismissible d-flex align-items-center"
            :class="growthError ? 'show' : 'fade'"
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
            {{ growthError }}
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
            v-if="chartData"
          >
            <div class="col-md-10 col-sm-12">
              <h3>
                {{ heading }} every {{ form.timeDelta }} days, repeated
                {{ form.timeDeltaFrequency }} times.
              </h3>
              <BarChartContainer
                class="my-5"
                :chart-data="chartData"
                :label="'label'"
              ></BarChartContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "SubComponentContainer",
  props: [
    "chartData",
    "growthError",
    "growthProgress",
    "imgSrc",
    "isAddRepo",
    "heading",
    "label",
    "otherGithubApi",
  ],
  data: function () {
    return {
      mutableIsAddRepo: this.isAddRepo,
    };
  },
};
</script>
