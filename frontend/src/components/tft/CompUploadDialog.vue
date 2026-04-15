<template>
  <v-dialog v-model="open" max-width="640">
    <v-card rounded="lg">
      <v-card-title class="d-flex align-center">
        <span class="text-h6 font-weight-bold">上传阵容图片</span>
        <v-spacer />
        <v-btn icon variant="text" @click="open = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-card-text>
        <v-alert density="compact" type="info" variant="tonal">
          上传目标：
          {{ tft.season ? `赛季 ${tft.season}` : "未选择赛季" }}
        </v-alert>

        <v-file-input
          v-model="form.files"
          accept="image/*"
          class="mt-4"
          density="compact"
          :disabled="saving"
          label="选择图片（可多选）"
          multiple
          prepend-icon=""
          prepend-inner-icon="mdi-image"
          show-size
          variant="outlined"
        />

        <v-text-field
          v-model="form.compCode"
          class="mt-3"
          density="compact"
          :disabled="saving"
          label="阵容码"
          variant="outlined"
        />

        <v-select
          v-model="form.tierName"
          class="mt-3"
          density="compact"
          :disabled="saving"
          :items="['S', 'A', 'B']"
          label="强度"
          variant="outlined"
        />

        <div class="mt-4">
          <KeywordsInput v-model="form.keywords" :disabled="saving" />
        </div>

        <v-alert v-if="error" class="mt-4" density="compact" type="error">
          <div style="white-space: pre-line">{{ error }}</div>
        </v-alert>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn :disabled="saving" variant="text" @click="open = false">
          取消
        </v-btn>
        <v-btn color="primary" :loading="saving" variant="flat" @click="submit">
          上传
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
  import { computed, reactive, ref, watch } from 'vue'
  import * as compApi from '@/api/comp'
  import { useTftStore } from '@/stores/tft'

  const tft = useTftStore()

  const props = defineProps({
    modelValue: { type: Boolean, default: false },
  })

  const emit = defineEmits(['update:modelValue', 'uploaded'])

  const open = computed({
    get: () => props.modelValue,
    set: value => emit('update:modelValue', value),
  })

  const saving = ref(false)
  const error = ref('')

  const form = reactive({
    files: [],
    compCode: '',
    tierName: 'B',
    keywords: [],
  })

  function normalize (value) {
    return (value ?? '').trim()
  }

  function tierToLevel (tierName) {
    return tierName === 'S' ? 0 : (tierName === 'A' ? 1 : 2)
  }

  watch(
    () => open.value,
    value => {
      if (!value) return
      error.value = ''
      form.files = []
      form.compCode = ''
      form.tierName = 'B'
      form.keywords = []
    },
  )

  async function submit () {
    error.value = ''

    const files = Array.isArray(form.files)
      ? form.files
      : (form.files
        ? [form.files]
        : [])
    const comp_code = normalize(form.compCode)

    if (files.length === 0) {
      error.value = '请选择至少一张图片'
      return
    }

    if (!tft.season) {
      error.value = '请先选择赛季'
      return
    }

    const tier_level = tierToLevel(form.tierName)
    const tier_display = form.tierName
    const keywords = (form.keywords || []).map(value => normalize(value)).filter(Boolean)

    saving.value = true

    try {
      await tft.ensureSelectedSeasonIsActive()

      const failures = []
      for (const file of files) {
        try {
          await compApi.uploadComp({
            file,
            comp_code,
            tier_level,
            tier_display,
            keywords,
          })
        } catch (uploadError) {
          const data = uploadError?.response?.data
          const message
            = data?.detail
              || data?.comp_code?.[0]
              || data?.image?.[0]
              || data?.keywords?.[0]
              || uploadError?.message
              || '上传失败'
          failures.push(`${file?.name || '(unknown file)'}: ${message}`)
        }
      }

      if (failures.length > 0) {
        error.value = `部分上传失败（${failures.length}/${files.length}）：\n${failures.join('\n')}`
        emit('uploaded')
        return
      }

      open.value = false
      emit('uploaded')
    } catch (submitError) {
      const data = submitError?.response?.data
      error.value
        = data?.detail
          || data?.comp_code?.[0]
          || data?.image?.[0]
          || data?.keywords?.[0]
          || submitError?.message
          || '上传失败'
    } finally {
      saving.value = false
    }
  }
</script>
