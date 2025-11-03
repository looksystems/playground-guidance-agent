<template>
  <div class="loading-state">
    <!-- Spinner -->
    <div v-if="variant === 'spinner'" data-testid="spinner" class="flex flex-col items-center justify-center p-12">
      <UIcon name="i-heroicons-arrow-path" class="w-12 h-12 text-primary-600 animate-spin" />
      <p v-if="message" class="mt-4 text-gray-600">{{ message }}</p>
    </div>

    <!-- Skeleton -->
    <div v-else-if="variant === 'skeleton'" data-testid="skeleton" class="space-y-4">
      <USkeleton class="h-12 w-full" />
      <USkeleton class="h-8 w-3/4" />
      <USkeleton class="h-8 w-1/2" />
    </div>

    <!-- Overlay -->
    <div v-else-if="variant === 'overlay'" data-testid="overlay" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-8 shadow-xl">
        <UIcon name="i-heroicons-arrow-path" class="w-12 h-12 text-primary-600 animate-spin mx-auto" />
        <p v-if="message" class="mt-4 text-gray-900">{{ message }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  variant?: 'spinner' | 'skeleton' | 'overlay'
  message?: string
}>(), {
  variant: 'spinner'
})
</script>
