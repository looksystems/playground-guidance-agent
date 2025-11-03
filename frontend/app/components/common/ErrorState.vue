<template>
  <div class="error-state flex flex-col items-center justify-center p-12 text-center">
    <UIcon name="i-heroicons-exclamation-circle" class="w-16 h-16 text-red-600 mb-4" />

    <h3 class="text-xl font-semibold text-gray-900 mb-2">
      {{ title || 'Something went wrong' }}
    </h3>

    <p class="text-gray-600 mb-6 max-w-md">
      {{ message || 'An error occurred while loading this page. Please try again.' }}
    </p>

    <div class="flex gap-3">
      <UButton
        @click="$emit('retry')"
        icon="i-heroicons-arrow-path"
      >
        Try Again
      </UButton>

      <UButton
        v-if="showHome"
        to="/"
        variant="outline"
        icon="i-heroicons-home"
      >
        Go Home
      </UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  message?: string
  showHome?: boolean
}>()

defineEmits<{
  retry: []
}>()
</script>
