import "bootstrap/dist/css/bootstrap.css";
import "bootstrap/dist/js/bootstrap.min.js";
import axios from "axios";
import * as Vue from "vue";
import VueCookies from 'vue-cookies';

import App from "./App.vue";
import router from "./router";

Vue.use(VueCookies);

axios.defaults.withCredentials = true;
axios.defaults.baseURL = process.env.VUE_APP_FASTAPI_URL; // the FastAPI backend

Vue.createApp(App).use(router).mount("#app");
