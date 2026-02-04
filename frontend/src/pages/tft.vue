<template>
  <v-card tile class="transparent">
    <v-img
      v-if="tft.currentComp"
      contain
      max-height="calc(100vh - 64px)"
      :src="tft.currentComp.image"
    />
  </v-card>
</template>

<script setup>
import { useTftStore } from "@/stores/tft";
const tft = useTftStore();
</script>

<style scoped>
.transparent {
  background-color: transparent !important;
  backdrop-filter: blur(8px);
}
</style>
