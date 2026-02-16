<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { BarChart, PieChart } from '@/components/ui/chart'
import { surveysApi } from '@/api/client'
import type { SurveyResultsResponse, ResponseResult, SurveyAnalyticsResponse, QuestionAnalytics } from '@/types'
import { ArrowLeft, Eye, Download, BarChart3 } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const surveyResults = ref<SurveyResultsResponse | null>(null)
const surveyAnalytics = ref<SurveyAnalyticsResponse | null>(null)
const loading = ref(true)
const analyticsLoading = ref(true)
const selectedResponse = ref<ResponseResult | null>(null)
const isDetailDialogOpen = ref(false)
const activeTab = ref<'responses' | 'analytics'>('responses')

const surveyId = Number(route.params.id)

const chartColors = [
  'rgba(59, 130, 246, 0.8)',   // blue
  'rgba(16, 185, 129, 0.8)',   // green
  'rgba(245, 158, 11, 0.8)',   // yellow
  'rgba(239, 68, 68, 0.8)',    // red
  'rgba(139, 92, 246, 0.8)',   // purple
  'rgba(236, 72, 153, 0.8)',   // pink
  'rgba(14, 165, 233, 0.8)',   // sky
  'rgba(168, 85, 247, 0.8)',   // violet
]

const getChartData = (question: QuestionAnalytics) => {
  if (!question.choice_distribution) return null

  return {
    labels: question.choice_distribution.map(d => d.option),
    datasets: [{
      data: question.choice_distribution.map(d => d.count),
      backgroundColor: chartColors.slice(0, question.choice_distribution.length),
    }],
  }
}

const viewDetails = (response: ResponseResult) => {
  selectedResponse.value = response
  isDetailDialogOpen.value = true
}

const switchTab = (tab: 'responses' | 'analytics') => {
  activeTab.value = tab
  if (tab === 'analytics' && !surveyAnalytics.value) {
    loadAnalytics()
  }
}

const formatDate = (dateString: string | null) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const goBack = () => {
  router.push('/surveys')
}

