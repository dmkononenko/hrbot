<script setup lang="ts">
import { ref, onMounted } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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
import { employeesApi } from '@/api/client'
import type { Employee } from '@/types'
import { Plus, Pencil, Trash2 } from 'lucide-vue-next'

const employees = ref<Employee[]>([])
const loading = ref(true)
const isDialogOpen = ref(false)
const editingEmployee = ref<Employee | null>(null)
const isDeleteDialogOpen = ref(false)
const deletingEmployee = ref<Employee | null>(null)

const formData = ref({
  telegram_id: 0,
  telegram_username: '',
  first_name: '',
  last_name: '',
  start_date: '',
  branch: '',
  department: '',
  position: '',
  is_active: true,
})

const branches = [
  { value: 'head_office', label: 'Головной офис' },
  { value: 'faoa_asia', label: 'ФАОА "О!БАнк - Азия"' },
]

const departments = [
  { value: 'project_management', label: 'Проектное управление' },
  { value: 'hr_department', label: 'Отдел управления персоналом' },
]

const positions = ref<string[]>([])

const getBranchLabel = (value: string | null) => {
  if (!value) return '-'
  return branches.find(b => b.value === value)?.label ?? '-'
}

const getDepartmentLabel = (value: string | null) => {
  if (!value) return '-'
  return departments.find(d => d.value === value)?.label ?? '-'
}

const resetForm = () => {
  formData.value = {
    telegram_id: 0,
    telegram_username: '',
    first_name: '',
    last_name: '',
    start_date: new Date().toISOString().split('T')[0] ?? '',
    branch: '',
    department: '',
    position: '',
    is_active: true,
  }
  editingEmployee.value = null
}

const openCreateDialog = () => {
  resetForm()
  isDialogOpen.value = true
}

const openEditDialog = (employee: Employee) => {
  editingEmployee.value = employee
  formData.value = {
    telegram_id: employee.telegram_id,
    telegram_username: employee.telegram_username ?? '',
    first_name: employee.first_name,
    last_name: employee.last_name,
    start_date: employee.start_date,
    branch: employee.branch ?? '',
    department: employee.department ?? '',
    position: employee.position ?? '',
    is_active: employee.is_active,
  }
  isDialogOpen.value = true
}

const saveEmployee = async () => {
  try {
    if (editingEmployee.value) {
      await employeesApi.update(editingEmployee.value.id, formData.value)
    } else {
      await employeesApi.create(formData.value)
    }
    isDialogOpen.value = false
    resetForm()
    await loadEmployees()
  } catch (error) {
    console.error('Failed to save employee:', error)
  }
}

const confirmDelete = (employee: Employee) => {
  deletingEmployee.value = employee
  isDeleteDialogOpen.value = true
}

const deleteEmployee = async () => {
  if (!deletingEmployee.value) return
  try {
    await employeesApi.delete(deletingEmployee.value.id)
    isDeleteDialogOpen.value = false
    deletingEmployee.value = null
    await loadEmployees()
  } catch (error) {
    console.error('Failed to delete employee:', error)
  }
}

const loadEmployees = async () => {
  try {
    const response = await employeesApi.getAll()
    employees.value = response.data.employees || []
  } catch (error) {
    console.error('Failed to load employees:', error)
  } finally {
    loading.value = false
  }
}

