<template>
  <UCard class="shadow-xl">
    <template #header>
      <div class="text-center space-y-4 py-4">
        <div class="text-6xl">💬</div>
        <h2 class="text-3xl font-bold text-gray-900">Start Your Pension Guidance Consultation</h2>
        <p class="text-lg text-gray-600 max-w-2xl mx-auto">
          Get personalized guidance on your pension options in a safe, confidential environment.
        </p>
      </div>
    </template>

    <UForm :schema="schema" :state="form" @submit="onSubmit" class="space-y-8">
      <!-- First Name -->
      <UFormField
        label="First Name"
        name="firstName"
        required
        size="xl"
      >
        <UInput
          v-model="form.firstName"
          name="firstName"
          placeholder="Enter your first name"
          size="xl"
          required
        />
      </UFormField>

      <!-- Age -->
      <UFormField
        label="Age"
        name="age"
        required
        size="xl"
      >
        <UInput
          v-model.number="form.age"
          name="age"
          type="number"
          placeholder="Enter your age"
          size="xl"
          :min="18"
          :max="120"
          required
        />
      </UFormField>

      <!-- Topic Selection -->
      <UFormField
        label="What brings you here today?"
        name="topic"
        required
        size="xl"
      >
        <div class="radio-group-wrapper space-y-3">
          <div
            v-for="option in topicOptions"
            :key="option.value"
            class="radio-option-wrapper"
            @click="selectTopic(option.value)"
            @keydown.enter="selectTopic(option.value)"
            @keydown.space.prevent="selectTopic(option.value)"
            :tabindex="0"
            role="radio"
            :aria-checked="form.topic === option.value"
            :aria-label="option.label"
            :data-testid="`topic-${option.value}`"
          >
            <label class="flex items-center cursor-pointer p-4 border-2 rounded-lg transition-all hover:border-primary-500 hover:bg-primary-50" :class="{
              'border-primary-500 bg-primary-50': form.topic === option.value,
              'border-gray-300 bg-white': form.topic !== option.value
            }">
              <input
                type="radio"
                :name="'topic'"
                :value="option.value"
                :checked="form.topic === option.value"
                class="sr-only"
                @change="selectTopic(option.value)"
              />
              <span class="flex items-center justify-center w-5 h-5 mr-3 border-2 rounded-full" :class="{
                'border-primary-500': form.topic === option.value,
                'border-gray-400': form.topic !== option.value
              }">
                <span v-if="form.topic === option.value" class="w-3 h-3 bg-primary-500 rounded-full"></span>
              </span>
              <span class="text-base font-medium text-gray-900">{{ option.label }}</span>
            </label>
          </div>
        </div>
      </UFormField>

      <!-- Error Message -->
      <UAlert
        v-if="error"
        color="red"
        variant="soft"
        :title="error"
        :close-button="{ icon: 'i-heroicons-x-mark-20-solid', color: 'gray', variant: 'link', padded: false }"
        @close="error = ''"
      />

      <!-- Submit Button -->
      <div class="pt-4">
        <UButton
          type="submit"
          size="xl"
          block
          :loading="loading"
          :disabled="loading"
        >
          <template v-if="!loading">
            <span>Start Consultation</span>
            <UIcon name="i-heroicons-arrow-right" class="w-5 h-5 ml-2" />
          </template>
          <template v-else>
            <span>Starting...</span>
          </template>
        </UButton>
      </div>
    </UForm>
  </UCard>
</template>

<script setup lang="ts">
import { z } from 'zod'
import type { FormSubmitEvent } from '#ui/types'

const loading = ref(false)
const error = ref('')

const schema = z.object({
  firstName: z.string().min(2, 'Name must be at least 2 characters'),
  age: z.number().min(18, 'Must be 18 or older').max(120, 'Age must be 120 or less'),
  topic: z.string().min(1, 'Please select a topic')
})

type Schema = z.output<typeof schema>

const form = reactive({
  firstName: '',
  age: undefined as number | undefined,
  topic: ''
})

const topicOptions = [
  { value: 'consolidation', label: 'Consolidating pensions' },
  { value: 'withdrawal', label: 'Considering pension withdrawal' },
  { value: 'understanding', label: 'Understanding my options' },
  { value: 'tax', label: 'Tax implications' },
  { value: 'other', label: 'Other' }
]

const selectTopic = (value: string) => {
  form.topic = value
}

const onSubmit = async (event: FormSubmitEvent<Schema>) => {
  loading.value = true
  error.value = ''

  try {
    const data = await $fetch('/api/consultations', {
      method: 'POST',
      body: {
        name: event.data.firstName,
        age: event.data.age,
        initial_query: event.data.topic
      }
    })

    if (data && typeof data === 'object' && 'id' in data) {
      await navigateTo(`/consultation/${(data as { id: string }).id}`)
    }
  } catch (err: any) {
    error.value = err?.data?.message || err?.message || 'Failed to start consultation. Please try again.'
  } finally {
    loading.value = false
  }
}

// Expose for testing
defineExpose({
  form,
  topicOptions,
  selectTopic,
  onSubmit
})
</script>
