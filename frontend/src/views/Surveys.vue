<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
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
  DialogFooter,
} from '@/components/ui/dialog'
import { surveysApi, employeesApi, botApi } from '@/api/client'
import type { Survey, QuestionType, Employee } from '@/types'
import { Plus, Pencil, Trash2, BarChart3, X, Users, Check } from 'lucide-vue-next'
import { Checkbox } from '@/components/ui/checkbox'

const router = useRouter()
const surveys = ref<Survey[]>([])
const loading = ref(true)
const isDialogOpen = ref(false)
const editingSurvey = ref<Survey | null>(null)
const isDeleteDialogOpen = ref(false)
const deletingSurvey = ref<Survey | null>(null)

// Assignment dialog state
const isAssignDialogOpen = ref(false)
const assigningSurvey = ref<Survey | null>(null)
const employees = ref<Employee[]>([])
const employeesLoading = ref(false)
const selectedEmployeeIds = ref<number[]>([])
const assignmentStatus = ref<Record<number, 'pending' | 'assigned' | 'error'>>({})
const assignmentErrors = ref<Record<number, string>>({})

const formData = ref({
  title: '',
  description: '',
  days_after_start: 90,
  is_active: true,
  questions: [] as {
    question_text: string
    question_type: QuestionType
    order_index: number
    is_required: boolean
    options: { option_text: string; order_index: number }[]
  }[],
})

const resetForm = () => {
  formData.value = {
    title: '',
    description: '',
    days_after_start: 90,
    is_active: true,
    questions: [],
  }
  editingSurvey.value = null
}

const openCreateDialog = () => {
  resetForm()
  isDialogOpen.value = true
}

const openEditDialog = (survey: Survey) => {
  editingSurvey.value = survey
  formData.value = {
    title: survey.title,
    description: survey.description,
    days_after_start: survey.days_after_start,
    is_active: survey.is_active,
    questions: survey.questions?.map(q => ({
      question_text: q.question_text,
      question_type: q.question_type,
      order_index: q.order_index,
      is_required: q.is_required,
      options: q.options?.map(o => ({
        option_text: o.option_text,
        order_index: o.order_index
      })) || [],
    })) || [],
  }
  isDialogOpen.value = true
}

const addQuestion = () => {
  formData.value.questions.push({
    question_text: '',
    question_type: 'single_choice',
    order_index: formData.value.questions.length,
    is_required: true,
    options: [
      { option_text: '', order_index: 0 },
      { option_text: '', order_index: 1 },
    ],
  })
}

const removeQuestion = (index: number) => {
  formData.value.questions.splice(index, 1)
  formData.value.questions.forEach((q, i) => {
    q.order_index = i
  })
}

const addOption = (questionIndex: number) => {
  const question = formData.value.questions[questionIndex]
  if (question) {
    question.options.push({
      option_text: '',
      order_index: question.options.length,
    })
  }
}

const removeOption = (questionIndex: number, optionIndex: number) => {
  const question = formData.value.questions[questionIndex]
  if (question) {
    question.options.splice(optionIndex, 1)
    question.options.forEach((o, i) => {
      o.order_index = i
    })
  }
}

const saveSurvey = async () => {
  try {
    if (editingSurvey.value) {
      await surveysApi.update(editingSurvey.value.id, formData.value)
    } else {
      await surveysApi.create(formData.value)
    }
    isDialogOpen.value = false
    resetForm()
    await loadSurveys()
  } catch (error) {
    console.error('Failed to save survey:', error)
  }
}

const confirmDelete = (survey: Survey) => {
  deletingSurvey.value = survey
  isDeleteDialogOpen.value = true
}

const deleteSurvey = async () => {
  if (!deletingSurvey.value) return
  try {
    await surveysApi.delete(deletingSurvey.value.id)
    isDeleteDialogOpen.value = false
    deletingSurvey.value = null
    await loadSurveys()
  } catch (error) {
    console.error('Failed to delete survey:', error)
  }
}

