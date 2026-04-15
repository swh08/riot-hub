<template>
  <div class="season-section">
    <v-card class="transparent" rounded="lg" variant="flat">
      <v-card-text class="season-summary">
        <div class="season-summary__top">
          <div class="text-body-2 text-medium-emphasis">
            创建新赛季、切换当前浏览赛季，并为每个赛季设置单独的背景图。
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
          先创建一个赛季，再开始管理对应的阵容内容和赛季背景。
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

          <v-card-text class="season-card__body">
            <div
              class="season-card__preview"
              :style="getBackgroundPreviewStyle(item.version)"
            >
              <div class="season-card__preview-meta">
                <span>赛季背景</span>
                <span>
                  {{ tft.hasCustomSeasonBackground(item.version) ? '已自定义' : '默认背景' }}
                </span>
              </div>
            </div>

            <div class="season-card__background-actions">
              <input
                :ref="element => setBackgroundInputRef(item.version, element)"
                accept="image/png,image/jpeg,image/webp"
                class="season-card__file-input"
                type="file"
                @change="event => handleBackgroundChange(item.version, event)"
              >

              <v-btn
                color="primary"
                :disabled="seasonBusy"
                :loading="uploadingBackground === item.version"
                size="small"
                variant="tonal"
                @click="openBackgroundPicker(item.version)"
              >
                更换背景图
              </v-btn>

              <v-btn
                :disabled="seasonBusy || !tft.hasCustomSeasonBackground(item.version)"
                size="small"
                variant="text"
                @click="resetSeasonBackground(item.version)"
              >
                恢复默认
              </v-btn>
            </div>

            <div class="text-caption text-medium-emphasis">
              支持 JPG / PNG / WebP，建议单张不超过 2 MB。
            </div>
          </v-card-text>
        </v-card>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { useTftStore } from '@/stores/tft'

  const MAX_BACKGROUND_SIZE = 2 * 1024 * 1024

  const tft = useTftStore()

  const seasonVersion = ref('')
  const seasonError = ref('')
  const creatingSeason = ref(false)
  const activatingSeason = ref('')
  const uploadingBackground = ref('')
  const backgroundInputRefs = ref({})

  const seasonBusy = computed(
    () =>
      creatingSeason.value
      || Boolean(activatingSeason.value)
      || Boolean(uploadingBackground.value),
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

  function setBackgroundInputRef (version, element) {
    if (element) {
      backgroundInputRefs.value[version] = element
    } else {
      delete backgroundInputRefs.value[version]
    }
  }

  function openBackgroundPicker (version) {
    backgroundInputRefs.value[version]?.click()
  }

  async function handleBackgroundChange (version, event) {
    const [file] = event?.target?.files || []

    if (!file) {
      return
    }

    seasonError.value = ''

    try {
      if (!file.type.startsWith('image/')) {
        throw new Error('请选择图片文件')
      }

      if (file.size > MAX_BACKGROUND_SIZE) {
        throw new Error('背景图不能超过 2 MB')
      }

      uploadingBackground.value = version
      const image = await readFileAsDataUrl(file)
      tft.setSeasonBackground(version, image)
    } catch (error) {
      seasonError.value = error?.message || '设置背景图失败'
    } finally {
      uploadingBackground.value = ''
      if (event?.target) {
        event.target.value = ''
      }
    }
  }

  function resetSeasonBackground (version) {
    seasonError.value = ''
    tft.clearSeasonBackground(version)
  }

  function getBackgroundPreviewStyle (version) {
    const background = tft.getSeasonBackground(version)

    return {
      '--season-preview-image': background ? `url("${background}")` : 'none',
    }
  }

  function readFileAsDataUrl (file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()

      reader.onload = () => resolve(String(reader.result || ''))
      reader.onerror = () => reject(new Error('读取背景图失败'))

      reader.readAsDataURL(file)
    })
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
.season-card__actions,
.season-card__background-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.season-card__subtitle {
  padding-bottom: 8px;
  line-height: 1.45;
}

.season-card__body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 0;
}

.season-card__preview {
  position: relative;
  min-height: 132px;
  border-radius: 14px;
  overflow: hidden;
  background:
    linear-gradient(
      135deg,
      rgba(16, 20, 28, 0.42),
      rgba(16, 20, 28, 0.72)
    ),
    var(--season-preview-image) center / cover no-repeat;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.season-card__preview::after {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      180deg,
      rgba(8, 11, 18, 0.04) 0%,
      rgba(8, 11, 18, 0.68) 100%
    );
}

.season-card__preview-meta {
  position: absolute;
  inset: auto 12px 12px 12px;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(4, 8, 16, 0.5);
  backdrop-filter: blur(8px);
  font-size: 12px;
  letter-spacing: 0.04em;
}

.season-card__file-input {
  display: none;
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

  .season-card__preview {
    min-height: 112px;
  }
}
</style>