onMounted(loadEmployees)
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight">Сотрудники</h1>
          <p class="text-muted-foreground">Управление списком сотрудников</p>
        </div>
        <Button @click="openCreateDialog">
          <Plus class="mr-2 h-4 w-4" />
          Добавить сотрудника
        </Button>
      </div>

      <!-- Employees Table -->
      <Card>
        <CardContent class="pt-6">
          <div v-if="loading" class="text-center py-8 text-muted-foreground">
            Загрузка...
          </div>
          <Table v-else>
            <TableHeader>
              <TableRow>
                <TableHead>Имя</TableHead>
                <TableHead>Филиал</TableHead>
                <TableHead>Департамент</TableHead>
                <TableHead>Должность</TableHead>
                <TableHead>Telegram</TableHead>
                <TableHead>Telegram ID</TableHead>
                <TableHead>Дата найма</TableHead>
                <TableHead>Статус</TableHead>
                <TableHead class="text-right">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="employees.length === 0">
                <TableCell colspan="9" class="text-center text-muted-foreground">
                  Нет сотрудников
                </TableCell>
              </TableRow>
              <TableRow v-for="employee in employees" :key="employee.id">
                <TableCell class="font-medium">
                  {{ employee.first_name }} {{ employee.last_name }}
                </TableCell>
                <TableCell>{{ getBranchLabel(employee.branch) }}</TableCell>
                <TableCell>{{ getDepartmentLabel(employee.department) }}</TableCell>
                <TableCell>{{ employee.position || '-' }}</TableCell>
                <TableCell>
                  {{ employee.telegram_username ? `@${employee.telegram_username}` : '-' }}
                </TableCell>
                <TableCell>{{ employee.telegram_id }}</TableCell>
                <TableCell>{{ employee.start_date }}</TableCell>
                <TableCell>
                  <Badge :variant="employee.is_active ? 'success' : 'secondary'">
                    {{ employee.is_active ? 'Активен' : 'Неактивен' }}
                  </Badge>
                </TableCell>
                <TableCell class="text-right">
                  <div class="flex justify-end gap-2">
                    <Button variant="ghost" size="icon" @click="openEditDialog(employee)">
                      <Pencil class="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" @click="confirmDelete(employee)">
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
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {{ editingEmployee ? 'Редактировать сотрудника' : 'Добавить сотрудника' }}
          </DialogTitle>
        </DialogHeader>

        <div class="space-y-4 py-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="first_name">Имя</Label>
              <Input id="first_name" v-model="formData.first_name" placeholder="Иван" />
            </div>
            <div class="space-y-2">
              <Label for="last_name">Фамилия</Label>
              <Input id="last_name" v-model="formData.last_name" placeholder="Иванов" />
            </div>
          </div>

          <div class="space-y-2">
            <Label for="telegram_id">Telegram ID</Label>
            <Input
              id="telegram_id"
              type="number"
              v-model="formData.telegram_id"
              placeholder="123456789"
              :disabled="!!editingEmployee"
            />
          </div>

          <div class="space-y-2">
            <Label for="telegram_username">Telegram Username</Label>
            <Input
              id="telegram_username"
              v-model="formData.telegram_username"
              placeholder="username (без @)"
            />
          </div>

          <div class="space-y-2">
            <Label for="start_date">Дата найма</Label>
            <Input
              id="start_date"
              type="date"
              v-model="formData.start_date"
            />
          </div>

          <div class="space-y-2">
            <Label for="branch">Филиал</Label>
            <Select v-model="formData.branch">
              <SelectTrigger id="branch">
                <SelectValue placeholder="Выберите филиал" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="branch in branches"
                  :key="branch.value"
                  :value="branch.value"
                >
                  {{ branch.label }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2">
            <Label for="department">Департамент</Label>
            <Select v-model="formData.department">
              <SelectTrigger id="department">
                <SelectValue placeholder="Выберите департамент" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="dept in departments"
                  :key="dept.value"
                  :value="dept.value"
                >
                  {{ dept.label }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2">
            <Label for="position">Должность</Label>
            <Input
              id="position"
              v-model="formData.position"
              placeholder="Введите должность"
            />
          </div>

          <div class="flex items-center space-x-2">
            <Switch
              :checked="formData.is_active"
              @update:checked="formData.is_active = $event"
            />
            <Label>Активен</Label>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="isDialogOpen = false">
            Отмена
          </Button>
          <Button
            @click="saveEmployee"
            :disabled="!formData.first_name || !formData.last_name || !formData.telegram_id"
          >
            {{ editingEmployee ? 'Сохранить' : 'Добавить' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog :open="isDeleteDialogOpen" @update:open="isDeleteDialogOpen = $event">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Удалить сотрудника?</DialogTitle>
        </DialogHeader>
        <p class="text-muted-foreground">
          Вы уверены, что хотите удалить сотрудника
          "{{ deletingEmployee?.first_name }} {{ deletingEmployee?.last_name }}"?
          Это действие нельзя отменить.
        </p>
        <DialogFooter>
          <Button variant="outline" @click="isDeleteDialogOpen = false">
            Отмена
          </Button>
          <Button variant="destructive" @click="deleteEmployee">
            Удалить
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </MainLayout>
</template>
