<template>
  <v-card class="tier-card" rounded="lg" :style="columnStyle" variant="flat">
    <v-card-title class="tier-header">
      <div class="tier-header__identity">
        <span class="tier-header__level">{{ title }}</span>
        <span class="tier-header__caption">{{ tierCaption }}</span>
      </div>

      <span
        :aria-label="`${items.length} 套阵容`"
        class="tier-header__count"
      >
        <strong>{{ items.length }}</strong>
        <span>套</span>
      </span>
    </v-card-title>

    <v-divider class="tier-header__divider" />

    <v-card-text class="tier-body">
      <Draggable
        :animation="150"
        chosen-class="drag-chosen"
        class="drop-zone"
        :disabled="mobileGestures"
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
          <CompCard
            :comp="element"
            :mobile-gestures="mobileGestures && !saving"
            @delete="openDelete"
            @edit="openEdit"
            @gesture-end="$emit('gesture-end', $event)"
            @gesture-move="$emit('gesture-move', $event)"
            @gesture-start="$emit('gesture-start', $event)"
            @tier-picker="$emit('tier-picker', $event)"
            @tier-step="$emit('tier-step', $event)"
          />
        </template>
      </Draggable>

      <div v-if="items.length === 0" class="empty-overlay">
        {{ mobileGestures ? '当前没有阵容' : '拖拽阵容到这里' }}
      </div>
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
  import { computed, reactive } from 'vue'
  import Draggable from 'vuedraggable'
  import { useTftStore } from '@/stores/tft'

  const props = defineProps({
    title: { type: String, required: true },
    items: { type: Array, required: true },
    group: { type: String, default: 'tiers' },
    mobileGestures: Boolean,
    saving: Boolean,
  })

  const TIER_META = {
    S: { color: '#ff4655', caption: '版本答案' },
    A: { color: '#ffa94d', caption: '强势可玩' },
    B: { color: '#ffd43b', caption: '过渡备选' },
  }

  const tierColor = computed(() => TIER_META[props.title]?.color || '#9aa4b2')
  const tierCaption = computed(() => TIER_META[props.title]?.caption || '')
  const columnStyle = computed(() => ({
    '--tier-color': tierColor.value,
  }))

  defineEmits([
    'change',
    'gesture-end',
    'gesture-move',
    'gesture-start',
    'tier-picker',
    'tier-step',
  ])

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
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: #0c111b;
}

.tier-card::before {
  content: '';
  flex: 0 0 auto;
  height: 3px;
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--tier-color) 24%, transparent),
    var(--tier-color) 28%,
    color-mix(in srgb, var(--tier-color) 72%, white) 50%,
    var(--tier-color) 72%,
    color-mix(in srgb, var(--tier-color) 24%, transparent)
  );
  box-shadow:
    0 2px 8px color-mix(in srgb, var(--tier-color) 42%, transparent),
    0 4px 16px color-mix(in srgb, var(--tier-color) 18%, transparent);
  opacity: 0.96;
}

.tier-header {
  min-height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--tier-color) 13%, #0c111b),
    color-mix(in srgb, var(--tier-color) 6%, #0c111b) 54%,
    color-mix(in srgb, var(--tier-color) 2%, #0c111b)
  );
}

.tier-header__identity {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.tier-header__level {
  width: 36px;
  height: 36px;
  display: inline-grid;
  flex: 0 0 36px;
  place-items: center;
  border: 1px solid color-mix(in srgb, var(--tier-color) 38%, transparent);
  border-radius: 10px;
  background: color-mix(in srgb, var(--tier-color) 13%, transparent);
  color: var(--tier-color);
  font-size: 20px;
  font-weight: 800;
  line-height: 1;
}

.tier-header__caption {
  overflow: hidden;
  color: rgba(255, 255, 255, 0.72);
  font-size: 13px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tier-header__count {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: baseline;
  gap: 4px;
  color: rgba(255, 255, 255, 0.46);
  font-size: 11px;
}

.tier-header__count strong {
  color: rgba(255, 255, 255, 0.9);
  font-size: 18px;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.tier-header__divider {
  opacity: 0.08;
}

.tier-body {
  position: relative;
  flex: 1;
  container-name: tier-body;
  container-type: inline-size;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 10px;
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
  opacity: 0.6;
  font-size: 13px;
  letter-spacing: 0.06em;
  border: 1px dashed color-mix(in srgb, var(--tier-color) 45%, rgba(255, 255, 255, 0.2));
  border-radius: 12px;
  background: color-mix(in srgb, var(--tier-color) 4%, transparent);
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

@media (max-width: 960px) {
  .tier-card {
    height: auto;
    min-height: 0;
  }

  .tier-body {
    max-height: none;
    overflow-y: visible;
  }

  .drop-zone {
    min-height: 0;
    padding-bottom: 0;
  }

  .empty-overlay {
    position: static;
    min-height: 88px;
  }
}
</style>
