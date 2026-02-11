# shadcn/ui Правила использования

## Обзор

Этот документ содержит правила и рекомендации по использованию компонентов и стилей shadcn/ui в проекте Jira Combiner. Проект уже настроен для работы с shadcn/ui, Vue 3 и Tailwind 3 CSS.

## Структура компонентов

### Расположение компонентов

- Все UI компоненты shadcn/ui находятся в директории `src/components/ui/`
- Каждый компонент расположен в отдельном файле с расширением `.vue`
- Название файла компонента должно совпадать с названием компонента в PascalCase

### Импорт компонентов

```vue
<script setup lang="ts">
import Button from '@/components/ui/Button.vue';
import Card from '@/components/ui/Card.vue';
import CardContent from '@/components/ui/CardContent.vue';
import Switch from '@/components/ui/Switch.vue';
</script>
```

## Использование утилит

### Функция cn()

Для объединения CSS классов используйте утилиту `cn()` из `@/lib/utils`:

```vue
<script setup lang="ts">
import { cn } from '@/lib/utils';
</script>

<template>
  <div :class="cn('base-class', 'additional-class', conditionalClass)">Содержимое</div>
</template>
```

## Использование стилей

### Цветовая схема

Используйте CSS переменные, определенные в `src/styles/globals.css`:

- `primary`, `primary-foreground`
- `secondary`, `secondary-foreground`
- `muted`, `muted-foreground`
- `accent`, `accent-foreground`
- `destructive`, `destructive-foreground`
- `border`, `input`, `ring`, `background`, `foreground`, `card`, `popover`

### Примеры использования цветов

```vue
<template>
  <div class="bg-card text-card-foreground border-border">
    <h2 class="text-foreground">Заголовок</h2>
    <p class="text-muted-foreground">Описание</p>
    <Button class="bg-primary text-primary-foreground">Кнопка</Button>
  </div>
</template>
```

### Темная тема

Проект поддерживает темную тему через класс `.dark` на корневом элементе. Все компоненты автоматически адаптируются под выбранную тему.

## Рекомендации по использованию компонентов

### Button

```vue
<template>
  <!-- Варианты кнопок -->
  <Button>По умолчанию</Button>
  <Button variant="destructive">Удалить</Button>
  <Button variant="outline">Контурная</Button>
  <Button variant="secondary">Вторичная</Button>
  <Button variant="ghost">Прозрачная</Button>
  <Button variant="link">Ссылка</Button>

  <!-- Размеры -->
  <Button size="sm">Маленькая</Button>
  <Button size="default">Обычная</Button>
  <Button size="lg">Большая</Button>
  <Button size="icon">
    <Icon name="plus" />
  </Button>
</template>
```

### Card

```vue
<template>
  <Card>
    <CardHeader>
      <CardTitle>Заголовок карточки</CardTitle>
      <CardDescription>Описание карточки</CardDescription>
    </CardHeader>
    <CardContent> Содержимое карточки </CardContent>
    <CardFooter>
      <Button>Действие</Button>
    </CardFooter>
  </Card>
</template>
```

### Switch

```vue
<template>
  <div class="flex items-center space-x-2">
    <Switch id="feature" v-model:checked="enabled" />
    <Label for="feature">Включить функцию</Label>
  </div>
</template>
```

### Dialog

```vue
<template>
  <Dialog>
    <DialogTrigger as-child>
      <Button>Открыть диалог</Button>
    </DialogTrigger>
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Заголовок диалога</DialogTitle>
        <DialogDescription> Описание диалога </DialogDescription>
      </DialogHeader>
      <!-- Содержимое диалога -->
    </DialogContent>
  </Dialog>
</template>
```

## Создание новых компонентов

При создании новых компонентов на основе shadcn/ui:

1. Используйте `class-variance-authority` для определения вариантов компонента
2. Применяйте функцию `cn()` для объединения классов
3. Определяйте типы для свойств компонента
4. Следуйте структуре существующих компонентов

```vue
<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue';
import { type VariantProps, cva } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const componentVariants = cva('базовые-классы', {
  variants: {
    variant: {
      default: 'классы-для-варианта-по-умолчанию',
      secondary: 'классы-для-вторичного-варианта',
    },
    size: {
      default: 'классы-для-размера-по-умолчанию',
      sm: 'классы-для-маленького-размера',
    },
  },
  defaultVariants: {
    variant: 'default',
    size: 'default',
  },
});

interface ComponentProps {
  variant?: VariantProps<typeof componentVariants>['variant'];
  size?: VariantProps<typeof componentVariants>['size'];
  class?: HTMLAttributes['class'];
}

const props = withDefaults(defineProps<ComponentProps>(), {
  variant: 'default',
  size: 'default',
});

const componentClass = computed(() =>
  cn(componentVariants({ variant: props.variant, size: props.size }), props.class)
);
</script>

<template>
  <div :class="componentClass">
    <slot />
  </div>
</template>
```

## Рекомендации

- Используйте семантические цвета из палитры shadcn/ui вместо жестко заданных цветов
- При необходимости кастомизации компонентов создавайте новые варианты через `class-variance-authority`
- Для анимаций и переходов используйте классы Tailwind CSS (`transition-*`, `duration-*`)
- Для адаптивного дизайна используйте адаптивные префиксы Tailwind (`sm:`, `md:`, `lg:`)
- При работе с формами используйте компоненты Label, Input и другие форм-компоненты для доступности
- Для иконок используйте библиотеку `lucide-vue-next`, уже подключенную в проекте

## Пример использования в реальном компоненте

```vue
<template>
  <div class="rounded-lg border bg-card p-6 shadow-sm border-border transition-colors duration-300">
    <h2 class="mb-6 text-xl font-semibold text-foreground transition-colors duration-300">
      Настройки
    </h2>

    <div class="mb-6 flex items-center justify-between gap-4">
      <div class="flex-1">
        <Label for="feature" class="text-base font-medium"> Включить функцию </Label>
        <p class="mt-1 text-sm text-muted-foreground transition-colors duration-300">
          Описание функции
        </p>
      </div>
      <div class="flex-shrink-0">
        <Switch id="feature" :checked="enabled" @update:checked="handleToggle" />
      </div>
    </div>

    <div class="flex justify-end gap-2">
      <Button variant="outline" @click="handleCancel">Отмена</Button>
      <Button @click="handleSave">Сохранить</Button>
    </div>
  </div>
</template>
```
