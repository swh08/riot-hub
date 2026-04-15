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
        :animation="150"
        chosen-class="drag-chosen"
        class="drop-zone"
        drag-class="drag-dragging"
        :empty-insert-threshold="24"
        :fallback-on-body="true"
        :fallback-tolerance="8"
        :filter="'.no-drag, button, input, textarea, select, a'"
        :force-fallback="true"
        ghost-class="drag-ghost"
        :group="{ name: group, pull: true, put: true }"
        :invert-swap="true"
        item-key="uid"
        :list="items"
        :prevent-on-filter="false"
        :scroll="true"
        :scroll-sensitivity="80"
        :scroll-speed="14"
        :swap-threshold="0.85"
        @change="$emit('change', $event)"
      >
        <template #item="{ element }">
          <CompCard :comp="element" @delete="openDelete" @edit="openEdit" />
        </template>
      </Draggable>

      <div v-if="items.length === 0" class="empty-overlay">拖拽阵容到这里</div>
    </v-card-text>
  </v-card>

  <CompEditDialog v-model="edit.open" :comp="edit.comp" @save="saveEdit" />

  <v-dialog v-model="remove.open" max-width="440">
    <v-card rounded="lg">
      <v-card-title class="text-h6 font-weight-bold">
        删除阵容
      </v-card-title>

      <v-card-text>
        确认删除
        <strong>{{ remove.comp?.name || remove.comp?.code || '该阵容' }}</strong>
        吗？相关图片文件也会一起删除，且无法恢复。
      </v-card-text>

      <v-alert
        v-if="remove.error"
        class="mx-6 mb-4"
        density="compact"
        type="error"
      >
        {{ remove.error }}
      </v-alert>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn :disabled="remove.loading" variant="text" @click="closeDelete">
          取消
        </v-btn>
        <v-btn
          color="error"
          :loading="remove.loading"
          variant="flat"
          @click="confirmDelete"
        >
          删除
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
  import { reactive } from 'vue'
  import Draggable from 'vuedraggable'
  import { useTftStore } from '@/stores/tft'

  defineProps({
    title: { type: String, required: true },
    items: { type: Array, required: true },
    group: { type: String, default: 'tiers' },
  })

  defineEmits(['change'])

  const tft = useTftStore()

  const edit = reactive({
    open: false,
    comp: null,
  })

  const remove = reactive({
    open: false,
    error: '',
    loading: false,
    comp: null,
  })

  function openEdit (comp) {
    edit.comp = comp
    edit.open = true
  }

  function openDelete (comp) {
    remove.error = ''
    remove.comp = comp
    remove.open = true
  }

  function closeDelete () {
    if (remove.loading) return
    remove.open = false
    remove.error = ''
    remove.comp = null
  }

  async function saveEdit ({ uid, comp_code, keywords }) {
    await tft.patchComp(uid, { comp_code, keywords })
  }

  async function confirmDelete () {
    if (!remove.comp?.uid) return

    remove.loading = true
    try {
      await tft.deleteComp(remove.comp.uid)
      remove.loading = false
      closeDelete()
      return
    } catch (error) {
      remove.error
        = error?.response?.data?.detail || error?.message || '删除阵容失败'
    } finally {
      remove.loading = false
    }
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
