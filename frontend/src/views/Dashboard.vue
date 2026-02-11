<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { surveysApi, employeesApi, responsesApi } from '@/api/client'
import type { Survey, Employee, SurveyResponse } from '@/types'
import { FileText, Users, CheckCircle, Clock } from 'lucide-vue-next'

const stats = ref({
  totalSurveys: 0,
  activeSurveys: 0,
  totalEmployees: 0,
  activeEmployees: 0,
  totalResponses: 0,
  completedResponses: 0,
  pendingResponses: 0,
})

const recentSurveys = ref<Survey[]>([])
const recentEmployees = ref<Employee[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [surveysRes, employeesRes, responsesRes] = await Promise.all([
      surveysApi.getAll(),
      employeesApi.getAll(),
      responsesApi.getAll(),
    ])

    const surveys = surveysRes.data.surveys || []
    const employees = employeesRes.data.employees || []
    const responses = responsesRes.data.responses || []

    stats.value = {
      totalSurveys: surveysRes.data.total || surveys.length,
      activeSurveys: surveys.filter((s: Survey) => s.is_active).length,
      totalEmployees: employeesRes.data.total || employees.length,
      activeEmployees: employees.filter((e: Employee) => e.is_active).length,
      totalResponses: responsesRes.data.total || responses.length,
      completedResponses: responses.filter((r: SurveyResponse) => r.status === 'completed').length,
      pendingResponses: responses.filter((r: SurveyResponse) => r.status === 'pending').length,
    }

    recentSurveys.value = surveys.slice(0, 5)
    recentEmployees.value = employees.slice(0, 5)
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <MainLayout>
    <div class="space-y-8">
      <!-- Header -->
      <div>
        <h1 class="text-3xl font-bold tracking-tight">Панель управления</h1>
        <p class="text-muted-foreground">Обзор системы HR опросов</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-sm font-medium">Всего опросов</CardTitle>
            <FileText class="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">{{ stats.totalSurveys }}</div>
            <p class="text-xs text-muted-foreground">
              {{ stats.activeSurveys }} активных
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-sm font-medium">Сотрудников</CardTitle>
            <Users class="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">{{ stats.totalEmployees }}</div>
            <p class="text-xs text-muted-foreground">
              {{ stats.activeEmployees }} активных
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-sm font-medium">Завершенные</CardTitle>
            <CheckCircle class="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">{{ stats.completedResponses }}</div>
            <p class="text-xs text-muted-foreground">
              из {{ stats.totalResponses }} ответов
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-sm font-medium">Ожидают</CardTitle>
            <Clock class="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">{{ stats.pendingResponses }}</div>
            <p class="text-xs text-muted-foreground">
              незавершенных опросов
            </p>
          </CardContent>
        </Card>
      </div>

      <!-- Recent Data -->
      <div class="grid gap-6 md:grid-cols-2">
        <!-- Recent Surveys -->
        <Card>
          <CardHeader>
            <CardTitle>Последние опросы</CardTitle>
          </CardHeader>
          <CardContent>
            <div v-if="loading" class="text-center py-4 text-muted-foreground">
              Загрузка...
            </div>
            <div v-else-if="recentSurveys.length === 0" class="text-center py-4 text-muted-foreground">
              Нет опросов
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="survey in recentSurveys"
                :key="survey.id"
                class="flex items-center justify-between"
              >
                <div>
                  <p class="font-medium">{{ survey.title }}</p>
                  <p class="text-sm text-muted-foreground">
                    {{ survey.questions?.length || 0 }} вопросов
                  </p>
                </div>
                <Badge :variant="survey.is_active ? 'success' : 'secondary'">
                  {{ survey.is_active ? 'Активен' : 'Неактивен' }}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Recent Employees -->
        <Card>
          <CardHeader>
            <CardTitle>Последние сотрудники</CardTitle>
          </CardHeader>
          <CardContent>
            <div v-if="loading" class="text-center py-4 text-muted-foreground">
              Загрузка...
            </div>
            <div v-else-if="recentEmployees.length === 0" class="text-center py-4 text-muted-foreground">
              Нет сотрудников
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="employee in recentEmployees"
                :key="employee.id"
                class="flex items-center justify-between"
              >
                <div>
                  <p class="font-medium">{{ employee.first_name }} {{ employee.last_name }}</p>
                  <p class="text-sm text-muted-foreground">
                    @{{ employee.telegram_username || 'нет username' }}
                  </p>
                </div>
                <Badge :variant="employee.is_active ? 'success' : 'secondary'">
                  {{ employee.is_active ? 'Активен' : 'Неактивен' }}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </MainLayout>
</template>
