/**
 * Tests for <think> tag highlighting in admin consultation view
 *
 * Admin view should highlight <think> blocks to make internal reasoning visible,
 * while customer view should filter them out completely.
 */

import { describe, it, expect } from 'vitest'

// Highlight function from admin/consultations/[id].vue
const highlightThinkTags = (text: string): string => {
  return text.replace(
    /<think>([\s\S]*?)<\/think>/gi,
    '<div class="bg-purple-50 dark:bg-purple-900/20 border-l-4 border-purple-500 pl-4 py-2 my-2 italic text-purple-700 dark:text-purple-300"><strong>[Internal Reasoning]</strong><br>$1</div>'
  )
}

// Filter function from customer chat (for comparison)
const filterThinkTags = (text: string): string => {
  return text.replace(/<think>[\s\S]*?<\/think>/gi, '').trim()
}

describe('Think Tag Highlighting in Admin View', () => {
  const sampleText = `<think>
I need to help the customer with pension consolidation.
Let me consider the pros and cons.
</think>

Thank you for your question about consolidating your pensions.`

  it('converts think blocks to highlighted divs', () => {
    const result = highlightThinkTags(sampleText)

    expect(result).toContain('[Internal Reasoning]')
    expect(result).toContain('bg-purple-50')
    expect(result).toContain('border-purple-500')
    expect(result).not.toContain('<think>')
    expect(result).not.toContain('</think>')
  })

  it('preserves content inside think blocks', () => {
    const result = highlightThinkTags(sampleText)

    expect(result).toContain('I need to help the customer')
    expect(result).toContain('pension consolidation')
    expect(result).toContain('pros and cons')
  })

  it('preserves content outside think blocks', () => {
    const result = highlightThinkTags(sampleText)

    expect(result).toContain('Thank you for your question')
    expect(result).toContain('consolidating your pensions')
  })

  it('handles multiple think blocks', () => {
    const text = `<think>First reasoning</think>
Content 1
<think>Second reasoning</think>
Content 2`

    const result = highlightThinkTags(text)
    const highlightCount = (result.match(/\[Internal Reasoning\]/g) || []).length

    expect(highlightCount).toBe(2)
    expect(result).toContain('First reasoning')
    expect(result).toContain('Second reasoning')
    expect(result).toContain('Content 1')
    expect(result).toContain('Content 2')
  })

  it('handles case-insensitive think tags', () => {
    const testCases = [
      '<think>reasoning</think>',
      '<THINK>reasoning</THINK>',
      '<Think>reasoning</Think>',
    ]

    testCases.forEach(text => {
      const result = highlightThinkTags(text)
      expect(result).toContain('[Internal Reasoning]')
      expect(result).toContain('reasoning')
    })
  })

  it('leaves text without think tags unchanged', () => {
    const text = 'Regular guidance content without think tags.'
    const result = highlightThinkTags(text)

    expect(result).toBe(text)
  })

  describe('Comparison: Admin vs Customer View', () => {
    it('admin view shows reasoning, customer view hides it', () => {
      const text = `<think>Internal reasoning here</think>Customer content`

      // Admin view: shows reasoning in highlighted box
      const adminResult = highlightThinkTags(text)
      expect(adminResult).toContain('Internal reasoning here')
      expect(adminResult).toContain('[Internal Reasoning]')

      // Customer view: completely removes reasoning
      const customerResult = filterThinkTags(text)
      expect(customerResult).toBe('Customer content')
      expect(customerResult).not.toContain('Internal reasoning')
      expect(customerResult).not.toContain('[Internal Reasoning]')
    })

    it('both views preserve customer-facing content', () => {
      const text = `<think>Reasoning</think>Important guidance for customer`

      const adminResult = highlightThinkTags(text)
      const customerResult = filterThinkTags(text)

      // Both should contain the guidance
      expect(adminResult).toContain('Important guidance for customer')
      expect(customerResult).toContain('Important guidance for customer')

      // Only admin shows reasoning
      expect(adminResult).toContain('Reasoning')
      expect(customerResult).not.toContain('Reasoning')
    })
  })

  describe('Real-world Examples', () => {
    it('handles realistic Qwen model output', () => {
      const qwenOutput = `<think>
Okay, the customer is 48 with £150k and wants to know if that's enough.
I need to:
1. Not evaluate their situation (FCA neutrality)
2. List factors that determine adequacy
3. Offer to explore or signpost to adviser
</think>

Thank you for sharing that information. To determine whether £150,000 will be sufficient for your retirement, we need to consider several important factors:

- Your desired retirement age and lifestyle
- Expected state pension amount
- Other income sources
- Life expectancy and health considerations

Would you like to explore what you might need for retirement?`

      // Admin view shows everything with reasoning highlighted
      const adminResult = highlightThinkTags(qwenOutput)
      expect(adminResult).toContain('[Internal Reasoning]')
      expect(adminResult).toContain('FCA neutrality')
      expect(adminResult).toContain('Thank you for sharing')

      // Customer view shows only guidance
      const customerResult = filterThinkTags(qwenOutput)
      expect(customerResult).not.toContain('FCA neutrality')
      expect(customerResult).not.toContain('Okay, the customer')
      expect(customerResult).toContain('Thank you for sharing')
      expect(customerResult).toContain('desired retirement age')
    })
  })
})
