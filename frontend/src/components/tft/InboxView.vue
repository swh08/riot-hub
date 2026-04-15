<template>
  <div class="inbox-card">
    <v-img
      v-if="tft.currentComp"
      class="inbox-image"
      contain
      :src="tft.currentComp.image"
    />
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
}

@media (max-width: 600px) {
  .inbox-card {
    min-height: calc(100dvh - var(--app-bar-height));
  }

  .inbox-image {
    max-height: calc(100dvh - var(--app-bar-height) - 16px);
  }
}
</style>
