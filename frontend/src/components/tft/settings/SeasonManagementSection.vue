<template>
  <div class="season-section">
    <v-card class="transparent" rounded="lg" variant="flat">
      <v-card-text class="season-summary">
        <div class="season-summary__top">
          <div class="text-body-2 text-medium-emphasis">
            创建新赛季、切换当前浏览赛季，并维护系统默认激活赛季。
          </div>

          <div class="season-summary__form">
            <v-text-field
              v-model="seasonVersion"
              density="compact"
              :disabled="seasonBusy"
              hide-details
              placeholder="新赛季版本号"
              variant="outlined"
              @keyup.enter="createSeason"
            />

            <div class="season-summary__actions">
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
          </div>
        </div>

        <v-alert v-if="seasonError" density="compact" type="error">
          {{ seasonError }}
        </v-alert>

        <v-alert v-else-if="tft.seasonError" density="compact" type="warning">
          {{ tft.seasonError }}
        </v-alert>
      </v-card-text>
    </v-card>

    <div class="season-board">
      <div v-if="tft.seasons.length === 0" class="season-empty">
        <div class="text-subtitle-1 font-weight-bold">暂无赛季</div>
        <div class="text-body-2 text-medium-emphasis mt-1">
          先创建一个赛季，再开始管理对应的阵容内容。
        </div>
      </div>

      <div v-else class="season-list">
        <v-card
          v-for="item in tft.seasons"
          :key="item.uid"
          class="season-card transparent"
          rounded="lg"
          variant="flat"
        >
          <v-card-title class="season-card__title">
            <div class="season-card__heading">
              <v-chip
                :color="item.version === tft.season ? 'primary' : undefined"
              >
                {{ item.title }}
              </v-chip>
              <v-chip
                v-if="item.version === tft.activeSeason"
                color="success"
                size="small"
                variant="outlined"
              >
                当前激活
              </v-chip>
            </div>

            <div class="season-card__actions">
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
                设为激活
              </v-btn>
            </div>
          </v-card-title>

          <v-card-subtitle class="season-card__subtitle">
            创建时间：{{ formatDate(item.createdAt) }}
          </v-card-subtitle>
        </v-card>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { useTftStore } from '@/stores/tft'

  const tft = useTftStore()

  const seasonVersion = ref('')
  const seasonError = ref('')
  const creatingSeason = ref(false)
  const activatingSeason = ref('')

  const seasonBusy = computed(
    () => creatingSeason.value || Boolean(activatingSeason.value),
  )

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
          || '设置激活赛季失败'
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
.season-section {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.season-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.season-summary__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.season-summary__actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.season-summary__form {
  display: grid;
  gap: 12px;
  grid-template-columns: minmax(220px, 360px) auto;
  align-items: center;
}

.season-board {
  display: flex;
  flex: 1;
  min-height: 0;
}

.season-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  align-content: start;
}

.season-card {
  height: fit-content;
}

.season-card__title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.season-card__heading,
.season-card__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.season-card__subtitle {
  padding-bottom: 16px;
  line-height: 1.45;
}

.season-empty {
  display: flex;
  flex: 1;
  min-height: 0;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  border: 1px dashed rgba(255, 255, 255, 0.25);
  border-radius: 12px;
  opacity: 0.8;
}

@media (max-width: 960px) {
  .season-summary__top {
    align-items: stretch;
  }

  .season-summary__form {
    grid-template-columns: 1fr;
    width: 100%;
  }

  .season-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .season-list {
    grid-template-columns: 1fr;
  }
}
</style>
