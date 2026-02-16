<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { employeesApi } from '@/api/client'
import type { SurveyResultsResponse, ResponseResult } from '@/types'
import { ArrowLeft, Eye } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const employeeResponses = ref<SurveyResultsResponse | null>(null)
const loading = ref(true)
const selectedResponse = ref<ResponseResult | null>(null)
const isDetailDialogOpen = ref(false)

const employeeId = Number(route.params.id)

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
  router.push('/employees')
}

const loadResponses = async () => {
  try {
    const response = await employeesApi.getResponses(employeeId)
    employeeResponses.value = response.data
  } catch (error) {
    console.error('Failed to load employee responses:', error)
  } finally {
    loading.value = false
  }
}

onMounted(loadResponses)
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
            {{ employeeResponses?.survey_title || 'Ответы сотрудника' }}
          </h1>
          <p class="text-muted-foreground">Все заполненные опросы</p>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm font-medium">Всего опросов</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">{{ employeeResponses?.total_responses || 0 }}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm font-medium">Завершено</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">
              {{ employeeResponses?.responses?.filter(r => r.completed_at).length || 0 }}
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Responses List -->
      <div v-if="loading" class="text-center py-8 text-muted-foreground">
        Загрузка...
      </div>

      <div v-else-if="!employeeResponses?.responses?.length" class="text-center py-8 text-muted-foreground">
        У сотрудника нет заполненных опросов
      </div>

      <div v-else class="space-y-4">
        <Card
          v-for="response in employeeResponses?.responses"
          :key="response.response_id"
        >
          <CardHeader>
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <CardTitle class="text-lg">
                  {{ response.survey_title }}
                </CardTitle>
                <CardDescription class="mt-2">
                  <div class="flex flex-wrap gap-2">
                    <Badge :variant="response.completed_at ? 'success' : 'secondary'">
                      {{ response.completed_at ? 'Завершён' : 'В процессе' }}
                    </Badge>
                    <span class="text-sm">
                      {{ formatDate(response.completed_at) }}
                    </span>
                  </div>
                </CardDescription>
              </div>
              <Button variant="ghost" size="icon" @click="viewDetails(response)">
                <Eye class="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div class="space-y-2">
              <div class="text-sm text-muted-foreground">
                Ответов на вопросы: {{ response.answers?.length || 0 }}
              </div>
              <div class="flex flex-wrap gap-2">
                <Badge
                  v-for="(answer, index) in response.answers?.slice(0, 3)"
                  :key="index"
                  variant="outline"
                  class="text-xs"
                >
                  {{ answer.question_type === 'text' ? 'Текст' : answer.question_type === 'single_choice' ? 'Один вариант' : 'Несколько вариантов' }}
                </Badge>
                <Badge v-if="response.answers?.length > 3" variant="outline" class="text-xs">
                  +{{ response.answers.length - 3 }}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- Detail Dialog -->
    <Dialog :open="isDetailDialogOpen" @update:open="isDetailDialogOpen = $event">
      <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Ответы на опрос: {{ selectedResponse?.survey_title }}</DialogTitle>
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
              <div v-if="!answer.answer_text && !answer.answer_options?.length" class="mt-2 text-muted-foreground text-sm">
                Нет ответа
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
