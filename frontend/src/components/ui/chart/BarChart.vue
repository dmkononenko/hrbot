<script setup lang="ts">
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import type { ChartData, ChartOptions } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

interface Props {
  data: ChartData<'bar'>
  options?: ChartOptions<'bar'>
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  height: 300,
})

const chartOptions = computed<ChartOptions<'bar'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
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
    },
  },
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        font: {
          size: 12,
        },
      },
    },
    y: {
      beginAtZero: true,
      ticks: {
        font: {
          size: 12,
        },
        precision: 0,
      },
    },
  },
  ...props.options,
}))
</script>

<template>
  <div :style="{ height: `${height}px` }">
    <Bar :data="data" :options="chartOptions" />
  </div>
</template>
