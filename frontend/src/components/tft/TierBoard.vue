<template>
  <div class="tier-board-root">
    <v-alert
      v-if="errorMsg"
      class="mb-4"
      density="compact"
      style="flex: 0 0 auto"
      type="error"
    >
      {{ errorMsg }}
    </v-alert>

    <v-row class="tier-board-row" dense>
      <v-col
        v-for="t in tiers"
        :key="t.level"
        class="tier-board-col"
        cols="12"
        md="4"
      >
        <TierColumn
          group="tiers"
          :items="t.items"
          :mobile-gestures="mobileGestures"
          :saving="saving"
          :title="t.title"
          @change="(evt) => onDrop(evt, t.level)"
          @gesture-end="endTierGesture"
          @gesture-move="moveTierGesture"
          @gesture-start="startTierGesture"
          @tier-picker="openTierPicker"
          @tier-step="onTierStep"
        />
      </v-col>
    </v-row>

    <div
      v-if="gesture.comp"
      aria-hidden="true"
      class="tier-gesture-layer"
    >
      <div class="tier-gesture-layer__backdrop" />
      <div class="tier-gesture-dock">
        <div class="tier-gesture-dock__heading">
          <span>左右滑动选择，松手确认</span>
          <span class="tier-gesture-dock__scale">较弱 → 较强</span>
        </div>
        <div class="tier-gesture-dock__targets">
          <div
            v-for="tier in mobileTierOptions"
            :key="tier.level"
            class="tier-gesture-target"
            :class="{
              'tier-gesture-target--active': gesture.highlightedTier === tier.level,
              'tier-gesture-target--current': gesture.currentTier === tier.level,
            }"
            :style="{ '--target-color': tier.color }"
          >
            <strong>{{ tier.title }}</strong>
            <span>{{ tier.caption }}</span>
          </div>
        </div>
      </div>
    </div>

    <v-bottom-sheet v-model="picker.open" inset>
      <v-card class="tier-picker" rounded="t-xl">
        <v-card-title class="d-flex align-center px-5 pt-5">
          <span class="text-subtitle-1 font-weight-bold">调整阵容强度</span>
          <v-spacer />
          <v-btn
            aria-label="关闭"
            icon="mdi-close"
            size="small"
            variant="text"
            @click="picker.open = false"
          />
        </v-card-title>
        <v-card-subtitle class="px-5 pb-3">
          {{ picker.comp?.name?.split('.')[0] }}
        </v-card-subtitle>
        <v-card-text class="tier-picker__options px-4 pb-5">
          <v-btn
            v-for="tier in mobileTierOptions"
            :key="tier.level"
            class="tier-picker__option"
            :color="tier.color"
            :disabled="saving"
            stacked
            :variant="Number(picker.comp?.tierLevel) === tier.level ? 'flat' : 'tonal'"
            @click="selectTierFromPicker(tier.level)"
          >
            <span class="text-h6 font-weight-bold">{{ tier.title }}</span>
            <span class="text-caption">{{ tier.caption }}</span>
          </v-btn>
        </v-card-text>
      </v-card>
    </v-bottom-sheet>

    <v-snackbar v-model="undo.visible" :timeout="5000">
      已将 {{ undo.name }} 调整为 {{ tierName(undo.toTier) }}
      <template #actions>
        <v-btn
          :loading="undo.loading"
          variant="text"
          @click="undoTierChange"
        >
          撤销
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
  import { onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
  import { useTftStore } from '@/stores/tft'

  const tft = useTftStore()

  const loading = ref(false)
  const saving = ref(false)
  const errorMsg = ref('')
  const mobileGestures = ref(false)
  let mobileGestureMedia = null

  const sList = ref([])
  const aList = ref([])
  const bList = ref([])
  const uidToPrevTier = ref(new Map())

  const mobileTierOptions = [
    { title: 'B', level: 2, color: '#ffd43b', caption: '过渡备选' },
    { title: 'A', level: 1, color: '#ffa94d', caption: '强势可玩' },
    { title: 'S', level: 0, color: '#ff4655', caption: '版本答案' },
  ]

  const gesture = reactive({
    comp: null,
    currentTier: null,
    highlightedTier: null,
    originX: 0,
  })

  const picker = reactive({
    open: false,
    comp: null,
  })

  const undo = reactive({
    visible: false,
    loading: false,
    comp: null,
    fromTier: null,
    toTier: null,
    name: '',
  })

  const tiers = [
    {
      title: 'S',
      level: 0,
      get items () {
        return sList.value
      },
    },
    {
      title: 'A',
      level: 1,
      get items () {
        return aList.value
      },
    },
    {
      title: 'B',
      level: 2,
      get items () {
        return bList.value
      },
    },
  ]

  function buildLocalListsFromStore () {
    const s = []
    const a = []
    const b = []
    const m = new Map()

    for (const c of tft.comps) {
      const tier = String(c.tierLevel)
      m.set(c.uid, tier)

      if (tier === '0') s.push(c)
      else if (tier === '1') a.push(c)
      else b.push(c)
    }

    uidToPrevTier.value = m
    sList.value = s
    aList.value = a
    bList.value = b
  }

  async function reload () {
    loading.value = true
    errorMsg.value = ''

    try {
      await tft.loadComps()
      buildLocalListsFromStore()
    } catch (error) {
      errorMsg.value = error?.response?.data?.detail || error?.message || '刷新失败'
    } finally {
      loading.value = false
    }
  }

  onMounted(async () => {
    mobileGestureMedia = window.matchMedia('(max-width: 960px), (pointer: coarse)')
    updateMobileGestures()
    mobileGestureMedia.addEventListener('change', updateMobileGestures)

    if (tft.comps.length === 0) {
      await reload()
    } else {
      buildLocalListsFromStore()
    }
  })

  onBeforeUnmount(() => {
    mobileGestureMedia?.removeEventListener('change', updateMobileGestures)
  })

  watch(
    () => tft.comps,
    () => {
      buildLocalListsFromStore()
    },
  )

  async function onDrop (evt, newTierLevel) {
    if (evt?.moved) return
    if (!evt?.added) return

    const item = evt.added.element
    if (!item?.uid) return

    const prevTier = uidToPrevTier.value.get(item.uid)
    const nextTier = String(newTierLevel)
    if (prevTier === nextTier) return

    await persistTierChange(item, newTierLevel, {
      fromTier: Number(prevTier),
      moveLocally: false,
    })
  }

  function updateMobileGestures () {
    mobileGestures.value = Boolean(mobileGestureMedia?.matches)
  }

  function tierName (level) {
    return ['S', 'A', 'B'][Number(level)] || ''
  }

  function moveCompLocally (comp, nextTier) {
    sList.value = sList.value.filter(item => item.uid !== comp.uid)
    aList.value = aList.value.filter(item => item.uid !== comp.uid)
    bList.value = bList.value.filter(item => item.uid !== comp.uid)

    comp.tierLevel = String(nextTier)
    comp.tierName = tierName(nextTier)

    if (nextTier === 0) sList.value.push(comp)
    else if (nextTier === 1) aList.value.push(comp)
    else bList.value.push(comp)

    uidToPrevTier.value.set(comp.uid, String(nextTier))
  }

  async function persistTierChange (
    comp,
    nextTier,
    { fromTier = Number(comp.tierLevel), moveLocally = true, showUndo = true } = {},
  ) {
    if (!comp?.uid || saving.value || fromTier === nextTier) return

    saving.value = true
    errorMsg.value = ''

    if (moveLocally) moveCompLocally(comp, nextTier)

    try {
      await tft.patchComp(comp.uid, {
        tier_level: nextTier,
        tier_display: tierName(nextTier),
      })

      comp.tierLevel = String(nextTier)
      comp.tierName = tierName(nextTier)
      uidToPrevTier.value.set(comp.uid, String(nextTier))

      if (showUndo) {
        undo.comp = comp
        undo.fromTier = fromTier
        undo.toTier = nextTier
        undo.name = (comp.name || comp.code || '阵容').split('.')[0]
        undo.visible = true
      }
    } catch (error) {
      errorMsg.value
        = error?.response?.data?.detail || error?.message || '更新强度失败，已回滚'
      await tft.loadComps()
      buildLocalListsFromStore()
    } finally {
      saving.value = false
    }
  }

  function startTierGesture ({ comp, x }) {
    gesture.comp = comp
    gesture.currentTier = Number(comp.tierLevel)
    gesture.highlightedTier = Number(comp.tierLevel)
    gesture.originX = x
  }

  function moveTierGesture ({ x }) {
    if (!gesture.comp) return

    const deltaX = x - gesture.originX
    const currentStrength = 2 - gesture.currentTier
    const strengthDelta = Math.round(deltaX / 72)
    const nextStrength = Math.min(2, Math.max(0, currentStrength + strengthDelta))
    gesture.highlightedTier = 2 - nextStrength
  }

  async function endTierGesture ({ cancelled = false, x }) {
    if (!gesture.comp) return

    const comp = gesture.comp
    const currentTier = gesture.currentTier

    if (!cancelled && Math.abs(x - gesture.originX) >= 24) {
      moveTierGesture({ x })
    }

    const nextTier = cancelled ? currentTier : gesture.highlightedTier

    gesture.comp = null
    gesture.currentTier = null
    gesture.highlightedTier = null
    gesture.originX = 0

    if (nextTier !== currentTier) {
      navigator.vibrate?.(12)
      await persistTierChange(comp, nextTier, { fromTier: currentTier })
    }
  }

  async function onTierStep ({ comp, delta }) {
    const currentTier = Number(comp.tierLevel)
    const nextTier = Math.min(2, Math.max(0, currentTier + delta))

    if (nextTier !== currentTier) {
      await persistTierChange(comp, nextTier, { fromTier: currentTier })
    }
  }

  function openTierPicker (comp) {
    picker.comp = comp
    picker.open = true
  }

  async function selectTierFromPicker (nextTier) {
    const comp = picker.comp
    const currentTier = Number(comp?.tierLevel)
    picker.open = false

    if (comp && nextTier !== currentTier) {
      await persistTierChange(comp, nextTier, { fromTier: currentTier })
    }
  }

  async function undoTierChange () {
    if (!undo.comp || undo.loading) return

    const comp = undo.comp
    const targetTier = undo.fromTier
    const currentTier = Number(comp.tierLevel)

    undo.loading = true
    undo.visible = false
    await persistTierChange(comp, targetTier, {
      fromTier: currentTier,
      showUndo: false,
    })
    undo.loading = false
  }

  defineExpose({
    reload,
    loading,
    saving,
    errorMsg,
  })
</script>

<style scoped>
.tier-board-root {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.tier-board-row {
  flex: 1;
  min-height: 0;
}

.tier-board-col {
  height: 100%;
  min-height: 0;
}

.tier-gesture-layer {
  position: fixed;
  z-index: 1900;
  inset: 0;
  pointer-events: none;
}

.tier-gesture-layer__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(5, 8, 13, 0.42);
}

.tier-gesture-dock {
  position: absolute;
  inset: auto 12px max(12px, env(safe-area-inset-bottom));
  overflow: hidden;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  background: rgba(16, 21, 31, 0.98);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.42);
}

