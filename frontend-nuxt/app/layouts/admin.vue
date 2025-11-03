<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Mobile Menu Button -->
    <div class="lg:hidden fixed top-4 left-4 z-50">
      <UButton
        icon="i-heroicons-bars-3"
        @click="mobileMenuOpen = !mobileMenuOpen"
        aria-label="Toggle menu"
      />
    </div>

    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200 z-40 transform transition-transform duration-300"
      :class="mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
    >
      <div class="p-6">
        <div class="flex items-center justify-between">
          <h2 class="text-2xl font-bold">🔐 Admin</h2>
          <UButton
            icon="i-heroicons-x-mark"
            variant="ghost"
            class="lg:hidden"
            @click="mobileMenuOpen = false"
            aria-label="Close menu"
          />
        </div>
      </div>

      <nav class="px-4 space-y-1">
        <UButton
          to="/admin"
          variant="ghost"
          block
          justify="start"
          icon="i-heroicons-chart-bar"
          :active="$route.path === '/admin'"
          @click="mobileMenuOpen = false"
        >
          Dashboard
        </UButton>
        <UButton
          to="/admin/metrics"
          variant="ghost"
          block
          justify="start"
          icon="i-heroicons-chart-pie"
          @click="mobileMenuOpen = false"
        >
          Metrics
        </UButton>
        <UButton
          to="/admin/settings"
          variant="ghost"
          block
          justify="start"
          icon="i-heroicons-cog-6-tooth"
          @click="mobileMenuOpen = false"
        >
          Settings
        </UButton>
      </nav>
    </aside>

    <!-- Overlay for mobile -->
    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
      @click="mobileMenuOpen = false"
      aria-hidden="true"
    ></div>

    <!-- Main Content -->
    <div class="lg:pl-64">
      <header class="bg-white border-b border-gray-200 p-4">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold ml-12 lg:ml-0">Admin Dashboard</h1>
          <UButton variant="ghost" icon="i-heroicons-arrow-left-on-rectangle" to="/">
            Exit Admin
          </UButton>
        </div>
      </header>

      <main class="p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const mobileMenuOpen = ref(false)

// Close mobile menu when route changes
const route = useRoute()
watch(
  () => route.path,
  () => {
    mobileMenuOpen.value = false
  }
)
</script>
