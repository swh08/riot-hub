<template>
  <div class="composition-section">
    <v-card
      class="transparent composition-toolbar"
      rounded="lg"
      variant="flat"
    >
      <v-card-text class="composition-toolbar__body">
        <div>
          <div class="d-flex align-center ga-2">
            <v-icon color="primary" size="20">mdi-view-grid-outline</v-icon>
            <span class="text-subtitle-1 font-weight-bold">阵容管理</span>
            <v-chip v-if="tft.season" color="primary" size="x-small" variant="tonal">
              赛季 {{ tft.season }}
            </v-chip>
          </div>
          <div class="text-body-2 text-medium-emphasis mt-1">
            <span class="desktop-strength-hint">
              上传阵容图、拖拽调整强度分级，改动会立即保存。
            </span>
            <span class="mobile-strength-hint">
              长按选择强度，左右滑动可快速升降一级。
            </span>
          </div>
        </div>

        <div class="composition-toolbar__actions">
          <v-btn
            class="composition-toolbar__action"
            color="primary"
            height="40"
            :loading="loading"
            prepend-icon="mdi-refresh"
            variant="flat"
            @click="reload"
          >
            刷新
          </v-btn>

          <v-btn
            class="composition-toolbar__action"
            color="primary"
            :disabled="!tft.season || loading || saving || importing || metadataBusy"
            height="40"
            :loading="importing"
            prepend-icon="mdi-sync"
            variant="flat"
            @click="importCompositions"
          >
            同步目录
          </v-btn>

          <v-menu location="bottom end">
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                append-icon="mdi-chevron-down"
                class="composition-toolbar__action"
                color="primary"
                :disabled="!tft.season || importing || metadataBusy"
                height="40"
                :loading="metadataBusy"
                prepend-icon="mdi-database-outline"
                variant="flat"
              >
                备份与恢复
              </v-btn>
            </template>

            <v-list class="metadata-menu" density="compact">
              <v-list-item
                :disabled="restoringMetadata"
                prepend-icon="mdi-download-outline"
                subtitle="下载当前赛季状态"
                title="导出 metadata"
                @click="exportMetadata"
              />
              <v-list-item
                :disabled="exportingMetadata"
                prepend-icon="mdi-backup-restore"
                subtitle="从 JSON 备份恢复"
                title="导入 metadata"
                @click="openMetadataImport"
              />
            </v-list>
          </v-menu>

          <v-btn
            class="composition-toolbar__action"
            color="primary"
            :disabled="!tft.season || importing || metadataBusy"
            height="40"
            prepend-icon="mdi-upload"
            variant="flat"
            @click="uploadOpen = true"
          >
            上传阵容
          </v-btn>

          <v-progress-circular
            v-if="saving"
            class="ml-2"
            indeterminate
            size="22"
            width="2"
          />
        </div>
      </v-card-text>
    </v-card>

    <v-alert
      v-if="importFeedback"
      class="flex-0-0"
      closable
      density="compact"
      :type="importFeedback.type"
      variant="tonal"
      @click:close="importFeedback = null"
    >
      {{ importFeedback.message }}
    </v-alert>

    <div class="composition-board">
      <TierBoard ref="board" class="composition-board__content" />
    </div>

    <CompUploadDialog v-model="uploadOpen" @uploaded="reload" />
    <input
      ref="metadataInput"
      accept=".json,application/json"
      class="metadata-file-input"
      type="file"
      @change="restoreMetadata"
    >
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { useTftStore } from '@/stores/tft'

  const tft = useTftStore()

  const board = ref(null)
  const metadataInput = ref(null)
  const uploadOpen = ref(false)
  const importing = ref(false)
  const exportingMetadata = ref(false)
  const restoringMetadata = ref(false)
  const importFeedback = ref(null)

  const loading = computed(() => board.value?.loading?.value ?? false)
  const saving = computed(() => board.value?.saving?.value ?? false)
  const metadataBusy = computed(() => exportingMetadata.value || restoringMetadata.value)

  async function reload () {
    await tft.loadSeasons()
    await board.value?.reload?.()
  }

  async function importCompositions () {
    importing.value = true
    importFeedback.value = null

    try {
      const result = await tft.importSeasonCompositions()
      const ignoredMessage = result.ignored > 0
        ? `，忽略 ${result.ignored} 个非图片文件`
        : ''
      const metadataMessage = result.metadata_created
        ? '，已创建 metadata.json'
        : ''

      importFeedback.value = {
        type: 'success',
        message: `同步完成：新增 ${result.imported} 个，更新 ${result.updated} 个，未变化 ${result.skipped} 个${ignoredMessage}${metadataMessage}。`,
      }
    } catch (error) {
      importFeedback.value = {
        type: 'error',
        message: error?.response?.data?.detail || error?.message || '一键同步失败',
      }
    } finally {
      importing.value = false
    }
  }

  async function exportMetadata () {
    exportingMetadata.value = true
    importFeedback.value = null

    try {
      const metadata = await tft.exportSeasonCompositionMetadata()
      const url = URL.createObjectURL(metadata)
      const link = document.createElement('a')
      link.href = url
      link.download = `season-${tft.season}-metadata.json`
      document.body.append(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)

      importFeedback.value = {
        type: 'success',
        message: `赛季 ${tft.season} metadata 备份已导出。`,
      }
    } catch (error) {
      importFeedback.value = {
        type: 'error',
        message: error?.response?.data?.detail || error?.message || 'metadata 导出失败',
      }
    } finally {
      exportingMetadata.value = false
    }
  }

  function openMetadataImport () {
    metadataInput.value?.click()
  }

  async function restoreMetadata (event) {
    const input = event.target
    const file = input.files?.[0]
    input.value = ''
    if (!file) return

    restoringMetadata.value = true
    importFeedback.value = null

    try {
      const result = await tft.restoreSeasonCompositionMetadata(file)
      importFeedback.value = {
        type: 'success',
        message: `恢复完成：新增 ${result.imported} 个，更新 ${result.updated} 个，未变化 ${result.skipped} 个。`,
      }
    } catch (error) {
      importFeedback.value = {
        type: 'error',
        message: error?.response?.data?.detail || error?.message || 'metadata 恢复失败',
      }
    } finally {
      restoringMetadata.value = false
    }
  }
</script>

<style scoped>
.composition-section {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.composition-toolbar__body {
  display: flex;
  align-items: center;
  gap: 16px;
  justify-content: space-between;
  flex-wrap: wrap;
}

.composition-toolbar__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.composition-toolbar__action {
  flex: 0 0 auto;
}

.metadata-menu {
  min-width: 240px;
}

.composition-board {
  display: flex;
  flex: 1;
  min-height: 0;
}

.composition-board__content {
  flex: 1;
  min-height: 0;
}

.metadata-file-input {
  display: none;
}

.mobile-strength-hint {
  display: none;
}

@media (max-width: 960px) {
  .composition-section {
    min-height: unset;
  }

  .composition-board {
    min-height: unset;
  }

  .composition-toolbar__actions {
    width: 100%;
  }

  .desktop-strength-hint {
    display: none;
  }

  .mobile-strength-hint {
    display: inline;
  }
}

@media (max-width: 600px) {
  .composition-toolbar__actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

.composition-toolbar__action {
    width: 100%;
  }
}
</style>
