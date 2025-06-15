<template>
  <div class="metric-card glass-container rounded-xl border border-violet-500/30 p-6 transition-all hover:border-violet-400/50 hover:scale-[1.02]">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-3">
        <div class="p-2 rounded-lg bg-gradient-to-r from-violet-500/20 to-purple-500/20">
          <FeatherIcon :name="icon" class="w-5 h-5 text-violet-400" />
        </div>
        <h3 class="text-white font-medium text-sm">{{ title }}</h3>
      </div>
      <div v-if="trend" class="flex items-center space-x-1">
        <FeatherIcon 
          :name="trend.direction === 'up' ? 'trending-up' : 'trending-down'" 
          class="w-4 h-4" 
          :class="trend.direction === 'up' ? 'text-green-400' : 'text-red-400'"
        />
        <span 
          class="text-xs font-medium"
          :class="trend.direction === 'up' ? 'text-green-400' : 'text-red-400'"
        >
          {{ trend.value }}
        </span>
      </div>
    </div>
    
    <div class="space-y-3">
      <div class="flex items-baseline space-x-2">
        <span class="text-2xl font-bold text-white">{{ value }}</span>
        <span class="text-sm text-gray-400">{{ unit }}</span>
      </div>
      
      <div v-if="subtitle" class="text-xs text-gray-400 leading-relaxed">
        {{ subtitle }}
      </div>
      
      <div v-if="progress" class="w-full bg-gray-700 rounded-full h-1.5">
        <div 
          class="h-1.5 rounded-full transition-all duration-500"
          :class="progress.color || 'bg-gradient-to-r from-violet-400 to-purple-400'"
          :style="{ width: `${progress.percentage}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import FeatherIcon from './FeatherIcon.vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  unit: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    required: true
  },
  trend: {
    type: Object,
    default: null
    // { direction: 'up'|'down', value: '+2.3%' }
  },
  progress: {
    type: Object,
    default: null
    // { percentage: 75, color: 'bg-green-400' }
  }
})
</script>

<style scoped>
.metric-card {
  background: rgba(10, 10, 15, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 92, 246, 0.3);
}

.metric-card:hover {
  background: rgba(10, 10, 15, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(139, 92, 246, 0.2);
}
</style>