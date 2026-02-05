<template>
  <div class="settings-root pa-4">
    <div class="d-flex align-center mb-4">
      <div class="text-h5 font-weight-bold">阵容编辑</div>
      <v-spacer />

      <v-btn class="mr-2" :loading="loading" @click="reload"> 刷新 </v-btn>

      <v-btn color="primary" variant="flat" @click="uploadOpen = true">
        <v-icon class="mr-2">mdi-upload</v-icon>
        上传
      </v-btn>

      <v-progress-circular
        v-if="saving"
        indeterminate
        size="22"
        width="2"
        class="ml-3"
      />
    </div>

    <TierBoard ref="board" class="settings-board" />

    <CompUploadDialog v-model="uploadOpen" @uploaded="reload" />
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
const board = ref(null);

const loading = computed(() => board.value?.loading?.value ?? false);
const saving = computed(() => board.value?.saving?.value ?? false);

const uploadOpen = ref(false);

async function reload() {
  await board.value?.reload?.();
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
</style>
