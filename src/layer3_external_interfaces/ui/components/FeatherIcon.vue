<template>
  <i :data-feather="name" :class="className" ref="iconRef"></i>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import feather from 'feather-icons'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  className: {
    type: String,
    default: 'w-5 h-5'
  }
})

const iconRef = ref(null)

const replaceIcon = () => {
  if (iconRef.value) {
    feather.replace()
  }
}

onMounted(() => {
  replaceIcon()
})

watch(() => props.name, () => {
  replaceIcon()
})
</script>