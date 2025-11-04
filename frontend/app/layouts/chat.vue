<template>
  <div class="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
    <header class="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-50 flex-shrink-0">
      <div class="max-w-7xl mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <NuxtLink to="/" class="text-2xl font-bold text-primary-900 dark:text-primary-100">
            Pension Guidance Service
          </NuxtLink>
          <nav class="flex gap-2 items-center">
            <UButton to="/history" variant="ghost">
              <UIcon name="i-heroicons-clock" class="w-5 h-5" />
              History
            </UButton>
            <UButton variant="ghost">
              <UIcon name="i-heroicons-question-mark-circle" class="w-5 h-5" />
              Help
            </UButton>
            <UButton variant="outline">
              <UIcon name="i-heroicons-arrow-left-on-rectangle" class="w-5 h-5" />
              Sign Out
            </UButton>
            <ColorModeToggle />
          </nav>
        </div>
      </div>
    </header>

    <main class="flex-1 overflow-hidden">
      <slot />
    </main>
  </div>
</template>
