<template>
  <div class="inbox-card">
    <v-img
      v-if="tft.currentComp"
      class="inbox-image"
      contain
      :src="tft.currentComp.image"
    />

    <div v-else class="inbox-empty">
      <v-icon class="inbox-empty__icon" size="72">
        mdi-image-multiple-outline
      </v-icon>
      <div class="text-h6 font-weight-medium mt-4">
        {{ tft.filteredComps.length > 0 ? '选择一个阵容' : '当前赛季暂无阵容' }}
      </div>
      <div class="text-body-2 text-medium-emphasis mt-2">
        {{
          tft.filteredComps.length > 0
            ? '从左侧列表中点击阵容即可查看大图'
            : '可以在设置中心的阵容管理中上传阵容图'
        }}
      </div>
    </div>
  </div>
</template>

<script setup>
  import { useTftStore } from '@/stores/tft'
  const tft = useTftStore()
</script>

<style scoped>
.inbox-card {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  overflow: hidden;
}

.inbox-image {
  width: 100%;
  height: 100%;
  max-height: calc(100dvh - var(--app-bar-height));
  filter: drop-shadow(0 18px 44px rgba(0, 0, 0, 0.55));
}

.inbox-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px 56px;
  border: 1px dashed rgba(255, 255, 255, 0.16);
  border-radius: 24px;
  background: rgba(10, 13, 20, 0.45);
  backdrop-filter: blur(10px);
}

.inbox-empty__icon {
  opacity: 0.35;
}

@media (max-width: 600px) {
  .inbox-card {
    min-height: calc(100dvh - var(--app-bar-height));
    padding: 16px;
  }

  .inbox-image {
    max-height: calc(100dvh - var(--app-bar-height) - 16px);
  }

  .inbox-empty {
    padding: 36px 24px;
  }
}
</style>
