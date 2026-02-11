<script setup lang="ts">
import { cn } from '@/lib/utils'
import { DialogTitle, type DialogTitleProps } from 'radix-vue'

interface Props extends DialogTitleProps {
  class?: string
}

const props = defineProps<Props>()
</script>

<template>
  <DialogTitle :class="cn('text-lg font-semibold leading-none tracking-tight', props.class)">
    <slot />
  </DialogTitle>
</template>
