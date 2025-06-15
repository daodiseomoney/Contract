<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
      Smart Contracts
    </h1>
    <div class="glass-card p-6">
      <div class="grid gap-4">
        <div v-for="contract in contracts" :key="contract.id"
             class="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
          <div class="flex items-center space-x-4">
            <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
              <FeatherIcon name="file-text" class="w-6 h-6 text-white" />
            </div>
            <div>
              <p class="font-semibold">{{ contract.name }}</p>
              <p class="text-sm text-gray-400">{{ contract.address }}</p>
            </div>
          </div>
          <div class="text-right">
            <span class="px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
              {{ contract.status }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import FeatherIcon from './FeatherIcon.vue'

const contracts = ref([
  {
    id: 1,
    name: 'Sunset Apartments Token',
    address: 'odiseo1abc123...def456',
    status: 'Active'
  },
  {
    id: 2,
    name: 'Tech Hub Office Token',
    address: 'odiseo1xyz789...abc123',
    status: 'Active'
  }
])

onMounted(() => {
  console.log('Contracts component mounted')
})
</script>