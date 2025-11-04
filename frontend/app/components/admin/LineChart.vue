<template>
  <div :style="{ height: `${height}px` }">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps<{
  data: any
  height?: number
}>()

const colorMode = useColorMode()

const chartData = computed(() => props.data)

const chartOptions = computed(() => {
  const isDark = colorMode.value === 'dark'

  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          color: isDark ? '#e5e7eb' : '#374151' // gray-200 : gray-700
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: isDark ? '#9ca3af' : '#6b7280' // gray-400 : gray-500
        },
        grid: {
          color: isDark ? '#374151' : '#e5e7eb' // gray-700 : gray-200
        }
      },
      y: {
        beginAtZero: false,
        ticks: {
          callback: (value: any) => `${value}%`,
          color: isDark ? '#9ca3af' : '#6b7280' // gray-400 : gray-500
        },
        grid: {
          color: isDark ? '#374151' : '#e5e7eb' // gray-700 : gray-200
        }
      }
    }
  }
})
</script>
