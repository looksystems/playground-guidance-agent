<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Mobile Menu Button -->
    <div class="lg:hidden fixed top-4 left-4 z-50">
      <UButton
        color="indigo"
        icon="i-heroicons-bars-3"
        @click="mobileMenuOpen = !mobileMenuOpen"
        aria-label="Toggle menu"
      />
    </div>

    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 z-40 transform transition-transform duration-300"
      :class="mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
    >
      <div class="p-6">
        <div class="flex items-center justify-between">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">🔐 Admin</h2>
          <UButton
            color="indigo"
            icon="i-heroicons-x-mark"
            variant="ghost"
            class="lg:hidden"
            @click="mobileMenuOpen = false"
            aria-label="Close menu"
          />
        </div>
      </div>

      <nav class="px-4 pb-4 space-y-6 overflow-y-auto" style="max-height: calc(100vh - 120px);">
        <!-- Dashboard Section -->
        <div class="space-y-1">
          <div class="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider text-left">
            Dashboard
          </div>
          <UButton
            to="/admin"
            color="indigo"
            variant="ghost"
            block
            justify="start"
            icon="i-heroicons-chart-bar"
            :active="$route.path === '/admin'"
            @click="mobileMenuOpen = false"
            class="text-left"
          >
            Overview
          </UButton>
        </div>

        <!-- Analytics Section -->
        <div class="space-y-1">
          <div class="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider text-left">
            Analytics
          </div>
          <UButton
            to="/admin/metrics"
            color="indigo"
            variant="ghost"
            block
            justify="start"
            icon="i-heroicons-chart-pie"
            :active="$route.path === '/admin/metrics'"
            @click="mobileMenuOpen = false"
          >
            Metrics
          </UButton>
        </div>

        <!-- Knowledge Base Section -->
        <div class="space-y-1">
          <div class="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider text-left">
            Knowledge Base
          </div>
          <UButton
            to="/admin/knowledge/fca"
            color="indigo"
            variant="ghost"
            block
            justify="start"
            icon="i-heroicons-clipboard-document-list"
            :active="$route.path.startsWith('/admin/knowledge/fca')"
            @click="mobileMenuOpen = false"
          >
            FCA Knowledge
          </UButton>
          <UButton
            to="/admin/knowledge/pension"
            color="indigo"
            variant="ghost"
            block
            justify="start"
            icon="i-heroicons-academic-cap"
            :active="$route.path.startsWith('/admin/knowledge/pension')"
            @click="mobileMenuOpen = false"
          >
            Pension Knowledge
          </UButton>
        </div>

        <!-- Learning System Section -->
        <div class="space-y-1">
          <div class="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider text-left">
            Learning System
          </div>
          <UButton
            to="/admin/learning/memories"
            color="indigo"
            variant="ghost"
            block
            justify="start"
            icon="i-heroicons-light-bulb"
            :active="$route.path.startsWith('/admin/learning/memories')"
            @click="mobileMenuOpen = false"
          >
            Memories
          </UButton>
          <UButton
            to="/admin/learning/cases"
            color="indigo"
            variant="ghost"
            block
            justify="start"
            icon="i-heroicons-cube"
            :active="$route.path.startsWith('/admin/learning/cases')"
            @click="mobileMenuOpen = false"
          >
            Cases
          </UButton>
          <UButton
            to="/admin/learning/rules"
            color="indigo"
            variant="ghost"
            block
            justify="start"
            icon="i-heroicons-scale"
            :active="$route.path.startsWith('/admin/learning/rules')"
            @click="mobileMenuOpen = false"
          >
            Rules
          </UButton>
        </div>

        <!-- User Management Section -->
        <div class="space-y-1">
          <div class="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider text-left">
            User Management
          </div>
          <UButton
            to="/admin/users/customers"
            color="indigo"
            variant="ghost"
            block
            justify="start"
            icon="i-heroicons-user-group"
            :active="$route.path.startsWith('/admin/users/customers')"
            @click="mobileMenuOpen = false"
          >
            Customers
          </UButton>
          <UButton
            to="/admin/consultations"
            color="indigo"
            variant="ghost"
            block
            justify="start"
            icon="i-heroicons-chat-bubble-left-right"
            :active="$route.path.startsWith('/admin/consultations')"
            @click="mobileMenuOpen = false"
          >
            Consultations
          </UButton>
        </div>

        <!-- Settings Section -->
        <div class="space-y-1">
          <div class="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider text-left">
            Settings
          </div>
          <UButton
            to="/admin/settings"
            color="indigo"
            variant="ghost"
            block
            justify="start"
            icon="i-heroicons-cog-6-tooth"
            :active="$route.path.startsWith('/admin/settings')"
            @click="mobileMenuOpen = false"
          >
            System Settings
          </UButton>
        </div>
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
      <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold ml-12 lg:ml-0 text-gray-900 dark:text-gray-100">Admin Dashboard</h1>
          <div class="flex gap-2 items-center">
            <ColorModeToggle />
            <UButton color="indigo" variant="ghost" icon="i-heroicons-arrow-left-on-rectangle" to="/">
              Exit Admin
            </UButton>
          </div>
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
