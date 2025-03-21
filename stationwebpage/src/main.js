//Bootstrap
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';


import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router/router';

const app = createApp(App);
app.use(createPinia()); // Instalar Pinia
app.use(router);
app.mount('#app');
