<template>
  <!-- ODIS Token Value Card - Exact Reference Match -->
  <div class="glass-card-reference p-4 relative">
    <!-- Header -->
    <div class="flex items-start justify-between mb-3">
      <div>
        <h3 class="text-sm text-white/80 font-medium mb-1">ODIS Token Value</h3>
        <div class="text-2xl font-bold text-green-400">
          ${{ price }}
        </div>
      </div>
      <div class="flex items-center space-x-1">
        <div class="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
        <span class="text-xs text-green-400">eLive</span>
      </div>
    </div>
    
    <!-- Performance Indicators -->
    <div class="flex items-center space-x-3 mb-3">
      <span class="text-green-400 text-sm font-medium">{{ changePercent }}</span>
      <span class="text-green-400 text-sm font-medium">{{ roiPercent }}</span>
    </div>
    
    <!-- Chart Area -->
    <div class="h-8 mb-4 relative bg-black/20 rounded">
      <svg class="w-full h-full" viewBox="0 0 100 20">
        <path d="M0,15 Q25,10 50,8 T100,5" stroke="#10b981" stroke-width="1" fill="none" opacity="0.8"/>
      </svg>
    </div>
    
    <!-- Bottom Info -->
    <div class="flex items-center justify-between text-xs text-white/50 mb-3">
      <span>{{ bottomLeft }}</span>
      <span>{{ bottomRight }}</span>
    </div>
    
    <!-- Action Button -->
    <button class="w-full bg-yellow-500 hover:bg-yellow-400 text-black font-semibold py-2 px-4 rounded text-sm transition-colors">
      {{ buttonText }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  price: { type: String, default: '$4.85' },
  changePercent: { type: String, default: '+2.3%' },
  roiPercent: { type: String, default: '+16.1%' },
  bottomLeft: { type: String, default: '$4,850' },
  bottomRight: { type: String, default: 'active' },
  buttonText: { type: String, default: 'Buy Odis' }
})
</script>