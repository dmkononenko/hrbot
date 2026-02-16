<script setup lang="ts">
import { useRoute, RouterLink } from 'vue-router'
import { LayoutDashboard, FileText, Users, BarChart3 } from 'lucide-vue-next'

const route = useRoute()

const navItems = [
  { path: '/dashboard', label: 'Панель', icon: LayoutDashboard },
  { path: '/', label: 'Опросы', icon: FileText },
  { path: '/employees', label: 'Сотрудники', icon: Users },
  { path: '/results', label: 'Результаты', icon: BarChart3 },
]

const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="sticky top-0 z-40 border-b bg-background">
      <div class="container flex h-16 items-center justify-between px-4">
        <div class="flex items-center gap-6">
          <RouterLink to="/dashboard" class="flex items-center gap-2">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <LayoutDashboard class="h-5 w-5" />
            </div>
            <span class="text-xl font-bold">HR Bot Admin</span>
          </RouterLink>

          <nav class="hidden md:flex items-center gap-1">
            <RouterLink
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              :class="[
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive(item.path)
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              ]"
            >
              <component :is="item.icon" class="h-4 w-4" />
              {{ item.label }}
            </RouterLink>
          </nav>
        </div>
      </div>
    </header>

    <!-- Mobile navigation -->
    <nav class="md:hidden fixed bottom-0 left-0 right-0 z-40 border-t bg-background">
      <div class="flex items-center justify-around py-2">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex flex-col items-center gap-1 px-3 py-2 text-xs font-medium transition-colors',
            isActive(item.path)
              ? 'text-primary'
              : 'text-muted-foreground'
          ]"
        >
          <component :is="item.icon" class="h-5 w-5" />
          {{ item.label }}
        </RouterLink>
      </div>
    </nav>

    <!-- Main content -->
    <main class="container px-4 py-8 pb-24 md:pb-8">
      <slot />
    </main>
  </div>
</template>