.tier-gesture-dock__heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 0 4px 10px;
  color: rgba(255, 255, 255, 0.86);
  font-size: 13px;
}

.tier-gesture-dock__scale {
  color: rgba(255, 255, 255, 0.56);
  white-space: nowrap;
}

.tier-gesture-dock__targets {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.tier-gesture-target {
  min-height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 2px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--target-color) 10%, #10151f);
  color: rgba(255, 255, 255, 0.68);
  transition:
    background 0.18s ease,
    color 0.18s ease,
    transform 0.18s cubic-bezier(0.22, 1, 0.36, 1);
}

.tier-gesture-target strong {
  color: var(--target-color);
  font-size: 22px;
}

.tier-gesture-target span {
  font-size: 11px;
}

.tier-gesture-target--current {
  outline: 1px solid color-mix(in srgb, var(--target-color) 50%, transparent);
}

.tier-gesture-target--active {
  background: color-mix(in srgb, var(--target-color) 24%, #10151f);
  color: white;
  transform: translateY(-4px);
}

.tier-picker {
  max-width: 600px;
  margin: 0 auto;
  background: #10151f;
}

.tier-picker__options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.tier-picker__option {
  min-height: 76px;
}

@media (max-width: 960px) {
  .tier-board-row {
    flex: initial;
  }

  .tier-board-col {
    height: auto;
  }
}

@media (prefers-reduced-motion: reduce) {
  .tier-gesture-target {
    transition: none;
  }
}
</style>
