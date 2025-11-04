<template>
  <button
    @click="toggleColorMode"
    :aria-label="colorMode.value === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
    class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
    type="button"
  >
    <Icon
      :name="colorMode.value === 'dark' ? 'i-heroicons-moon' : 'i-heroicons-sun'"
      class="w-5 h-5 text-gray-700 dark:text-gray-300"
    />
  </button>
</template>

<script setup lang="ts">
const colorMode = useColorMode()

const toggleColorMode = () => {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>
