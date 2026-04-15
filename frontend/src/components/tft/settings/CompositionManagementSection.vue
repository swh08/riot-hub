<template>
  <div class="composition-section">
    <v-card
      class="transparent composition-toolbar"
      rounded="lg"
      variant="flat"
    >
      <v-card-text class="composition-toolbar__body">
        <div>
          <div class="text-body-2 text-medium-emphasis">
            上传阵容图、调整强度分级，并随时刷新当前赛季的数据。
          </div>
        </div>

        <div class="composition-toolbar__actions">
          <v-btn :loading="loading" @click="reload">刷新</v-btn>

          <v-btn color="primary" variant="flat" @click="uploadOpen = true">
            <v-icon class="mr-2">mdi-upload</v-icon>
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

    <div class="composition-board">
      <TierBoard ref="board" class="composition-board__content" />
    </div>

    <CompUploadDialog v-model="uploadOpen" @uploaded="reload" />
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { useTftStore } from '@/stores/tft'

  const tft = useTftStore()

  const board = ref(null)
  const uploadOpen = ref(false)

  const loading = computed(() => board.value?.loading?.value ?? false)
  const saving = computed(() => board.value?.saving?.value ?? false)

  async function reload () {
    await tft.loadSeasons()
    await board.value?.reload?.()
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
  gap: 12px;
  flex-wrap: wrap;
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
</style>