const exportToExcel = async () => {
  try {
    const response = await surveysApi.exportResults(surveyId)

    // Check if we got data
    if (!response.data) {
      alert('Ошибка: нет данных от сервера')
      return
    }

    const url = window.URL.createObjectURL(new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }))
    const link = document.createElement('a')
    link.href = url
    const surveyTitle = surveyResults.value?.survey_title || 'survey'
    link.setAttribute('download', `${surveyTitle}_${new Date().toISOString().split('T')[0]}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error: any) {
    console.error('Failed to export results:', error)
    alert(`Ошибка экспорта: ${error.response?.data?.detail || error.message || 'Неизвестная ошибка'}`)
  }
}

const loadResults = async () => {
  try {
    const response = await surveysApi.getResults(surveyId)
    surveyResults.value = response.data
  } catch (error) {
    console.error('Failed to load survey results:', error)
  } finally {
    loading.value = false
  }
}

const loadAnalytics = async () => {
  analyticsLoading.value = true
  try {
    const response = await surveysApi.getAnalytics(surveyId)
    surveyAnalytics.value = response.data
  } catch (error) {
    console.error('Failed to load survey analytics:', error)
  } finally {
    analyticsLoading.value = false
  }
}

onMounted(loadResults)
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <Button variant="ghost" size="icon" @click="goBack">
            <ArrowLeft class="h-4 w-4" />
          </Button>
          <div>
            <h1 class="text-3xl font-bold tracking-tight">
              {{ surveyResults?.survey_title || 'Результаты опроса' }}
            </h1>
            <p class="text-muted-foreground">Детальная статистика ответов</p>
          </div>
        </div>
        <Button @click="exportToExcel">
          <Download class="mr-2 h-4 w-4" />
          Экспорт в Excel
        </Button>
      </div>

      <!-- Stats -->
      <div class="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm font-medium">Всего ответов</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">{{ surveyResults?.total_responses || 0 }}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm font-medium">Процент завершения</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">
              {{ Math.round((surveyResults?.completion_rate || 0) * 100) }}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm font-medium">ID опроса</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">#{{ surveyId }}</div>
          </CardContent>
        </Card>
      </div>

      <!-- Tabs -->
      <div class="flex gap-2 border-b">
        <Button
          variant="ghost"
          :class="{ 'border-b-2 border-primary': activeTab === 'responses' }"
          @click="switchTab('responses')"
        >
          Ответы сотрудников
        </Button>
        <Button
          variant="ghost"
          :class="{ 'border-b-2 border-primary': activeTab === 'analytics' }"
          @click="switchTab('analytics')"
        >
          <BarChart3 class="mr-2 h-4 w-4" />
          Аналитика
        </Button>
      </div>

      <!-- Responses Tab -->
      <div v-if="activeTab === 'responses'">
      <!-- Responses Table -->
      <Card>
        <CardHeader>
          <CardTitle>Ответы сотрудников</CardTitle>
          <CardDescription>
            Список всех ответов на этот опрос
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div v-if="loading" class="text-center py-8 text-muted-foreground">
            Загрузка...
          </div>
          <Table v-else>
            <TableHeader>
              <TableRow>
                <TableHead>Сотрудник</TableHead>
                <TableHead>Telegram</TableHead>
                <TableHead>Завершен</TableHead>
                <TableHead>Ответов</TableHead>
                <TableHead class="text-right">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="!surveyResults?.responses?.length">
                <TableCell colspan="5" class="text-center text-muted-foreground">
                  Нет ответов
                </TableCell>
              </TableRow>
              <TableRow
                v-for="response in surveyResults?.responses"
                :key="response.response_id"
              >
                <TableCell class="font-medium">
                  {{ response.employee?.first_name }} {{ response.employee?.last_name }}
                </TableCell>
                <TableCell>
                  {{ response.employee?.telegram_username ? `@${response.employee.telegram_username}` : '-' }}
                </TableCell>
                <TableCell>{{ formatDate(response.completed_at) }}</TableCell>
                <TableCell>{{ response.answers?.length || 0 }}</TableCell>
                <TableCell class="text-right">
                  <Button variant="ghost" size="icon" @click="viewDetails(response)">
                    <Eye class="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      </div>

      <!-- Analytics Tab -->
      <div v-if="activeTab === 'analytics'">
        <div v-if="analyticsLoading" class="text-center py-8 text-muted-foreground">
          Загрузка аналитики...
        </div>

        <div v-else-if="!surveyAnalytics" class="text-center py-8 text-muted-foreground">
          Нет данных для аналитики
        </div>

        <div v-else class="space-y-6">
          <!-- Summary Stats -->
          <div class="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader class="pb-2">
                <CardTitle class="text-sm font-medium">Завершенные опросы</CardTitle>
              </CardHeader>
              <CardContent>
                <div class="text-2xl font-bold">{{ surveyAnalytics.completed_responses }}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader class="pb-2">
                <CardTitle class="text-sm font-medium">Процент завершения</CardTitle>
              </CardHeader>
              <CardContent>
                <div class="text-2xl font-bold">
                  {{ Math.round(surveyAnalytics.completion_rate * 100) }}%
                </div>
              </CardContent>
            </Card>
          </div>

          <!-- Questions Analytics -->
          <div v-for="question in surveyAnalytics.question_analytics" :key="question.question_id" class="space-y-4">
            <Card>
              <CardHeader>
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <CardTitle class="text-lg">{{ question.question_text }}</CardTitle>
                    <CardDescription>
                      <Badge variant="outline" class="mt-2">
                        {{ question.question_type === 'text' ? 'Текст' : question.question_type === 'single_choice' ? 'Один вариант' : 'Несколько вариантов' }}
                      </Badge>
                      <span class="ml-2 text-sm">
                        Всего ответов: {{ question.total_answers }}
                      </span>
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <!-- Choice questions -->
                <div v-if="question.choice_distribution && question.choice_distribution.length > 0">
                  <div class="grid gap-6 md:grid-cols-2">
                    <!-- Pie Chart -->
                    <div>
                      <h4 class="text-sm font-medium mb-4 text-muted-foreground">Распределение ответов</h4>
                      <PieChart
                        v-if="getChartData(question)"
                        :data="getChartData(question)!"
                        :height="280"
                      />
                    </div>

                    <!-- Bar Chart -->
                    <div>
                      <h4 class="text-sm font-medium mb-4 text-muted-foreground">Количество ответов</h4>
                      <BarChart
                        v-if="getChartData(question)"
                        :data="getChartData(question)!"
                        :height="280"
                      />
                    </div>
                  </div>

                  <!-- Stats Table -->
                  <div class="mt-6">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Вариант</TableHead>
                          <TableHead class="text-right">Количество</TableHead>
                          <TableHead class="text-right">Процент</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow v-for="item in question.choice_distribution" :key="item.option_id">
                          <TableCell class="font-medium">{{ item.option }}</TableCell>
                          <TableCell class="text-right">{{ item.count }}</TableCell>
                          <TableCell class="text-right">{{ item.percentage }}%</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </div>
                </div>

                <!-- Text questions -->
                <div v-else-if="question.text_responses && question.text_responses.length > 0">
                  <div class="space-y-3 max-h-96 overflow-y-auto">
                    <div
                      v-for="(response, index) in question.text_responses"
                      :key="index"
                      class="p-3 bg-muted rounded-lg"
                    >
                      <p class="text-sm">{{ response }}</p>
                    </div>
                  </div>
                </div>

                <!-- No answers -->
                <div v-else class="text-center py-8 text-muted-foreground">
                  Нет ответов на этот вопрос
                </div>
              </CardContent>
            </Card>
          </div>

          <!-- No questions -->
          <div v-if="!surveyAnalytics.question_analytics?.length" class="text-center py-8 text-muted-foreground">
            Нет вопросов в опросе
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Dialog -->
    <Dialog :open="isDetailDialogOpen" @update:open="isDetailDialogOpen = $event">
      <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Ответы сотрудника</DialogTitle>
        </DialogHeader>

        <div v-if="selectedResponse" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-muted-foreground">Сотрудник</p>
              <p class="font-medium">
                {{ selectedResponse.employee?.first_name }} {{ selectedResponse.employee?.last_name }}
              </p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Завершен</p>
              <p class="font-medium">{{ formatDate(selectedResponse.completed_at) }}</p>
            </div>
          </div>

          <div class="space-y-4">
            <h4 class="font-semibold">Ответы на вопросы</h4>
            <div
              v-for="(answer, index) in selectedResponse.answers"
              :key="index"
              class="border rounded-lg p-4"
            >
              <p class="font-medium mb-2">{{ answer.question_text }}</p>
              <Badge variant="outline" class="mb-2">
                {{ answer.question_type === 'text' ? 'Текст' : answer.question_type === 'single_choice' ? 'Один вариант' : 'Несколько вариантов' }}
              </Badge>
              <div v-if="answer.answer_text" class="mt-2 p-2 bg-muted rounded">
                {{ answer.answer_text }}
              </div>
              <div v-if="answer.answer_options?.length" class="mt-2 flex flex-wrap gap-2">
                <Badge v-for="option in answer.answer_options" :key="option" variant="secondary">
                  {{ option }}
                </Badge>
              </div>
            </div>
            <div v-if="!selectedResponse.answers?.length" class="text-center text-muted-foreground py-4">
              Нет ответов
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </MainLayout>
</template>
