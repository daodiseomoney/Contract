<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
      Blockchain Broadcast
    </h1>
    <div class="glass-card p-8">
      <div class="text-center">
        <FeatherIcon name="radio" class="w-16 h-16 text-violet-400 mx-auto mb-4" />
        <p class="text-xl mb-2">Deploy to Odiseo Network</p>
        <p class="text-gray-400 mb-6">Tokenize your property on the blockchain</p>
        <button class="btn-primary">Deploy Contract</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import FeatherIcon from './FeatherIcon.vue'

onMounted(() => {
  console.log('Broadcast component mounted')
})
</script>