<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
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
import { responsesApi, surveysApi } from '@/api/client'
import type { SurveyResponse, Survey } from '@/types'
import { Eye, BarChart3 } from 'lucide-vue-next'

const router = useRouter()
const responses = ref<SurveyResponse[]>([])
const surveys = ref<Survey[]>([])
const loading = ref(true)
const selectedResponse = ref<SurveyResponse | null>(null)
const isDetailDialogOpen = ref(false)

const getSurveyTitle = (surveyId: number) => {
  const survey = surveys.value.find(s => s.id === surveyId)
  return survey?.title || `Опрос #${surveyId}`
}

const viewDetails = (response: SurveyResponse) => {
  selectedResponse.value = response
  isDetailDialogOpen.value = true
}

const viewSurveyResults = (surveyId: number) => {
  router.push(`/surveys/${surveyId}/results`)
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

const loadData = async () => {
  try {
    const [responsesRes, surveysRes] = await Promise.all([
      responsesApi.getAll(),
      surveysApi.getAll(),
    ])
    responses.value = responsesRes.data.responses || []
    surveys.value = surveysRes.data.surveys || []
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div>
        <h1 class="text-3xl font-bold tracking-tight">Результаты опросов</h1>
        <p class="text-muted-foreground">Все ответы на опросы</p>
      </div>

      <!-- Responses Table -->
      <Card>
        <CardContent class="pt-6">
          <div v-if="loading" class="text-center py-8 text-muted-foreground">
            Загрузка...
          </div>
          <Table v-else>
            <TableHeader>
              <TableRow>
                <TableHead>Сотрудник</TableHead>
                <TableHead>Опрос</TableHead>
                <TableHead>Статус</TableHead>
                <TableHead>Завершен</TableHead>
                <TableHead class="text-right">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="responses.length === 0">
                <TableCell colspan="5" class="text-center text-muted-foreground">
                  Нет ответов
                </TableCell>
              </TableRow>
              <TableRow v-for="response in responses" :key="response.id">
                <TableCell class="font-medium">
                  {{ response.employee?.first_name }} {{ response.employee?.last_name }}
                </TableCell>
                <TableCell>{{ getSurveyTitle(response.survey_id) }}</TableCell>
                <TableCell>
                  <Badge :variant="response.status === 'completed' ? 'success' : 'warning'">
                    {{ response.status === 'completed' ? 'Завершен' : 'Ожидает' }}
                  </Badge>
                </TableCell>
                <TableCell>{{ formatDate(response.completed_at) }}</TableCell>
                <TableCell class="text-right">
                  <div class="flex justify-end gap-2">
                    <Button variant="ghost" size="icon" @click="viewDetails(response)">
                      <Eye class="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      @click="viewSurveyResults(response.survey_id)"
                    >
                      <BarChart3 class="h-4 w-4" />
                    </Button>
                  </div>
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
          <DialogTitle>Детали ответа</DialogTitle>
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
              <p class="text-sm text-muted-foreground">Статус</p>
              <Badge :variant="selectedResponse.status === 'completed' ? 'success' : 'warning'">
                {{ selectedResponse.status === 'completed' ? 'Завершен' : 'Ожидает' }}
              </Badge>
            </div>
          </div>

          <div class="space-y-4">
            <h4 class="font-semibold">Ответы</h4>
            <div
              v-for="answer in selectedResponse.answers"
              :key="answer.id"
              class="border rounded-lg p-4"
            >
              <p class="font-medium mb-2">{{ answer.answer_text || 'Текстовый ответ' }}</p>
              <div v-if="answer.answer_options?.length" class="text-sm text-muted-foreground">
                Выбранные варианты: {{ answer.answer_options.join(', ') }}
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
