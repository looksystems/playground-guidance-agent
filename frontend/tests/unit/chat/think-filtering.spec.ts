/**
 * Tests for <think> tag filtering in customer chat
 *
 * The customer chat component filters out <think> tags from advisor responses
 * since these are internal reasoning blocks that customers shouldn't see.
 */

import { describe, it, expect } from 'vitest'

// Filter function from AIChat.vue
const filterThinkTags = (text: string): string => {
  // Remove <think>...</think> blocks including the tags
  return text.replace(/<think>[\s\S]*?<\/think>/gi, '').trim()
}

describe('Think Tag Filtering', () => {
  it('filters simple think tag', () => {
    const text = '<think>Internal reasoning here</think>Customer-facing content'
    const result = filterThinkTags(text)

    expect(result).toBe('Customer-facing content')
    expect(result).not.toContain('<think>')
    expect(result).not.toContain('Internal reasoning')
  })

  it('filters multiline think blocks', () => {
    const text = `<think>
Okay, I need to help the customer.
Let's break this down:
1. First point
2. Second point
</think>

Thank you for your question. Here's my guidance...`

    const result = filterThinkTags(text)

    expect(result).toContain('Thank you for your question')
    expect(result).not.toContain('<think>')
    expect(result).not.toContain('Okay, I need to help')
  })

  it('filters case-insensitively', () => {
    const testCases = [
      '<think>reasoning</think>content',
      '<THINK>reasoning</THINK>content',
      '<Think>reasoning</Think>content',
      '<tHiNk>reasoning</tHiNk>content',
    ]

    testCases.forEach(text => {
      const result = filterThinkTags(text)
      expect(result).toBe('content')
      expect(result).not.toContain('reasoning')
    })
  })

  it('filters multiple think tags', () => {
    const text = '<think>First reasoning</think>Content 1<think>Second reasoning</think>Content 2'
    const result = filterThinkTags(text)

    expect(result).toBe('Content 1Content 2')
    expect(result).not.toContain('reasoning')
  })

  it('leaves text without think tags unchanged', () => {
    const text = 'This is regular guidance content without any think tags.'
    const result = filterThinkTags(text)

    expect(result).toBe(text)
  })

  it('preserves special characters in content', () => {
    const text = '<think>reasoning</think>Price: £100, (example) [test] *note*'
    const result = filterThinkTags(text)

    expect(result).toContain('Price: £100')
    expect(result).toContain('(example)')
    expect(result).not.toContain('reasoning')
  })

  it('handles empty think tags', () => {
    const text = '<think></think>Content after empty tag'
    const result = filterThinkTags(text)

    expect(result).toBe('Content after empty tag')
  })

  it('preserves angle brackets that are not think tags', () => {
    const text = 'For x < 10 and y > 5, the result is positive.'
    const result = filterThinkTags(text)

    expect(result).toBe(text)
    expect(result).toContain('< 10')
    expect(result).toContain('> 5')
  })

  it('filters real Qwen model output example', () => {
    const text = `<think>
Okay, the user said "Say hello." I need to respond appropriately. Since it's a simple greeting, I should keep the response friendly and open-ended. Maybe start with a cheerful "Hello!" to acknowledge their greeting. Then offer
</think>Hello! How can I assist you today?`

    const result = filterThinkTags(text)

    expect(result).toBe('Hello! How can I assist you today?')
    expect(result).not.toContain('Okay, the user said')
  })
})