const viewResults = (surveyId: number) => {
  router.push(`/surveys/${surveyId}/results`)
}

// Assignment functions
const openAssignDialog = async (survey: Survey) => {
  assigningSurvey.value = survey
  selectedEmployeeIds.value = []
  assignmentStatus.value = {}
  assignmentErrors.value = {}
  isAssignDialogOpen.value = true
  await loadEmployees()
}

const loadEmployees = async () => {
  employeesLoading.value = true
  try {
    const response = await employeesApi.getAll()
    employees.value = response.data.employees || []
  } catch (error) {
    console.error('Failed to load employees:', error)
  } finally {
    employeesLoading.value = false
  }
}

const toggleSelectAll = () => {
  if (selectedEmployeeIds.value.length === employees.value.length) {
    selectedEmployeeIds.value = []
  } else {
    selectedEmployeeIds.value = employees.value
      .filter(e => assignmentStatus.value[e.id] !== 'assigned')
      .map(e => e.id)
  }
}

const toggleEmployee = (employeeId: number) => {
  const index = selectedEmployeeIds.value.indexOf(employeeId)
  if (index > -1) {
    selectedEmployeeIds.value.splice(index, 1)
  } else {
    selectedEmployeeIds.value.push(employeeId)
  }
}

const assignToSelected = async () => {
  if (!assigningSurvey.value || selectedEmployeeIds.value.length === 0) return

  const surveyId = assigningSurvey.value.id
  let successCount = 0

  for (const employeeId of selectedEmployeeIds.value) {
    const employee = employees.value.find(e => e.id === employeeId)
    if (!employee) continue

    assignmentStatus.value[employeeId] = 'pending'

    try {
      await botApi.initiateSurvey({
        employee_telegram_id: employee.telegram_id,
        survey_id: surveyId
      })
      assignmentStatus.value[employeeId] = 'assigned'
      successCount++
    } catch (error: any) {
      assignmentStatus.value[employeeId] = 'error'
      assignmentErrors.value[employeeId] = error.response?.data?.detail || 'Ошибка назначения'
    }
  }

  // Remove assigned from selection
  selectedEmployeeIds.value = selectedEmployeeIds.value.filter(
    id => assignmentStatus.value[id] !== 'assigned'
  )
}

const loadSurveys = async () => {
  try {
    const response = await surveysApi.getAll()
    surveys.value = response.data.surveys || []
  } catch (error) {
    console.error('Failed to load surveys:', error)
  } finally {
    loading.value = false
  }
}

