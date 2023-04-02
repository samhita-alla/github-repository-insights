import "bootstrap/dist/css/bootstrap.css";
import "bootstrap/dist/js/bootstrap.min.js";
import axios from "axios";
import * as Vue from "vue";

import App from "./App.vue";
import router from "./router";

axios.defaults.withCredentials = true;
axios.defaults.baseURL = process.env.FASTAPI_URL; // the FastAPI backend

Vue.createApp(App).use(router).mount("#app");
