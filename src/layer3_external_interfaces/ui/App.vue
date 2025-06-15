<template>
  <!-- Mobile Detection and Desktop-Only Message -->
  <div class="block md:hidden min-h-screen bg-gradient-to-br from-[#0a0a0f] via-[#1a1a2e] to-[#16213e] flex items-center justify-center p-4">
    <div class="max-w-sm w-full space-y-6">
      <!-- Main Message Card -->
      <div class="glass-container rounded-2xl border border-violet-500/30 p-6 text-center">
        <div class="text-violet-400 font-bold text-2xl mb-2">DAODISEO</div>
        <div class="text-white text-lg mb-4">Real Estate Tokenization ai-dApp</div>
        <div class="text-gray-300 text-sm mb-6 leading-relaxed">
          For the best experience with BIM models and blockchain workflows, please access DAODISEO on desktop.
        </div>
        <div class="text-violet-400 text-xs">
          Mobile optimization coming soon
        </div>
      </div>

      <!-- Live Market Data Preview -->
      <div class="glass-container rounded-xl border border-violet-500/20 p-4">
        <div class="text-white text-sm font-medium mb-3 text-center">Live ODIS Market</div>
        <div class="grid grid-cols-2 gap-4">
          <div class="text-center">
            <div class="text-xl font-bold text-green-400" id="mobile-price">$4.85</div>
            <div class="text-xs text-gray-400">Price USD</div>
          </div>
          <div class="text-center">
            <div class="text-xl font-bold text-blue-400" id="mobile-change">+2.3%</div>
            <div class="text-xs text-gray-400">24h Change</div>
          </div>
        </div>
      </div>

      <!-- Trust Indicators for Landlords -->
      <div class="glass-container rounded-xl border border-violet-500/20 p-4">
        <div class="text-white text-sm font-medium mb-3 text-center">Platform Security</div>
        <div class="space-y-2">
          <div class="flex items-center justify-between text-xs">
            <span class="text-gray-400">Network Status</span>
            <span class="text-green-400 font-medium">Active</span>
          </div>
          <div class="flex items-center justify-between text-xs">
            <span class="text-gray-400">Validators</span>
            <span class="text-blue-400 font-medium">125+</span>
          </div>
          <div class="flex items-center justify-between text-xs">
            <span class="text-gray-400">Blockchain</span>
            <span class="text-violet-400 font-medium">Cosmos</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Desktop Layout - Mobile-inspired Deep Purple Gradient -->
  <div class="hidden md:flex h-screen bg-gradient-to-br from-[#190033] via-[#3a0ca3] to-[#1a0033] p-4">
    <!-- Unified App Frame with Mobile-style Glow -->
    <div class="app-frame relative border-2 border-[#e242ff]/40 rounded-xl flex flex-col w-full h-full overflow-hidden shadow-[0_0_40px_rgba(226,66,255,0.3)]">
      <!-- Global Header - Mobile-inspired Magenta Glow -->
      <header class="h-20 px-8 flex items-center justify-between backdrop-blur-xl bg-black/40 border-b border-[#e242ff]/30 shadow-[0_2px_20px_rgba(226,66,255,0.15)]">
        <div class="daodiseo-logo flex items-center space-x-3">
          <img :src="logoUrl" alt="DAODISEO" class="w-10 h-10" />
          <div class="daodiseo-logo-text">DAODISEO</div>
          <div class="daodiseo-logo-app">.APP</div>
        </div>
        <div class="flex items-center space-x-4">
          <!-- ODIS Balance with Claim Feature -->
          <div 
            @click="claimOdis" 
            class="odis-balance-container relative transition-all cursor-pointer"
            :class="{ 'odis-claimed': odisClaimed, 'odis-pulsing': !odisClaimed }"
            @mouseenter="showOdisTooltip = true"
            @mouseleave="showOdisTooltip = false"
          >
            <div class="bg-[#ffd200] text-black px-6 py-2 rounded-lg font-bold text-base relative overflow-hidden shadow-[0_0_20px_rgba(255,210,0,0.4)]">
              {{ odisBalance }} ODIS
              <div v-if="odisProgress < 100" class="odis-progress-ring absolute inset-0 border-2 border-[#ffb700] rounded-lg opacity-60 animate-pulse"></div>
            </div>
            
            <!-- Action-price tooltip -->
            <div v-if="showOdisTooltip" class="odis-tooltip absolute top-full right-0 mt-2 bg-black/90 backdrop-blur-xl border border-violet-500/30 rounded-lg p-3 text-sm whitespace-nowrap z-50">
              <div class="tooltip-item text-gray-300 mb-1">Analyze BIM · 2 ODIS</div>
              <div class="tooltip-item text-gray-300 mb-1">Broadcast Tx · 5 ODIS</div>
              <div class="tooltip-item text-gray-300">Smart Contract · 3 ODIS</div>
            </div>
          </div>

          <!-- Keplr Wallet Connection with Mobile-inspired Colors -->
          <button 
            @click="connectWallet" 
            class="keplr-button px-6 py-2 rounded-lg font-medium transition-all hover:scale-105"
            :class="walletConnected ? 'bg-green-500 hover:bg-green-600 text-white shadow-[0_0_15px_rgba(34,197,94,0.4)]' : 'bg-[#5c3bff] hover:bg-[#4c31d9] text-white shadow-[0_0_15px_rgba(92,59,255,0.4)]'"
          >
            <span v-if="!walletConnected">Connect Keplr</span>
            <span v-else class="flex items-center space-x-2">
              <div class="w-2 h-2 bg-green-300 rounded-full animate-pulse"></div>
              <span>{{ truncatedAddress }}</span>
            </span>
          </button>
        </div>
      </header>

      <!-- Main Content Container - Full Viewport -->
      <div class="flex-1 flex overflow-hidden">
        <!-- Sidebar Navigation - Mobile-inspired Glass -->
        <aside class="w-24 bg-black/30 backdrop-blur-xl border-r border-[#e242ff]/30 flex flex-col items-center py-8 space-y-8 shadow-[2px_0_20px_rgba(226,66,255,0.1)]">
          <!-- Navigation Icons -->
          <nav class="flex flex-col space-y-8">
            <router-link to="/" class="sidebar-icon-glass" :class="{ 'sidebar-icon-active-glass': $route.path === '/' }">
              <FeatherIcon name="grid" class="w-7 h-7" />
            </router-link>
            <router-link to="/upload" class="sidebar-icon-glass" :class="{ 'sidebar-icon-active-glass': $route.path === '/upload' }">
              <FeatherIcon name="upload" class="w-7 h-7" />
            </router-link>
            <router-link to="/viewer" class="sidebar-icon-glass" :class="{ 'sidebar-icon-active-glass': $route.path === '/viewer' }">
              <FeatherIcon name="eye" class="w-7 h-7" />
            </router-link>
            <router-link to="/broadcast" class="sidebar-icon-glass" :class="{ 'sidebar-icon-active-glass': $route.path === '/broadcast' }">
              <FeatherIcon name="radio" class="w-7 h-7" />
            </router-link>
            <router-link to="/contracts" class="sidebar-icon-glass" :class="{ 'sidebar-icon-active-glass': $route.path === '/contracts' }">
              <FeatherIcon name="layers" class="w-7 h-7" />
            </router-link>
          </nav>
        </aside>

        <!-- Main Content Area - Fixed Height -->
        <main class="flex-1 flex flex-col overflow-hidden">
          <div class="flex-1 p-8 overflow-hidden">
            <router-view />
          </div>
        </main>
      </div>

      <!-- Footer - Mobile-inspired Dynamic Testnet Badge -->
      <footer class="h-16 px-8 flex items-center justify-center backdrop-blur-xl bg-black/40 border-t border-[#e242ff]/30 shadow-[0_-2px_20px_rgba(226,66,255,0.1)]">
        <div class="flex items-center space-x-2 text-sm text-gray-400">
          <span>© 2025 DAODISEO</span>
          <span class="text-gray-600">·</span>
          <a href="https://daodiseo.money/whitepaper/" target="_blank" class="hover:text-[#8F43E9] transition-colors">
            Whitepaper
          </a>
          <span class="text-gray-600">·</span>
          <a href="#" class="hover:text-[#8F43E9] transition-colors">
            daoDAO Governance
          </a>
          <span class="text-gray-600">·</span>
          <div class="flex items-center space-x-2">
            <div 
              class="w-2 h-2 rounded-full transition-colors"
              :class="walletConnected ? 'bg-green-400 animate-pulse' : 'bg-orange-400'"
            ></div>
            <span 
              class="font-medium transition-colors"
              :class="walletConnected ? 'text-green-400' : 'text-orange-400'"
            >
              {{ testnetStatus }}
            </span>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import FeatherIcon from './components/FeatherIcon.vue'
