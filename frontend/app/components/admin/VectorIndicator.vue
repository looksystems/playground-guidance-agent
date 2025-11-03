<template>
  <UTooltip
    :text="tooltipText"
    :popper="{ placement: 'top' }"
  >
    <UBadge
      :color="hasEmbedding ? 'green' : 'gray'"
      :size="size"
      variant="subtle"
      class="inline-flex items-center gap-1"
    >
      <UIcon
        :name="iconName"
        :class="iconClass"
      />
      <span v-if="showLabel" class="font-medium">
        {{ hasEmbedding ? 'Embedded' : 'No Embedding' }}
      </span>
    </UBadge>
  </UTooltip>
</template>

<script setup lang="ts">
/**
 * VectorIndicator Component
 *
 * A visual indicator component for displaying the presence or absence
 * of vector embeddings. Shows a green checkmark badge when an embedding
 * is present and a gray dash when absent.
 *
 * @component
 * @example
 * ```vue
 * <!-- With embedding -->
 * <VectorIndicator :has-embedding="true" size="md" />
 *
 * <!-- Without embedding -->
 * <VectorIndicator :has-embedding="false" size="sm" />
 *
 * <!-- With label -->
 * <VectorIndicator :has-embedding="true" :show-label="true" />
 * ```
 */

interface Props {
  /** Whether a vector embedding is present */
  hasEmbedding: boolean
  /** Size of the indicator badge */
  size?: 'xs' | 'sm' | 'md' | 'lg'
  /** Whether to show text label alongside icon */
  showLabel?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  showLabel: false,
})

/**
 * Tooltip text based on embedding status
 */
const tooltipText = computed(() => {
  return props.hasEmbedding
    ? 'Vector embedding present'
    : 'No embedding'
})

/**
 * Icon name based on embedding status
 */
const iconName = computed(() => {
  return props.hasEmbedding
    ? 'i-heroicons-check-circle-20-solid'
    : 'i-heroicons-minus-circle-20-solid'
})

/**
 * Icon class for size adjustments
 */
const iconClass = computed(() => {
  const sizeMap = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  }

  return sizeMap[props.size] || sizeMap.md
})
</script>

<style scoped>
/* No custom styles needed - using Nuxt UI components */
</style>
