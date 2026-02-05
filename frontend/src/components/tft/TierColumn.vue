<template>
  <v-card class="tier-card transparent" rounded="lg">
    <v-card-title class="tier-header d-flex align-center my-2">
      <v-chip class="text-h6 font-weight-bold">{{ title }}</v-chip>
      <v-spacer />
      <v-chip variant="outlined">{{ items.length }}</v-chip>
    </v-card-title>

    <v-divider />

    <v-card-text class="tier-body">
      <Draggable
        class="drop-zone"
        :list="items"
        item-key="uid"
        :group="{ name: group, pull: true, put: true }"
        :animation="150"
        :force-fallback="true"
        :fallback-on-body="true"
        :fallback-tolerance="8"
        :scroll="true"
        :scroll-sensitivity="80"
        :scroll-speed="14"
        :swap-threshold="0.85"
        :invert-swap="true"
        :empty-insert-threshold="24"
        ghost-class="drag-ghost"
        chosen-class="drag-chosen"
        drag-class="drag-dragging"
        :filter="'.no-drag, button, input, textarea, select, a'"
        :prevent-on-filter="false"
        @change="$emit('change', $event)"
      >
        <template #item="{ element }">
          <CompCard :comp="element" @edit="openEdit" />
        </template>
      </Draggable>

      <div v-if="items.length === 0" class="empty-overlay">拖拽阵容到这里</div>
    </v-card-text>
  </v-card>

  <CompEditDialog v-model="edit.open" :comp="edit.comp" @save="saveEdit" />
</template>

<script setup>
import Draggable from "vuedraggable";
import { reactive } from "vue";
import { useTftStore } from "@/stores/tft";

defineProps({
  title: { type: String, required: true },
  items: { type: Array, required: true },
  group: { type: String, default: "tiers" },
});

defineEmits(["change"]);

const tft = useTftStore();

const edit = reactive({
  open: false,
  comp: null,
});

function openEdit(comp) {
  edit.comp = comp;
  edit.open = true;
}

async function saveEdit({ uid, comp_code, keywords }) {
  await tft.patchComp(uid, { comp_code, keywords });
}
</script>

<style scoped>
.tier-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tier-body {
  position: relative;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px;
}

:global(.sortable-fallback) {
  z-index: 200000 !important;
}

:global(.sortable-drag) {
  z-index: 200000 !important;
}

.empty-overlay {
  position: absolute;
  inset: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  border: 1px dashed rgba(255, 255, 255, 0.25);
  border-radius: 12px;
  pointer-events: none;
}

.drop-zone {
  min-height: 100%;
  padding-bottom: 140px;
}

.no-drag {
  cursor: auto;
}

.drag-ghost {
  opacity: 0.35;
}
.drag-chosen {
  outline: 2px dashed rgba(255, 255, 255, 0.35);
}
</style>
