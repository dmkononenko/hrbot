<script setup lang="ts">
import { computed } from 'vue'
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js'
import type { ChartData, ChartOptions } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, ArcElement)

interface Props {
  data: ChartData<'pie'>
  options?: ChartOptions<'pie'>
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  height: 300,
})

const chartOptions = computed<ChartOptions<'pie'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        padding: 15,
        font: {
          size: 12,
        },
        usePointStyle: true,
      },
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 12,
      titleFont: {
        size: 14,
      },
      bodyFont: {
        size: 13,
      },
      callbacks: {
        label: (context) => {
          const label = context.label || ''
          const value = context.parsed
          const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
          const percentage = ((value / total) * 100).toFixed(1)
          return `${label}: ${value} (${percentage}%)`
        },
      },
    },
  },
  ...props.options,
}))
</script>

<template>
  <div :style="{ height: `${height}px` }">
    <Pie :data="data" :options="chartOptions" />
  </div>
</template>
