<template>
  <div>
    <div class="d-flex align-center">
      <v-text-field
        v-model="keywordInput"
        :disabled="disabled"
        hide-details
        :label="label"
        variant="outlined"
        @keyup.enter="add"
      />

      <v-btn
        class="ml-2"
        :disabled="disabled || !keywordInput.trim()"
        icon
        variant="outlined"
        @click="add"
      >
        <v-icon>mdi-plus</v-icon>
      </v-btn>
    </div>

    <div class="mt-3">
      <v-chip
        v-for="keyword in keywords"
        :key="keyword"
        class="mr-2 mb-2"
        closable
        :disabled="disabled"
        variant="outlined"
        @click:close="remove(keyword)"
      >
        {{ keyword }}
      </v-chip>

      <div
        v-if="keywords.length === 0"
        class="text-caption text-medium-emphasis"
      >
        {{ emptyText }}
      </div>
    </div>
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'

  const props = defineProps({
    modelValue: { type: Array, default: () => [] },
    disabled: { type: Boolean, default: false },
    label: { type: String, default: '添加关键词' },
    emptyText: { type: String, default: '暂无关键词' },
  })

  const emit = defineEmits(['update:modelValue'])

  const keywordInput = ref('')

  const keywords = computed(() =>
    Array.isArray(props.modelValue) ? props.modelValue : [],
  )

  function normalize (s) {
    return (s ?? '').trim()
  }

  function setKeywords (next) {
    emit('update:modelValue', next)
  }

  function add () {
    const kw = normalize(keywordInput.value)
    if (!kw) return

    const exists = keywords.value.some(
      x => x.toLowerCase() === kw.toLowerCase(),
    )
    if (!exists) setKeywords([...keywords.value, kw])

    keywordInput.value = ''
  }

  function remove (kw) {
    setKeywords(keywords.value.filter(x => x !== kw))
  }
</script>