onMounted(loadSurveys)
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight">Опросы</h1>
          <p class="text-muted-foreground">Управление опросами для сотрудников</p>
        </div>
        <Button @click="openCreateDialog">
          <Plus class="mr-2 h-4 w-4" />
          Создать опрос
        </Button>
      </div>

      <!-- Surveys Table -->
      <Card>
        <CardContent class="pt-6">
          <div v-if="loading" class="text-center py-8 text-muted-foreground">
            Загрузка...
          </div>
          <Table v-else>
            <TableHeader>
              <TableRow>
                <TableHead>Название</TableHead>
                <TableHead>Описание</TableHead>
                <TableHead>Дней после найма</TableHead>
                <TableHead>Вопросов</TableHead>
                <TableHead>Статус</TableHead>
                <TableHead class="text-right">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="surveys.length === 0">
                <TableCell colspan="6" class="text-center text-muted-foreground">
                  Нет опросов
                </TableCell>
              </TableRow>
              <TableRow v-for="survey in surveys" :key="survey.id">
                <TableCell class="font-medium">{{ survey.title }}</TableCell>
                <TableCell class="max-w-xs truncate">{{ survey.description }}</TableCell>
                <TableCell>{{ survey.days_after_start }}</TableCell>
                <TableCell>{{ survey.questions?.length || 0 }}</TableCell>
                <TableCell>
                  <Badge :variant="survey.is_active ? 'success' : 'secondary'">
                    {{ survey.is_active ? 'Активен' : 'Неактивен' }}
                  </Badge>
                </TableCell>
                <TableCell class="text-right">
                  <div class="flex justify-end gap-2">
                    <Button variant="ghost" size="icon" @click="openAssignDialog(survey)" title="Назначить сотрудникам">
                      <Users class="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" @click="viewResults(survey.id)">
                      <BarChart3 class="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" @click="openEditDialog(survey)">
                      <Pencil class="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" @click="confirmDelete(survey)">
                      <Trash2 class="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>

    <!-- Create/Edit Dialog -->
    <Dialog :open="isDialogOpen" @update:open="isDialogOpen = $event">
      <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {{ editingSurvey ? 'Редактировать опрос' : 'Создать опрос' }}
          </DialogTitle>
        </DialogHeader>

        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <Label for="title">Название</Label>
            <Input id="title" v-model="formData.title" placeholder="Название опроса" />
          </div>

          <div class="space-y-2">
            <Label for="description">Описание</Label>
            <Textarea
              id="description"
              v-model="formData.description"
              placeholder="Описание опроса"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="days">Дней после найма</Label>
              <Input
                id="days"
                type="number"
                v-model="formData.days_after_start"
              />
            </div>

            <div class="flex items-center space-x-2 pt-8">
              <Switch
                :checked="formData.is_active"
                @update:checked="formData.is_active = $event"
              />
              <Label>Активен</Label>
            </div>
          </div>

          <!-- Questions -->
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <Label>Вопросы</Label>
              <Button variant="outline" size="sm" @click="addQuestion">
                <Plus class="mr-2 h-4 w-4" />
                Добавить вопрос
              </Button>
            </div>

            <div
              v-for="(question, qIndex) in formData.questions"
              :key="qIndex"
              class="border rounded-lg p-4 space-y-4"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 space-y-4">
                  <div class="space-y-2">
                    <Label :for="`question-${qIndex}`">Вопрос {{ qIndex + 1 }}</Label>
                    <Input
                      :id="`question-${qIndex}`"
                      v-model="question.question_text"
                      placeholder="Текст вопроса"
                    />
                  </div>

                  <div class="grid grid-cols-2 gap-4">
                    <div class="space-y-2">
                      <Label>Тип</Label>
                      <select
                        v-model="question.question_type"
                        class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      >
                        <option value="text">Текст</option>
                        <option value="single_choice">Один вариант</option>
                        <option value="multiple_choice">Несколько вариантов</option>
                      </select>
                    </div>

                    <div class="flex items-center space-x-2 pt-8">
                      <Switch
                        :checked="question.is_required"
                        @update:checked="question.is_required = $event"
                      />
                      <Label>Обязательный</Label>
                    </div>
                  </div>

                  <!-- Options for choice questions -->
                  <div
                    v-if="question.question_type !== 'text'"
                    class="space-y-2"
                  >
                    <Label>Варианты ответов</Label>
                    <div
                      v-for="(option, oIndex) in question.options"
                      :key="oIndex"
                      class="flex gap-2"
                    >
                      <Input
                        v-model="option.option_text"
                        :placeholder="`Вариант ${oIndex + 1}`"
                        class="flex-1"
                      />
                      <Button
                        variant="ghost"
                        size="icon"
                        @click="removeOption(qIndex, oIndex)"
                        :disabled="question.options.length <= 2"
                      >
                        <X class="h-4 w-4" />
                      </Button>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      @click="addOption(qIndex)"
                    >
                      <Plus class="mr-2 h-4 w-4" />
                      Добавить вариант
                    </Button>
                  </div>
                </div>

                <Button
                  variant="ghost"
                  size="icon"
                  @click="removeQuestion(qIndex)"
                  class="ml-2"
                >
                  <Trash2 class="h-4 w-4 text-destructive" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="isDialogOpen = false">
            Отмена
          </Button>
          <Button @click="saveSurvey" :disabled="!formData.title">
            {{ editingSurvey ? 'Сохранить' : 'Создать' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog :open="isDeleteDialogOpen" @update:open="isDeleteDialogOpen = $event">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Удалить опрос?</DialogTitle>
        </DialogHeader>
        <p class="text-muted-foreground">
          Вы уверены, что хотите удалить опрос "{{ deletingSurvey?.title }}"?
          Это действие нельзя отменить.
        </p>
        <DialogFooter>
          <Button variant="outline" @click="isDeleteDialogOpen = false">
            Отмена
          </Button>
          <Button variant="destructive" @click="deleteSurvey">
            Удалить
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Assignment Dialog -->
    <Dialog :open="isAssignDialogOpen" @update:open="isAssignDialogOpen = $event">
      <DialogContent class="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Назначить опрос: {{ assigningSurvey?.title }}</DialogTitle>
        </DialogHeader>

        <div class="space-y-4 py-4">
          <div class="flex items-center justify-between">
            <Button variant="outline" size="sm" @click="toggleSelectAll">
              {{ selectedEmployeeIds.length === employees.length ? 'Снять выбор' : 'Выбрать всех' }}
            </Button>
            <span class="text-sm text-muted-foreground">
              Выбрано: {{ selectedEmployeeIds.length }}
            </span>
          </div>

          <div v-if="employeesLoading" class="text-center py-8 text-muted-foreground">
            Загрузка сотрудников...
          </div>

          <Table v-else>
            <TableHeader>
              <TableRow>
                <TableHead class="w-12"></TableHead>
                <TableHead>Имя</TableHead>
                <TableHead>Telegram</TableHead>
                <TableHead>Дата найма</TableHead>
                <TableHead>Дней работы</TableHead>
                <TableHead>Статус</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="employees.length === 0">
                <TableCell colspan="6" class="text-center text-muted-foreground">
                  Нет сотрудников
                </TableCell>
              </TableRow>
              <TableRow v-for="employee in employees" :key="employee.id">
                <TableCell>
                  <Checkbox
                    v-if="assignmentStatus[employee.id] !== 'assigned'"
                    :checked="selectedEmployeeIds.includes(employee.id)"
                    @update:checked="toggleEmployee(employee.id)"
                    :disabled="assignmentStatus[employee.id] === 'pending'"
                  />
                  <Check v-else class="h-4 w-4 text-green-600" />
                </TableCell>
                <TableCell class="font-medium">
                  {{ employee.first_name }} {{ employee.last_name }}
                </TableCell>
                <TableCell>@{{ employee.telegram_username || employee.telegram_id }}</TableCell>
                <TableCell>{{ employee.start_date }}</TableCell>
                <TableCell>
                  {{ Math.floor((new Date().getTime() - new Date(employee.start_date).getTime()) / (1000 * 60 * 60 * 24)) }}
                </TableCell>
                <TableCell>
                  <span v-if="assignmentStatus[employee.id] === 'assigned'" class="text-green-600">
                    Назначено
                  </span>
                  <span v-else-if="assignmentStatus[employee.id] === 'error'" class="text-red-600">
                    {{ assignmentErrors[employee.id] }}
                  </span>
                  <span v-else-if="assignmentStatus[employee.id] === 'pending'" class="text-muted-foreground">
                    Назначение...
                  </span>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="isAssignDialogOpen = false">
            Закрыть
          </Button>
          <Button
            @click="assignToSelected"
            :disabled="selectedEmployeeIds.length === 0"
          >
            Назначить {{ selectedEmployeeIds.length > 0 ? `${selectedEmployeeIds.length} сотрудникам` : '' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </MainLayout>
</template>