import logoImage from './src/assets/DAO_O_transparent.png'

// Use authentic DAO logo
const logoUrl = logoImage

// Reactive state for landlord value features
const walletConnected = ref(false)
const walletAddress = ref('')
const odisBalance = ref(10) // Start with 10 ODIS welcome bonus
const odisClaimed = ref(false)
const odisProgress = ref(0)
const showOdisTooltip = ref(false)
const showUnlockReward = ref(false)

// Computed properties
const truncatedAddress = computed(() => {
  if (!walletAddress.value) return ''
  return `${walletAddress.value.slice(0, 6)}...${walletAddress.value.slice(-4)}`
})

const testnetStatus = computed(() => {
  return walletConnected.value ? 'Odiseo Connected' : 'Odiseo Testnet'
})

// Landlord value functions
const claimOdis = () => {
  if (!odisClaimed.value) {
    odisClaimed.value = true
    odisBalance.value = 10
    odisProgress.value = 25 // First milestone
    
    // Show instant gratification
    const toast = document.createElement('div')
    toast.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce'
    toast.textContent = '🎉 Claimed 10 ODIS! Your first on-chain asset.'
    document.body.appendChild(toast)
    
    setTimeout(() => {
      toast.remove()
    }, 3000)
    
    // Check for dual-button combo reward
    checkComboReward()
  }
}

