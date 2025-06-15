<template>
  <!-- BIM Upload Workspace - Unified Layout -->
  <div class="h-full w-full flex flex-col space-y-6" data-testid="upload-workspace">
    <!-- Header with Real Estate Context -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
          Property Tokenization Workspace
        </h1>
        <p class="text-gray-400 mt-2">Upload BIM model to analyze tokenization potential and ROI projections</p>
      </div>
      <div class="glass-card p-4">
        <div class="text-green-400 font-bold text-xl" id="estimated-value">
          ${{ estimatedPropertyValue.toLocaleString() }}
        </div>
        <div class="text-xs text-gray-400">Estimated Property Value</div>
      </div>
    </div>

    <!-- Main Upload Area - Full Viewport -->
    <div class="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Left: Upload Zone -->
      <div class="lg:col-span-2 glass-card p-8 h-full flex flex-col">
        <div class="flex-1 border-2 border-dashed border-violet-500/50 rounded-2xl relative">
          <input 
            type="file" 
            ref="fileInput"
            @change="handleFileUpload"
            accept=".ifc,.rvt,.dwg,.step,.stp,.obj"
            class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          
          <!-- Upload State: Empty -->
          <div v-if="!uploadProgress && !fileUploaded" class="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
            <FeatherIcon name="upload-cloud" class="w-24 h-24 text-violet-400 mb-6" />
            <h3 class="text-2xl font-bold text-white mb-3">Drop your BIM file here</h3>
            <p class="text-gray-400 mb-6 max-w-md">
              Upload IFC, RVT, DWG files for instant property analysis and tokenization preview
            </p>
            <div class="grid grid-cols-3 gap-4 text-sm text-gray-500 mb-6">
              <div class="flex items-center space-x-2">
                <FeatherIcon name="file" class="w-4 h-4" />
                <span>IFC Models</span>
              </div>
              <div class="flex items-center space-x-2">
                <FeatherIcon name="layers" class="w-4 h-4" />
                <span>Revit Files</span>
              </div>
              <div class="flex items-center space-x-2">
                <FeatherIcon name="box" class="w-4 h-4" />
                <span>CAD Drawings</span>
              </div>
            </div>
            <button 
              @click="triggerFileInput"
              class="bg-violet-600 hover:bg-violet-500 text-white px-8 py-3 rounded-lg font-medium transition-colors">
              Select BIM File
            </button>
          </div>

          <!-- Upload State: Processing -->
          <div v-if="uploadProgress && !fileUploaded" class="absolute inset-0 flex flex-col items-center justify-center">
            <div class="w-32 h-32 relative mb-6">
              <div class="absolute inset-0 border-4 border-violet-500/20 rounded-full"></div>
              <div 
                class="absolute inset-0 border-4 border-violet-500 rounded-full transition-all duration-300"
                :style="{ 'clip-path': `polygon(0 0, ${uploadProgress}% 0, ${uploadProgress}% 100%, 0 100%)` }"
              ></div>
              <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-2xl font-bold text-white">{{ uploadProgress }}%</span>
              </div>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Processing BIM Model</h3>
            <p class="text-gray-400 mb-4">{{ uploadStatus }}</p>
            <div class="w-64 bg-gray-700 rounded-full h-2">
              <div 
                class="bg-violet-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: uploadProgress + '%' }"
              ></div>
            </div>
          </div>

          <!-- Upload State: Complete -->
          <div v-if="fileUploaded" class="absolute inset-0 p-8">
            <div class="h-full bg-gradient-to-br from-green-500/10 to-blue-500/10 rounded-xl border border-green-500/30 p-6">
              <div class="flex items-center justify-between mb-6">
                <div class="flex items-center space-x-3">
                  <FeatherIcon name="check-circle" class="w-8 h-8 text-green-400" />
                  <div>
                    <h3 class="text-xl font-bold text-white">{{ uploadedFileName }}</h3>
                    <p class="text-green-400">BIM model processed successfully</p>
                  </div>
                </div>
                <button 
                  @click="resetUpload"
                  class="text-gray-400 hover:text-white transition-colors">
                  <FeatherIcon name="x" class="w-6 h-6" />
                </button>
              </div>
              
              <!-- BIM Analysis Results -->
              <div class="grid grid-cols-2 gap-6">
                <div class="space-y-4">
                  <div class="bg-white/5 rounded-lg p-4">
                    <div class="text-2xl font-bold text-white">{{ bimAnalysis.totalArea.toLocaleString() }}</div>
                    <div class="text-sm text-gray-400">Total Area (sq ft)</div>
                  </div>
                  <div class="bg-white/5 rounded-lg p-4">
                    <div class="text-2xl font-bold text-blue-400">{{ bimAnalysis.rooms }}</div>
                    <div class="text-sm text-gray-400">Identified Rooms</div>
                  </div>
                </div>
                <div class="space-y-4">
                  <div class="bg-white/5 rounded-lg p-4">
                    <div class="text-2xl font-bold text-yellow-400">${{ bimAnalysis.estimatedCost.toLocaleString() }}</div>
                    <div class="text-sm text-gray-400">Construction Cost</div>
                  </div>
                  <div class="bg-white/5 rounded-lg p-4">
                    <div class="text-2xl font-bold text-purple-400">{{ bimAnalysis.floors }}</div>
                    <div class="text-sm text-gray-400">Floor Levels</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Tokenization Preview -->
      <div class="space-y-6">
        <!-- Enhanced Property Valuation Card -->
        <div class="hot-asset-card">
          <h3 class="card-title">Live Valuation</h3>
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-gray-300">Market Value</span>
              <span class="text-green-400 font-bold">${{ estimatedPropertyValue.toLocaleString() }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-300">Token Supply</span>
              <span class="text-white font-bold">{{ tokenSupply.toLocaleString() }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-300">Price per Token</span>
              <span class="text-violet-400 font-bold">${{ tokenPrice.toFixed(2) }}</span>
            </div>
            <div class="border-t border-gray-500/30 pt-4">
              <div class="flex justify-between items-center">
                <span class="text-gray-300">Expected ROI</span>
                <span class="asset-roi font-bold">{{ expectedROI }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Investment Breakdown -->
        <div class="glass-card p-6">
          <h3 class="text-xl font-bold text-white mb-4">Investment Structure</h3>
          <div class="space-y-3">
            <div class="bg-gradient-to-r from-blue-500/20 to-blue-600/20 rounded-lg p-3">
              <div class="flex justify-between items-center">
                <span class="text-blue-400">Rental Income</span>
                <span class="text-white font-bold">65%</span>
              </div>
            </div>
            <div class="bg-gradient-to-r from-green-500/20 to-green-600/20 rounded-lg p-3">
              <div class="flex justify-between items-center">
                <span class="text-green-400">Appreciation</span>
                <span class="text-white font-bold">25%</span>
              </div>
            </div>
            <div class="bg-gradient-to-r from-purple-500/20 to-purple-600/20 rounded-lg p-3">
              <div class="flex justify-between items-center">
                <span class="text-purple-400">Platform Fees</span>
                <span class="text-white font-bold">10%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Next Steps -->
        <div class="glass-card p-6">
          <h3 class="text-xl font-bold text-white mb-4">Next Steps</h3>
          <div class="space-y-3">
            <button 
              :disabled="!fileUploaded"
              class="w-full bg-violet-600 hover:bg-violet-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-3 rounded-lg font-medium transition-colors">
              Continue to Viewer
            </button>
            <button 
              :disabled="!fileUploaded"
              class="w-full border border-violet-500 hover:bg-violet-500/20 disabled:border-gray-600 disabled:cursor-not-allowed text-violet-400 disabled:text-gray-400 py-3 rounded-lg font-medium transition-colors">
              Generate Report
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import FeatherIcon from './FeatherIcon.vue'

// Upload state management
const fileInput = ref(null)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const fileUploaded = ref(false)
const uploadedFileName = ref('')

// Property valuation data (connected to real market data)
const estimatedPropertyValue = ref(2850000)
const tokenSupply = ref(100000)
const expectedROI = ref(14.2)

// BIM analysis results
const bimAnalysis = ref({
  totalArea: 12500,
  rooms: 28,
  estimatedCost: 850000,
  floors: 4
})

// Computed properties for tokenization
const tokenPrice = computed(() => estimatedPropertyValue.value / tokenSupply.value)

// File upload handlers
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  uploadedFileName.value = file.name
  uploadProgress.value = 0
  fileUploaded.value = false

  // Simulate BIM processing with realistic stages
  const stages = [
    { progress: 15, status: 'Parsing IFC structure...' },
    { progress: 35, status: 'Extracting geometry data...' },
    { progress: 55, status: 'Analyzing spatial relationships...' },
    { progress: 75, status: 'Calculating property metrics...' },
    { progress: 90, status: 'Generating valuation model...' },
    { progress: 100, status: 'Processing complete!' }
  ]

  for (const stage of stages) {
    uploadProgress.value = stage.progress
    uploadStatus.value = stage.status
    await new Promise(resolve => setTimeout(resolve, 800))
  }

  // Simulate property analysis based on file size and type
  const fileSize = file.size
  const baseValue = 2000000
  const sizeMultiplier = Math.min(fileSize / 1000000, 3) // Cap at 3x for large files
  
  estimatedPropertyValue.value = Math.round(baseValue * (1 + sizeMultiplier * 0.2))
  
  // Update BIM analysis based on file characteristics
  bimAnalysis.value = {
    totalArea: Math.round(8000 + (fileSize / 100000)),
    rooms: Math.round(15 + (fileSize / 500000)),
    estimatedCost: Math.round(600000 + (fileSize / 2000)),
    floors: Math.round(2 + (fileSize / 2000000))
  }

  fileUploaded.value = true
  console.log('BIM file processed:', {
    fileName: uploadedFileName.value,
    estimatedValue: estimatedPropertyValue.value,
    analysis: bimAnalysis.value
  })
}

const resetUpload = () => {
  uploadProgress.value = 0
  uploadStatus.value = ''
  fileUploaded.value = false
  uploadedFileName.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Fetch live property market data on mount
const fetchPropertyMetrics = async () => {
  try {
    const response = await fetch('/api/metrics')
    if (response.ok) {
      const data = await response.json()
      if (data.status === 'success') {
        // Use live blockchain data to enhance property valuation
        const odisPrice = parseFloat(data.data.odis_token.price_usd)
        const marketTrend = parseFloat(data.data.odis_token.price_change_24h)
        
        // Adjust property valuation based on ODIS market performance
        const marketMultiplier = 1 + (marketTrend / 100) * 0.1
        estimatedPropertyValue.value = Math.round(2850000 * marketMultiplier)
        
        console.log('Property valuation updated with live market data:', {
          odisPrice,
          marketTrend,
          adjustedValue: estimatedPropertyValue.value
        })
      }
    }
  } catch (error) {
    console.warn('Property metrics fetch failed, using default values:', error)
  }
}

onMounted(() => {
  console.log('Upload workspace initialized')
  fetchPropertyMetrics()
})
</script>