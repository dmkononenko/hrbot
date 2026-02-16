<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { surveysApi, employeesApi, responsesApi } from '@/api/client'
import type { Survey, Employee, SurveyResponse } from '@/types'
import { FileText, Users, CheckCircle, Clock, ArrowRight } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

const router = useRouter()
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
const recentResponses = ref<SurveyResponse[]>([])
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
    recentResponses.value = responses.slice(0, 5)
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    loading.value = false
  }
})

const goToSurveys = () => router.push('/')
const goToEmployees = () => router.push('/employees')
const goToResults = () => router.push('/results')
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
        <Card class="cursor-pointer hover:bg-accent/50 transition-colors" @click="goToSurveys">
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

        <Card class="cursor-pointer hover:bg-accent/50 transition-colors" @click="goToEmployees">
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

        <Card class="cursor-pointer hover:bg-accent/50 transition-colors" @click="goToResults">
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
      <div class="grid gap-6 lg:grid-cols-2">
        <!-- Recent Surveys -->
        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <div>
                <CardTitle>Последние опросы</CardTitle>
                <CardDescription>Недавно добавленные опросы</CardDescription>
              </div>
              <Button variant="ghost" size="icon" @click="goToSurveys">
                <ArrowRight class="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div v-if="loading" class="text-center py-4 text-muted-foreground">
              Загрузка...
            </div>
            <div v-else-if="recentSurveys.length === 0" class="text-center py-8 text-muted-foreground">
              Нет опросов
              <div class="mt-2">
                <Button variant="outline" size="sm" @click="goToSurveys">
                  Создать первый опрос
                </Button>
              </div>
            </div>
            <Table v-else>
              <TableHeader>
                <TableRow>
                  <TableHead>Название</TableHead>
                  <TableHead>Вопросов</TableHead>
                  <TableHead>Статус</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="survey in recentSurveys" :key="survey.id">
                  <TableCell class="font-medium">{{ survey.title }}</TableCell>
                  <TableCell>{{ survey.questions?.length || 0 }}</TableCell>
                  <TableCell>
                    <Badge :variant="survey.is_active ? 'success' : 'secondary'">
                      {{ survey.is_active ? 'Активен' : 'Неактивен' }}
                    </Badge>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <!-- Recent Employees -->
        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <div>
                <CardTitle>Последние сотрудники</CardTitle>
                <CardDescription>Недавно добавленные сотрудники</CardDescription>
              </div>
              <Button variant="ghost" size="icon" @click="goToEmployees">
                <ArrowRight class="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div v-if="loading" class="text-center py-4 text-muted-foreground">
              Загрузка...
            </div>
            <div v-else-if="recentEmployees.length === 0" class="text-center py-8 text-muted-foreground">
              Нет сотрудников
            </div>
            <Table v-else>
              <TableHeader>
                <TableRow>
                  <TableHead>Имя</TableHead>
                  <TableHead>Telegram</TableHead>
                  <TableHead>Статус</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="employee in recentEmployees" :key="employee.id">
                  <TableCell class="font-medium">
                    {{ employee.first_name }} {{ employee.last_name }}
                  </TableCell>
                  <TableCell>@{{ employee.telegram_username || employee.telegram_id }}</TableCell>
                  <TableCell>
                    <Badge :variant="employee.is_active ? 'success' : 'secondary'">
                      {{ employee.is_active ? 'Активен' : 'Неактивен' }}
                    </Badge>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      <!-- Recent Responses -->
      <Card v-if="recentResponses.length > 0">
        <CardHeader>
          <div class="flex items-center justify-between">
            <div>
              <CardTitle>Последние ответы</CardTitle>
              <CardDescription>Недавно полученные ответы на опросы</CardDescription>
            </div>
            <Button variant="ghost" size="icon" @click="goToResults">
              <ArrowRight class="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Сотрудник</TableHead>
                <TableHead>Опрос</TableHead>
                <TableHead>Статус</TableHead>
                <TableHead>Дата</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="response in recentResponses" :key="response.id">
                <TableCell class="font-medium">
                  {{ response.employee?.first_name }} {{ response.employee?.last_name }}
                </TableCell>
                <TableCell>Опрос #{{ response.survey_id }}</TableCell>
                <TableCell>
                  <Badge
                    :variant="response.status === 'completed' ? 'success' : 'secondary'"
                  >
                    {{ response.status === 'completed' ? 'Завершен' : 'В процессе' }}
                  </Badge>
                </TableCell>
                <TableCell class="text-muted-foreground">
                  {{ response.completed_at ? new Date(response.completed_at).toLocaleDateString('ru-RU') : '-' }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  </MainLayout>
</template>
