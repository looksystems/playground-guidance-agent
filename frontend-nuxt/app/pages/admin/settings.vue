<template>
  <div class="space-y-8">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">Settings</h1>
      <p class="mt-2 text-gray-600">Configure system settings and preferences</p>
    </div>

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
      <UButton variant="outline" @click="resetSettings">Reset</UButton>
      <UButton @click="saveSettings">Save Settings</UButton>
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

const saveSettings = () => {
  // In a real app, this would save to the backend
  toast.add({
    title: 'Settings saved',
    description: 'Your settings have been saved successfully',
    color: 'success'
  })
}

const resetSettings = () => {
  settings.value = {
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
  }
  toast.add({
    title: 'Settings reset',
    description: 'Settings have been reset to defaults',
    color: 'warning'
  })
}
</script>
