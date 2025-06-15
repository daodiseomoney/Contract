<template>
  <div class="min-h-screen bg-gradient-to-br from-[#0a0a0f] via-[#1a1a2e] to-[#16213e] flex items-center justify-center p-4">
    <div class="glass-container rounded-2xl border border-violet-500/30 p-6 text-center max-w-sm">
      <!-- Logo -->
      <div class="text-violet-400 font-bold text-3xl mb-2">D</div>
      <div class="text-violet-400 font-bold text-xl mb-4">DAODISEO</div>
      
      <!-- Value Proposition -->
      <div class="text-white text-lg mb-4">Real Estate Tokenization Platform</div>
      
      <!-- Features Overview -->
      <div class="text-gray-300 text-sm mb-6 space-y-2">
        <div>• Upload BIM Models</div>
        <div>• AI-Powered Analysis</div>
        <div>• Smart Contract Generation</div>
        <div>• Odiseo Blockchain Integration</div>
      </div>
      
      <!-- Desktop Requirement -->
      <div class="bg-gradient-to-r from-violet-500/20 to-pink-500/20 rounded-lg p-4 mb-6">
        <div class="text-white text-sm font-medium mb-2">Desktop Experience Required</div>
        <div class="text-gray-300 text-xs">
          Complex BIM workflows and blockchain interactions are optimized for desktop browsers with larger screens.
        </div>
      </div>
      
      <!-- Contact Information -->
      <div class="text-violet-400 text-xs mb-4">
        Mobile app launching Q3 2025
      </div>
      
      <!-- Footer -->
      <div class="text-gray-500 text-xs">
        © 2025 DAODISEO
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  console.log('Mobile redirect component mounted')
})
</script>