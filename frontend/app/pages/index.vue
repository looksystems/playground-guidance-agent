<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
    <div class="max-w-2xl mx-auto px-4">
      <CustomerProfileForm />

      <!-- Quick Links -->
      <div class="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
        <UCard class="p-6">
          <NuxtLink to="/history" class="flex items-center gap-3 text-gray-900 dark:text-gray-100 hover:text-indigo-700 dark:hover:text-indigo-400 transition-colors">
            <UIcon name="i-heroicons-document-text" class="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
            <span class="text-lg font-medium">View Past Consultations</span>
          </NuxtLink>
        </UCard>

        <UCard class="p-6">
          <NuxtLink to="/admin" class="flex items-center gap-3 text-gray-900 dark:text-gray-100 hover:text-indigo-700 dark:hover:text-indigo-400 transition-colors">
            <UIcon name="i-heroicons-chart-bar" class="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
            <div>
              <span class="text-lg font-medium">Admin Review</span>
              <p class="text-sm text-gray-600 dark:text-gray-400">(Admin Only)</p>
            </div>
          </NuxtLink>
        </UCard>
      </div>
    </div>
  </div>
</template>