const connectWallet = async () => {
  try {
    if (!window.keplr) {
      alert('Please install Keplr extension to connect your wallet')
      window.open('https://www.keplr.app/', '_blank')
      return
    }
    
    const chainId = "osmo-test-5" // Odiseo testnet
    await window.keplr.enable(chainId)
    
    const offlineSigner = window.getOfflineSigner(chainId)
    const accounts = await offlineSigner.getAccounts()
    
    if (accounts.length > 0) {
      walletConnected.value = true
      walletAddress.value = accounts[0].address
      
      // Store connection state
      localStorage.setItem('keplr_connected', 'true')
      localStorage.setItem('wallet_address', accounts[0].address)
      
      console.log('Wallet connected:', accounts[0].address)
      
      // Reward user with progress
      odisProgress.value = Math.max(odisProgress.value, 50)
      
      // Check for dual-button combo reward
      checkComboReward()
    }
  } catch (error) {
    console.error('Wallet connection failed:', error)
    alert('Failed to connect wallet. Please try again.')
  }
}

const checkComboReward = () => {
  if (odisClaimed.value && walletConnected.value && !showUnlockReward.value) {
    showUnlockReward.value = true
    
    // Show combo reward toast
    setTimeout(() => {
      const toast = document.createElement('div')
      toast.className = 'fixed top-4 right-4 bg-purple-600 text-white px-6 py-4 rounded-lg shadow-lg z-50 max-w-sm'
      toast.innerHTML = `
        <div class="font-bold mb-1">🔓 Unlocked: Free AI Analysis</div>
        <div class="text-sm opacity-90">2 ODIS saved! Wallet + ODIS = Platform perks</div>
      `
      document.body.appendChild(toast)
      
      setTimeout(() => {
        toast.remove()
      }, 5000)
    }, 1000)
  }
}

