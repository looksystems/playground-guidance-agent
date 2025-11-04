<template>
  <div class="h-full flex flex-col">
    <!-- Consultation Header -->
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex-shrink-0">
      <div class="flex items-center justify-between max-w-7xl mx-auto">
        <NuxtLink to="/" class="flex items-center gap-2 text-primary-700 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300">
          <UIcon name="i-heroicons-arrow-left" />
          <span>Back to Home</span>
        </NuxtLink>

        <h1 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Consultation with Sarah</h1>

        <UDropdownMenu :items="menuItems">
          <UButton icon="i-heroicons-ellipsis-vertical" variant="ghost" />
        </UDropdownMenu>
      </div>
    </header>

    <!-- Advisor Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex-shrink-0">
      <div class="flex items-center gap-3 max-w-7xl mx-auto">
        <UAvatar size="md" alt="Sarah" />
        <div>
          <div class="font-semibold text-gray-900 dark:text-gray-100">Sarah</div>
          <div class="text-sm text-gray-600 dark:text-gray-400">Pension Guidance Specialist</div>
        </div>
        <UBadge color="success" variant="soft">Active</UBadge>
      </div>
    </div>

    <!-- Chat Component -->
    <div class="flex-1 overflow-hidden" data-testid="chat-container">
      <AIChat :consultation-id="id" />
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'chat'
})

const route = useRoute()
const router = useRouter()
const id = computed(() => route.params.id as string)

const ending = ref(false)

const handleEndConsultation = async () => {
  if (!confirm('Are you sure you want to end this consultation? This action cannot be undone.')) {
    return
  }

  ending.value = true
  try {
    await $fetch(`/api/consultations/${id.value}/end`, {
      method: 'POST',
      body: {}
    })

    // Redirect to history page
    router.push('/history')
  } catch (error) {
    console.error('Error ending consultation:', error)
    alert('Failed to end consultation. Please try again.')
  } finally {
    ending.value = false
  }
}

const menuItems = [[
  { label: 'Export Transcript', icon: 'i-heroicons-document-arrow-down' }
], [
  {
    label: 'End Consultation',
    icon: 'i-heroicons-x-mark',
    color: 'error' as const,
    onSelect: handleEndConsultation
  }
]]
</script>
