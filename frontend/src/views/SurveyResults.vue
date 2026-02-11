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
import { surveysApi } from '@/api/client'
import type { SurveyResultsResponse, ResponseResult } from '@/types'
import { ArrowLeft, Eye } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const surveyResults = ref<SurveyResultsResponse | null>(null)
const loading = ref(true)
const selectedResponse = ref<ResponseResult | null>(null)
const isDetailDialogOpen = ref(false)

const surveyId = Number(route.params.id)

const viewDetails = (response: ResponseResult) => {
  selectedResponse.value = response
  isDetailDialogOpen.value = true
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

onMounted(loadResults)
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
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
