<template>
  <div class="settings-root pa-4">
    <div class="d-flex align-center mb-4">
      <div class="text-h5 font-weight-bold">阵容编辑</div>
      <v-spacer />

      <v-btn class="mr-2" :loading="loading" @click="reload">刷新</v-btn>

      <v-btn color="primary" variant="flat" @click="uploadOpen = true">
        <v-icon class="mr-2">mdi-upload</v-icon>
        上传
      </v-btn>

      <v-progress-circular
        v-if="saving"
        class="ml-3"
        indeterminate
        size="22"
        width="2"
      />
    </div>

    <v-card class="mb-4 transparent season-panel" rounded="lg" variant="flat">
      <v-card-title class="d-flex align-center season-panel__header">
        <div class="text-h6 font-weight-bold">赛季管理</div>
        <v-spacer />
        <v-chip
          :color="tft.activeSeason ? 'success' : 'warning'"
          variant="outlined"
        >
          {{
            tft.activeSeason
              ? `当前激活：赛季 ${tft.activeSeason}`
              : "当前没有激活赛季"
          }}
        </v-chip>
      </v-card-title>

      <v-divider class="season-panel__divider" />

      <v-card-text class="season-panel__body">
        <v-row>
          <v-col cols="12" md="4">
            <div class="season-panel__controls">
              <v-text-field
                v-model="seasonVersion"
                density="comfortable"
                :disabled="seasonBusy"
                label="新赛季版本"
                variant="outlined"
                @keyup.enter="createSeason"
              />

              <div class="d-flex align-center ga-2 mt-2">
                <v-btn
                  color="primary"
                  :disabled="seasonBusy || !seasonVersion.trim()"
                  :loading="creatingSeason"
                  variant="flat"
                  @click="createSeason"
                >
                  添加赛季
                </v-btn>

                <v-btn
                  :disabled="seasonBusy"
                  :loading="tft.seasonLoading"
                  variant="text"
                  @click="refreshSeasons"
                >
                  刷新赛季
                </v-btn>
              </div>

              <div class="text-body-2 text-medium-emphasis mt-4">
                当前查看：
                {{ tft.season ? `赛季 ${tft.season}` : "未选择赛季" }}
              </div>

              <v-alert
                v-if="seasonError"
                class="mt-4"
                density="compact"
                type="error"
              >
                {{ seasonError }}
              </v-alert>

              <v-alert
                v-else-if="tft.seasonError"
                class="mt-4"
                density="compact"
                type="warning"
              >
                {{ tft.seasonError }}
              </v-alert>
            </div>
          </v-col>

          <v-col cols="12" md="8">
            <v-list class="season-list" lines="two">
              <v-list-item
                v-for="item in tft.seasons"
                :key="item.uid"
                class="season-list__item"
                :subtitle="`创建时间：${formatDate(item.createdAt)}`"
              >
                <template #prepend>
                  <div class="d-flex ga-2 align-center season-tags">
                    <v-chip
                      :color="item.version === tft.season ? 'primary' : undefined"
                      variant="flat"
                    >
                      {{ item.title }}
                    </v-chip>
                    <v-chip
                      v-if="item.version === tft.activeSeason"
                      color="success"
                      variant="outlined"
                    >
                      当前
                    </v-chip>
                  </div>
                </template>

                <template #append>
                  <div class="d-flex ga-2 season-actions">
                    <v-btn
                      :disabled="seasonBusy || item.version === tft.season"
                      size="small"
                      variant="text"
                      @click="selectSeason(item.version)"
                    >
                      查看
                    </v-btn>
                    <v-btn
                      color="success"
                      :disabled="seasonBusy || item.version === tft.activeSeason"
                      :loading="activatingSeason === item.version"
                      size="small"
                      variant="tonal"
                      @click="setActiveSeason(item.version)"
                    >
                      设为当前赛季
                    </v-btn>
                  </div>
                </template>
              </v-list-item>

              <v-list-item v-if="tft.seasons.length === 0" class="season-list__empty">
                <v-list-item-title>暂无赛季</v-list-item-title>
                <v-list-item-subtitle>
                  创建一个赛季后再开始管理阵容。
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <TierBoard ref="board" class="settings-board" />

    <CompUploadDialog v-model="uploadOpen" @uploaded="reload" />
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { useTftStore } from '@/stores/tft'

  const board = ref(null)
  const tft = useTftStore()

  const loading = computed(() => board.value?.loading?.value ?? false)
  const saving = computed(() => board.value?.saving?.value ?? false)
  const seasonBusy = computed(
    () => creatingSeason.value || Boolean(activatingSeason.value),
  )

  const uploadOpen = ref(false)
  const seasonVersion = ref('')
  const seasonError = ref('')
  const creatingSeason = ref(false)
  const activatingSeason = ref('')

  async function reload () {
    await tft.loadSeasons()
    await board.value?.reload?.()
  }

  async function refreshSeasons () {
    seasonError.value = ''
    await tft.loadSeasons()
  }

  async function createSeason () {
    const version = seasonVersion.value.trim()
    if (!version) return

    seasonError.value = ''
    creatingSeason.value = true

    try {
      await tft.createSeason(version)
      seasonVersion.value = ''
    } catch (error) {
      seasonError.value
        = error?.response?.data?.version?.[0]
          || error?.response?.data?.detail
          || error?.message
          || '创建赛季失败'
    } finally {
      creatingSeason.value = false
    }
  }

  async function setActiveSeason (version) {
    seasonError.value = ''
    activatingSeason.value = version

    try {
      await tft.activateSeason(version)
    } catch (error) {
      seasonError.value
        = error?.response?.data?.detail
          || error?.message
          || '设置当前赛季失败'
    } finally {
      activatingSeason.value = ''
    }
  }

  async function selectSeason (version) {
    seasonError.value = ''

    try {
      await tft.changeSeason(version)
    } catch (error) {
      seasonError.value
        = error?.response?.data?.detail
          || error?.message
          || '切换赛季失败'
    }
  }

  function formatDate (value) {
    if (!value) return '未知'
    return new Date(value).toLocaleString()
  }
</script>

<style scoped>
.settings-root {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.settings-board {
  flex: 1;
  min-height: 0;
}

.season-panel {
  border-color: rgba(255, 255, 255, 0.1);
}

.season-panel__header {
  padding-bottom: 18px;
}

.season-panel__divider {
  opacity: 0.55;
}

.season-panel__body {
  padding-top: 20px;
}

.season-panel__controls {
  padding: 4px;
}

.season-list {
  max-height: 300px;
  overflow-y: auto;
  border-radius: 16px;
  padding: 8px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02)),
    rgba(7, 10, 16, 0.68);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.season-list__item {
  margin-bottom: 8px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
}

.season-list__item:last-child {
  margin-bottom: 0;
}

.season-list__empty {
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.02);
}

.season-tags {
  flex-wrap: wrap;
}

.season-actions {
  align-items: center;
}
</style>
