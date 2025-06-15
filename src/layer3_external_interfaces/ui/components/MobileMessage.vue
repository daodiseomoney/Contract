<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 flex items-center justify-center p-4">
    <div class="max-w-md w-full">
      <!-- Logo and Branding -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-violet-400 to-purple-600 rounded-2xl flex items-center justify-center">
          <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
            <span class="text-violet-600 font-bold text-sm">D</span>
          </div>
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">DAODISEO</h1>
        <p class="text-violet-300 text-lg font-medium">Real Estate Tokenization ai-dApp</p>
      </div>

      <!-- Mobile Message Card -->
      <div class="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-2xl">
        <div class="text-center mb-6">
          <div class="w-12 h-12 mx-auto mb-4 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center">
            <FeatherIcon name="monitor" class="w-6 h-6 text-white" />
          </div>
          <h2 class="text-xl font-semibold text-white mb-3">Best Experience on Desktop</h2>
          <p class="text-gray-300 leading-relaxed">
            For the best experience with BIM models and blockchain workflows, please access DAODISEO on desktop.
          </p>
        </div>

        <!-- Features that require desktop -->
        <div class="space-y-3 mb-6">
          <div class="flex items-center space-x-3">
            <div class="w-2 h-2 bg-violet-400 rounded-full"></div>
            <span class="text-gray-300 text-sm">3D BIM model visualization</span>
          </div>
          <div class="flex items-center space-x-3">
            <div class="w-2 h-2 bg-violet-400 rounded-full"></div>
            <span class="text-gray-300 text-sm">Keplr wallet integration</span>
          </div>
          <div class="flex items-center space-x-3">
            <div class="w-2 h-2 bg-violet-400 rounded-full"></div>
            <span class="text-gray-300 text-sm">Smart contract signing</span>
          </div>
        </div>

        <!-- CTA Button -->
        <button 
          @click="openDesktopVersion"
          class="w-full bg-gradient-to-r from-violet-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-xl hover:from-violet-600 hover:to-purple-700 transition-all duration-200 shadow-lg"
        >
          Open on Desktop
        </button>

        <!-- Coming Soon -->
        <div class="text-center mt-4 pt-4 border-t border-white/10">
          <p class="text-violet-300 text-sm">Mobile optimization coming soon</p>
        </div>
      </div>

      <!-- Quick Stats Preview -->
      <div class="mt-6 grid grid-cols-2 gap-4">
        <div class="bg-white/5 backdrop-blur-sm rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-white">${{ metrics.odisPrice }}</div>
          <div class="text-violet-300 text-sm">ODIS Price</div>
        </div>
        <div class="bg-white/5 backdrop-blur-sm rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-white">{{ metrics.blockHeight.toLocaleString() }}</div>
          <div class="text-violet-300 text-sm">Block Height</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import FeatherIcon from './FeatherIcon.vue'

const metrics = ref({
  odisPrice: '4.85',
  blockHeight: 3483091
})

const openDesktopVersion = () => {
  // Open current URL in new tab with desktop user agent hint
  window.open(window.location.href, '_blank')
}

const fetchLiveMetrics = async () => {
  try {
    const response = await fetch('/api/metrics')
    if (response.ok) {
      const data = await response.json()
      if (data.status === 'success') {
        metrics.value = {
          odisPrice: data.data.odis_token.price_usd,
          blockHeight: data.data.network_health.block_height
        }
      }
    }
  } catch (error) {
    console.warn('Mobile metrics fetch failed:', error)
  }
}

onMounted(() => {
  fetchLiveMetrics()
})
</script>