// Initialize from localStorage
onMounted(() => {
  const savedConnection = localStorage.getItem('keplr_connected')
  const savedAddress = localStorage.getItem('wallet_address')
  
  if (savedConnection === 'true' && savedAddress) {
    walletConnected.value = true
    walletAddress.value = savedAddress
    odisProgress.value = 50
  }
  
  // Pulse animation for unclaimed ODIS
  if (!odisClaimed.value) {
    setInterval(() => {
      const pill = document.querySelector('.odis-pulsing')
      if (pill) {
        pill.style.transform = 'scale(1.05)'
        setTimeout(() => {
          pill.style.transform = 'scale(1)'
        }, 200)
      }
    }, 2000)
  }
})

// Mobile data fetching for landlord trust indicators
const updateMobileData = async () => {
  try {
    const response = await fetch('/api/metrics')
    if (response.ok) {
      const data = await response.json()
      if (data.status === 'success') {
        const apiData = data.data
        // Update mobile price display
        const priceEl = document.getElementById('mobile-price')
        const changeEl = document.getElementById('mobile-change')
        if (priceEl) priceEl.textContent = `$${parseFloat(apiData.odis_token.price_usd).toFixed(2)}`
        if (changeEl) changeEl.textContent = `+${parseFloat(apiData.odis_token.price_change_24h).toFixed(1)}%`
      }
    }
  } catch (error) {
    console.warn('Mobile data fetch failed:', error)
  }
}

onMounted(() => {
  console.log('DAODISEO Vue app mounted successfully')
  // Update mobile data every 30 seconds for landlord confidence
  updateMobileData()
  setInterval(updateMobileData, 30000)
})
</script>

<style scoped>
/* Enhanced landlord value features styling */
.odis-pulsing {
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0%, 100% { 
    transform: scale(1);
    box-shadow: 0 0 20px rgba(250, 204, 21, 0.3);
  }
  50% { 
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(250, 204, 21, 0.6);
  }
}

.odis-claimed {
  transform: scale(1);
  animation: none;
}

.odis-tooltip {
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 92, 246, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.tooltip-item {
  font-size: 0.75rem;
  color: rgb(209, 213, 219);
  margin-bottom: 0.25rem;
}

.tooltip-item:last-child {
  margin-bottom: 0;
}

.keplr-button {
  position: relative;
  overflow: hidden;
}

.keplr-connected {
  background: linear-gradient(135deg, #059669, #047857);
  box-shadow: 0 0 20px rgba(5, 150, 105, 0.3);
}

.keplr-disconnected {
  background: linear-gradient(135deg, #8B5CF6, #7C3AED);
}

.keplr-button:hover {
  transform: scale(1.05);
  transition: all 0.3s ease;
}

/* Enhanced logo styling */
.daodiseo-logo {
  display: flex;
  align-items: center;
  space: 0.75rem;
}

.daodiseo-logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  letter-spacing: -0.025em;
}

.daodiseo-logo-app {
  font-size: 1.5rem;
  font-weight: 700;
  color: rgb(139, 92, 246);
  letter-spacing: -0.025em;
}

/* Sidebar icon enhancements */
.sidebar-icon-glass {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  color: rgb(196, 181, 253);
  transition: all 0.3s ease;
  text-decoration: none;
}

.sidebar-icon-glass:hover {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.4);
  color: white;
  transform: scale(1.1);
}

.sidebar-icon-active-glass {
  background: rgba(139, 92, 246, 0.3);
  border-color: rgba(139, 92, 246, 0.6);
  color: white;
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}

/* Glass container styling */
.glass-container {
  background: rgba(10, 10, 15, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 92, 246, 0.3);
}

/* App frame styling */
.app-frame {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

/* Progress ring styling */
.odis-progress-ring {
  border: 2px solid rgba(250, 204, 21, 0.3);
  border-top-color: rgba(250, 204, 21, 0.8);
  animation: spin 2s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Mobile responsive adjustments */
@media (max-width: 768px) {
  .daodiseo-logo-text,
  .daodiseo-logo-app {
    font-size: 1.25rem;
  }
  
  .odis-balance-container {
    margin-right: 0.5rem;
  }
  
  .keplr-button {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }
}
</style>

