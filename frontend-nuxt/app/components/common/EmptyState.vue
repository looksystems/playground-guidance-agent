<template>
  <div class="empty-state flex flex-col items-center justify-center p-12 text-center">
    <UIcon
      :name="icon || 'i-heroicons-inbox'"
      class="w-16 h-16 text-gray-400 mb-4"
    />

    <h3 class="text-lg font-semibold text-gray-900 mb-2">
      {{ title || 'Nothing here yet' }}
    </h3>

    <p class="text-gray-600 mb-6 max-w-md">
      {{ message || 'Get started by creating your first item.' }}
    </p>

    <UButton
      v-if="actionLabel"
      :to="actionTo"
      :icon="actionIcon"
    >
      {{ actionLabel }}
    </UButton>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon?: string
  title?: string
  message?: string
  actionLabel?: string
  actionTo?: string
  actionIcon?: string
}>()
</script>
