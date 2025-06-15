<template>
  <div class="workflow-strip glass-container rounded-2xl border border-violet-500/30 p-8">
    <div class="flex items-center justify-center space-x-8">
      
      <!-- Step 1: Upload -->
      <div class="workflow-step" :class="{ 'workflow-step-active': isStepActive('upload') }">
        <div class="workflow-step-icon">
          <FeatherIcon name="upload" class="w-6 h-6" />
        </div>
        <div class="workflow-step-content">
          <div class="workflow-step-title">Upload</div>
          <div class="workflow-step-subtitle">BIM Models</div>
          <div v-if="uploadCost" class="workflow-step-cost">{{ uploadCost }} ODIS</div>
        </div>
      </div>

      <!-- Arrow 1 -->
      <div class="workflow-arrow">
        <FeatherIcon name="arrow-right" class="w-5 h-5 text-violet-400" />
      </div>

      <!-- Step 2: Viewer -->
      <div class="workflow-step" :class="{ 'workflow-step-active': isStepActive('viewer') }">
        <div class="workflow-step-icon">
          <FeatherIcon name="eye" class="w-6 h-6" />
        </div>
        <div class="workflow-step-content">
          <div class="workflow-step-title">Viewer</div>
          <div class="workflow-step-subtitle">3D Analysis</div>
          <div v-if="analysisCost" class="workflow-step-cost">{{ analysisCost }} ODIS</div>
        </div>
      </div>

      <!-- Arrow 2 -->
      <div class="workflow-arrow">
        <FeatherIcon name="arrow-right" class="w-5 h-5 text-violet-400" />
      </div>

      <!-- Step 3: Broadcast -->
      <div class="workflow-step" :class="{ 'workflow-step-active': isStepActive('broadcast') }">
        <div class="workflow-step-icon">
          <FeatherIcon name="radio" class="w-6 h-6" />
        </div>
        <div class="workflow-step-content">
          <div class="workflow-step-title">Broadcast</div>
          <div class="workflow-step-subtitle">Deploy to Odiseo</div>
          <div v-if="broadcastCost" class="workflow-step-cost">{{ broadcastCost }} ODIS</div>
        </div>
      </div>

      <!-- Arrow 3 -->
      <div class="workflow-arrow">
        <FeatherIcon name="arrow-right" class="w-5 h-5 text-violet-400" />
      </div>

      <!-- Step 4: Asset Management -->
      <div class="workflow-step" :class="{ 'workflow-step-active': isStepActive('contracts') }">
        <div class="workflow-step-icon">
          <FeatherIcon name="layers" class="w-6 h-6" />
        </div>
        <div class="workflow-step-content">
          <div class="workflow-step-title">Asset Management</div>
          <div class="workflow-step-subtitle">Smart Contracts</div>
          <div v-if="contractCost" class="workflow-step-cost">{{ contractCost }} ODIS</div>
        </div>
      </div>

    </div>

    <!-- Progress Bar -->
    <div class="mt-6 w-full bg-gray-700 rounded-full h-2">
      <div 
        class="h-2 rounded-full bg-gradient-to-r from-violet-400 to-purple-400 transition-all duration-500"
        :style="{ width: `${progress}%` }"
      ></div>
    </div>

    <!-- Progress Text -->
    <div class="mt-3 text-center text-sm text-gray-400">
      {{ progressText }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import FeatherIcon from './FeatherIcon.vue'

const props = defineProps({
  currentStep: {
    type: String,
    default: 'upload'
  },
  completedSteps: {
    type: Array,
    default: () => []
  },
  uploadCost: {
    type: String,
    default: '1'
  },
  analysisCost: {
    type: String,
    default: '2'
  },
  broadcastCost: {
    type: String,
    default: '5'
  },
  contractCost: {
    type: String,
    default: '3'
  }
})

const steps = ['upload', 'viewer', 'broadcast', 'contracts']

const isStepActive = (step) => {
  return props.currentStep === step || props.completedSteps.includes(step)
}

const progress = computed(() => {
  const currentIndex = steps.indexOf(props.currentStep)
  const completedCount = props.completedSteps.length
  return Math.max((currentIndex + 1) * 25, completedCount * 25)
})

const progressText = computed(() => {
  const currentIndex = steps.indexOf(props.currentStep)
  return `Step ${currentIndex + 1} of ${steps.length}: ${props.currentStep.charAt(0).toUpperCase() + props.currentStep.slice(1)}`
})
</script>

<style scoped>
.workflow-strip {
  background: rgba(10, 10, 15, 0.6);
  backdrop-filter: blur(20px);
}

.workflow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: all 0.3s ease;
  opacity: 0.6;
}

.workflow-step-active {
  opacity: 1;
  transform: scale(1.05);
}

.workflow-step-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(139, 92, 246, 0.2);
  border: 2px solid rgba(139, 92, 246, 0.3);
  color: rgb(196, 181, 253);
  margin-bottom: 0.75rem;
  transition: all 0.3s ease;
}

.workflow-step-active .workflow-step-icon {
  background: rgba(139, 92, 246, 0.4);
  border-color: rgba(139, 92, 246, 0.6);
  color: white;
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}

.workflow-step-content {
  min-height: 4rem;
}

.workflow-step-title {
  font-weight: 600;
  color: white;
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.workflow-step-subtitle {
  font-size: 0.75rem;
  color: rgb(156, 163, 175);
  margin-top: 0.25rem;
}

.workflow-step-cost {
  font-size: 0.75rem;
  color: rgb(250, 204, 21);
  margin-top: 0.25rem;
  font-weight: 500;
}

.workflow-arrow {
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

.workflow-step-active + .workflow-arrow {
  opacity: 1;
}
</style>