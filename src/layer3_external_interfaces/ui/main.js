import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import feather from 'feather-icons'
import App from './App.vue'
import './style.css'

// Import components
import Dashboard from './components/Dashboard.vue'
import Upload from './components/Upload.vue'
import Viewer from './components/Viewer.vue'
import Broadcast from './components/Broadcast.vue'
import Contracts from './components/Contracts.vue'
import FeatherIcon from './components/FeatherIcon.vue'

// Define routes
const routes = [
  { path: '/', component: Dashboard },
  { path: '/upload', component: Upload },
  { path: '/viewer', component: Viewer },
  { path: '/viewer/:id', name: 'Viewer', component: Viewer },
  { path: '/broadcast', component: Broadcast },
  { path: '/contracts', component: Contracts }
]

// Create router instance
const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// Create and mount Vue app
const app = createApp(App)
app.use(router)

// Register FeatherIcon component globally
app.component('FeatherIcon', FeatherIcon)

// Mount the app and ensure proper initialization
const mountedApp = app.mount('#app')

// Initialize Feather icons after Vue mounts using bundled library
setTimeout(() => {
  feather.replace()
  console.log('DAODISEO Vue app mounted successfully')
}, 100)