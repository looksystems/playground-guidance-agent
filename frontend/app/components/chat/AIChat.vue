<template>
  <div class="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
    <!-- Messages -->
    <div ref="messagesRef" class="flex-1 overflow-y-auto p-6 space-y-4">
      <!-- Loading History -->
      <div v-if="isLoadingHistory" class="flex justify-center items-center h-full">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 dark:border-primary-400"></div>
          <p class="mt-2 text-gray-600 dark:text-gray-400">Loading conversation...</p>
        </div>
      </div>

      <!-- Messages -->
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['flex', message.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <div
          :class="[
            'max-w-[70%] rounded-2xl px-4 py-3 shadow-sm',
            message.role === 'user'
              ? 'bg-primary-600 dark:bg-primary-700 text-white'
              : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100'
          ]"
        >
          <div class="prose prose-sm dark:prose-invert max-w-none" v-html="renderMarkdown(message.content)" />

          <!-- Compliance Badge -->
          <div
            v-if="message.role === 'assistant' && message.compliance_score"
            class="mt-2 flex items-center gap-1 text-xs opacity-75 text-gray-600 dark:text-gray-400"
          >
            <UIcon name="i-heroicons-shield-check-solid" class="w-3 h-3" />
            <span>{{ (message.compliance_score * 100).toFixed(0) }}% compliant</span>
          </div>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="flex justify-start">
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3">
          <div class="flex gap-1">
            <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0ms" />
            <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style="animation-delay: 150ms" />
            <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style="animation-delay: 300ms" />
          </div>
        </div>
      </div>
    </div>

    <!-- Input -->
    <div class="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
      <form @submit.prevent="handleSubmit" class="flex gap-3 items-end">
        <UTextarea
          v-model="input"
          :disabled="isLoading"
          placeholder="Ask about your pension options..."
          :rows="1"
          autoresize
          :maxrows="4"
          class="flex-1"
          size="lg"
        />
        <UButton
          type="submit"
          :disabled="!input.trim() || isLoading"
          :loading="isLoading"
          icon="i-heroicons-paper-airplane-solid"
          size="lg"
        >
          Send
        </UButton>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  compliance_score?: number
}

const props = defineProps<{
  consultationId: string
}>()

const messagesRef = ref<HTMLDivElement>()
const messages = ref<Message[]>([])
const input = ref('')
const isLoading = ref(false)
const isLoadingHistory = ref(false)

// Load conversation history when component mounts
onMounted(async () => {
  await loadConversationHistory()
})

const loadConversationHistory = async () => {
  isLoadingHistory.value = true
  try {
    const response = await fetch(`/api/consultations/${props.consultationId}`)
    if (!response.ok) {
      console.error('Failed to load conversation history')
      return
    }

    const data = await response.json()

    // Convert backend conversation format to our message format
    if (data.conversation && Array.isArray(data.conversation)) {
      messages.value = data.conversation
        .filter((turn: any) => turn.role !== 'system') // Skip system messages
        .map((turn: any, index: number) => ({
          id: `history-${index}`,
          role: turn.role === 'customer' ? 'user' : 'assistant',
          content: turn.content,
          timestamp: turn.timestamp,
          compliance_score: turn.compliance_score
        }))

      // Scroll to bottom after loading
      nextTick(() => {
        messagesRef.value?.scrollTo({
          top: messagesRef.value.scrollHeight,
          behavior: 'smooth'
        })
      })
    }
  } catch (error) {
    console.error('Error loading conversation history:', error)
  } finally {
    isLoadingHistory.value = false
  }
}

const handleSubmit = async (event?: { preventDefault?: () => void }) => {
  event?.preventDefault?.()

  if (!input.value.trim() || isLoading.value) return

  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: input.value,
    timestamp: new Date().toISOString()
  }

  messages.value.push(userMessage)
  const currentInput = input.value
  input.value = ''
  isLoading.value = true

  try {
    // Step 1: Send message to backend
    const messageResponse = await fetch(`/api/consultations/${props.consultationId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content: currentInput })
    })

    if (!messageResponse.ok) {
      throw new Error('Failed to send message')
    }

    // Step 2: Connect to SSE stream for advisor response
    const eventSource = new EventSource(`/api/consultations/${props.consultationId}/stream`)

    // Create a placeholder message for streaming response
    const assistantMessageId = (Date.now() + 1).toString()
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString()
    }
    messages.value.push(assistantMessage)

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        if (data.type === 'chunk') {
          // Append chunk to assistant message
          const msgIndex = messages.value.findIndex(m => m.id === assistantMessageId)
          if (msgIndex !== -1) {
            messages.value[msgIndex].content += data.content
          }

          // Scroll to bottom
          nextTick(() => {
            messagesRef.value?.scrollTo({
              top: messagesRef.value.scrollHeight,
              behavior: 'smooth'
            })
          })
        } else if (data.type === 'complete') {
          // Update with final message and compliance score
          const msgIndex = messages.value.findIndex(m => m.id === assistantMessageId)
          if (msgIndex !== -1) {
            messages.value[msgIndex].content = data.full_message
            messages.value[msgIndex].compliance_score = data.compliance_score
          }

          // Close connection
          eventSource.close()
          isLoading.value = false

          // Scroll to bottom
          nextTick(() => {
            messagesRef.value?.scrollTo({
              top: messagesRef.value.scrollHeight,
              behavior: 'smooth'
            })
          })
        } else if (data.type === 'error') {
          console.error('Stream error:', data.error)
          eventSource.close()
          isLoading.value = false

          // Update message to show error
          const msgIndex = messages.value.findIndex(m => m.id === assistantMessageId)
          if (msgIndex !== -1) {
            messages.value[msgIndex].content = 'Sorry, an error occurred. Please try again.'
          }
        }
      } catch (err) {
        console.error('Error parsing SSE data:', err)
      }
    }

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error)
      eventSource.close()
      isLoading.value = false
    }

  } catch (error) {
    console.error('Error sending message:', error)
    isLoading.value = false

    // Show error message
    messages.value.push({
      id: (Date.now() + 2).toString(),
      role: 'assistant',
      content: 'Sorry, an error occurred. Please try again.',
      timestamp: new Date().toISOString()
    })
  }
}

const renderMarkdown = (text: string) => marked.parse(text)

// Expose for testing
defineExpose({
  messages,
  input,
  isLoading,
  handleSubmit
})
</script>
