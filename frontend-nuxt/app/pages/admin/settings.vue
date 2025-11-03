<template>
  <div class="space-y-8">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">Settings</h1>
      <p class="mt-2 text-gray-600">Configure system settings and preferences</p>
    </div>

    <!-- Loading State -->
    <div v-if="initialLoading" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="mt-2 text-sm text-gray-500">Loading settings...</p>
      </div>
    </div>

    <!-- Settings Forms (hidden while loading) -->
    <div v-if="!initialLoading" class="space-y-8">
      <!-- General Settings -->
      <UCard>
        <template #header>
          <h2 class="text-xl font-semibold">General Settings</h2>
        </template>
      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">System Name</label>
          <UInput v-model="settings.systemName" placeholder="Enter system name" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Support Email</label>
          <UInput v-model="settings.supportEmail" type="email" placeholder="support@example.com" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Session Timeout (minutes)</label>
          <UInput v-model="settings.sessionTimeout" type="number" placeholder="30" />
        </div>
      </div>
    </UCard>

    <!-- Compliance Settings -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">Compliance Settings</h2>
      </template>
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <label class="block text-sm font-medium text-gray-700">Enable FCA Compliance Checks</label>
            <p class="text-sm text-gray-500">Automatically validate consultations against FCA guidelines</p>
          </div>
          <UCheckbox v-model="settings.fcaComplianceEnabled" />
        </div>
        <div class="flex items-center justify-between">
          <div>
            <label class="block text-sm font-medium text-gray-700">Require Risk Assessment</label>
            <p class="text-sm text-gray-500">Mandate risk assessment for all consultations</p>
          </div>
          <UCheckbox v-model="settings.riskAssessmentRequired" />
        </div>
        <div class="flex items-center justify-between">
          <div>
            <label class="block text-sm font-medium text-gray-700">Auto-Archive Consultations</label>
            <p class="text-sm text-gray-500">Automatically archive consultations after 90 days</p>
          </div>
          <UCheckbox v-model="settings.autoArchive" />
        </div>
      </div>
    </UCard>

    <!-- Notification Settings -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">Notification Settings</h2>
      </template>
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <label class="block text-sm font-medium text-gray-700">Email Notifications</label>
            <p class="text-sm text-gray-500">Receive email alerts for important events</p>
          </div>
          <UCheckbox v-model="settings.emailNotifications" />
        </div>
        <div class="flex items-center justify-between">
          <div>
            <label class="block text-sm font-medium text-gray-700">Compliance Alerts</label>
            <p class="text-sm text-gray-500">Get notified when compliance scores drop below threshold</p>
          </div>
          <UCheckbox v-model="settings.complianceAlerts" />
        </div>
        <div class="flex items-center justify-between">
          <div>
            <label class="block text-sm font-medium text-gray-700">Daily Digest</label>
            <p class="text-sm text-gray-500">Receive daily summary of consultations and metrics</p>
          </div>
          <UCheckbox v-model="settings.dailyDigest" />
        </div>
      </div>
    </UCard>

    <!-- AI Configuration -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">AI Configuration</h2>
      </template>
      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">AI Model</label>
          <USelect v-model="settings.aiModel" :options="aiModels" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Temperature</label>
          <UInput v-model="settings.temperature" type="number" step="0.1" min="0" max="2" />
          <p class="mt-1 text-xs text-gray-500">Controls randomness in responses (0.0 - 2.0)</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Max Tokens</label>
          <UInput v-model="settings.maxTokens" type="number" />
        </div>
      </div>
    </UCard>

      <!-- Save Button -->
      <div class="flex justify-end gap-3">
        <UButton variant="outline" @click="resetSettings" :disabled="loading">Reset</UButton>
        <UButton @click="saveSettings" :loading="loading" :disabled="loading">
          {{ loading ? 'Saving...' : 'Save Settings' }}
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin'
})

const settings = ref({
  systemName: 'Pension Guidance Service',
  supportEmail: 'support@pensionguidance.com',
  sessionTimeout: 30,
  fcaComplianceEnabled: true,
  riskAssessmentRequired: true,
  autoArchive: false,
  emailNotifications: true,
  complianceAlerts: true,
  dailyDigest: false,
  aiModel: 'gpt-4',
  temperature: 0.7,
  maxTokens: 2000
})

const aiModels = [
  { label: 'GPT-4', value: 'gpt-4' },
  { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' },
  { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
  { label: 'Claude 3 Opus', value: 'claude-3-opus' },
  { label: 'Claude 3 Sonnet', value: 'claude-3-sonnet' }
]

const toast = useToast()
const loading = ref(false)
const initialLoading = ref(true)

// Store original settings for reset
const originalSettings = ref({})

// Load settings from backend on mount
onMounted(async () => {
  await loadSettings()
})

const loadSettings = async () => {
  try {
    initialLoading.value = true
    const { data, error } = await useFetch('/api/admin/settings', {
      headers: {
        'Authorization': 'Bearer admin-token'
      }
    })

    if (error.value) {
      console.error('Failed to load settings:', error.value)
      toast.add({
        title: 'Error loading settings',
        description: 'Could not load settings from server. Using defaults.',
        color: 'error'
      })
      return
    }

    if (data.value) {
      settings.value = { ...data.value }
      originalSettings.value = { ...data.value }
    }
  } catch (err) {
    console.error('Error loading settings:', err)
    toast.add({
      title: 'Error loading settings',
      description: 'An unexpected error occurred.',
      color: 'error'
    })
  } finally {
    initialLoading.value = false
  }
}

const saveSettings = async () => {
  try {
    loading.value = true

    const { data, error } = await useFetch('/api/admin/settings', {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer admin-token'
      },
      body: settings.value
    })

    if (error.value) {
      console.error('Failed to save settings:', error.value)
      toast.add({
        title: 'Error saving settings',
        description: 'Could not save settings to server.',
        color: 'error'
      })
      return
    }

    if (data.value) {
      settings.value = { ...data.value }
      originalSettings.value = { ...data.value }
      toast.add({
        title: 'Settings saved',
        description: 'Your settings have been saved successfully',
        color: 'success'
      })
    }
  } catch (err) {
    console.error('Error saving settings:', err)
    toast.add({
      title: 'Error saving settings',
      description: 'An unexpected error occurred.',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

const resetSettings = () => {
  // Reset to originally loaded settings
  settings.value = { ...originalSettings.value }
  toast.add({
    title: 'Settings reset',
    description: 'Settings have been reset to last saved values',
    color: 'warning'
  })
}
</script>
