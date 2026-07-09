<template>
  <div
    class="mb-2 comp-card-shell"
    :class="{ 'comp-card-shell--mobile': mobileGestures }"
  >
    <span
      aria-hidden="true"
      class="comp-card-shell__swipe comp-card-shell__swipe--promote"
    >
      {{ promoteLabel }}
    </span>
    <span
      aria-hidden="true"
      class="comp-card-shell__swipe comp-card-shell__swipe--demote"
    >
      {{ demoteLabel }}
    </span>

    <v-card
      class="comp-card"
      :class="{
        'comp-card--gesture-active': longPressActive,
        'comp-card--tracking': trackingPointer,
      }"
      rounded="lg"
      :style="[cardStyle, gestureStyle]"
      variant="flat"
      @contextmenu="onContextMenu"
      @pointercancel="onPointerCancel"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
    >
      <v-card-title class="comp-card__title d-flex align-center py-2">
        <v-chip
          :aria-label="`当前强度 ${comp.tierName}，点击调整`"
          class="no-drag comp-card__tier font-weight-bold flex-shrink-0"
          :class="{ 'comp-card__tier--interactive': mobileGestures }"
          :color="tierColor"
          role="button"
          size="small"
          variant="tonal"
          @click.stop="openTierPicker"
          @keydown.enter.prevent="openTierPicker"
          @keydown.space.prevent="openTierPicker"
        >
          {{ comp.tierName }}
        </v-chip>

        <span class="text-subtitle-2 font-weight-bold text-truncate ml-2">
          {{ displayName }}
        </span>

        <v-spacer />

        <v-btn
          aria-label="编辑阵容"
          class="no-drag comp-card__action"
          color="warning"
          icon
          size="x-small"
          variant="text"
          @click.stop="$emit('edit', comp)"
        >
          <v-icon size="18">mdi-pencil</v-icon>
        </v-btn>

        <v-btn
          aria-label="删除阵容"
          class="no-drag comp-card__action"
          color="error"
          icon
          size="x-small"
          variant="text"
          @click.stop="$emit('delete', comp)"
        >
          <v-icon size="18">mdi-delete</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-subtitle class="comp-card__code text-caption pb-2">
        {{ comp.code }}
      </v-card-subtitle>

      <div v-if="(comp.keywords || []).length > 0" class="px-3 pb-3">
        <v-chip
          v-for="kw in comp.keywords.slice(0, 6)"
          :key="kw"
          class="mr-1 mb-1 comp-card__keyword"
          size="x-small"
          variant="outlined"
        >
          {{ kw }}
        </v-chip>
      </div>
    </v-card>
  </div>
</template>

<script setup>
  import { computed, onBeforeUnmount, reactive, ref } from 'vue'

  const props = defineProps({
    comp: { type: Object, required: true },
    mobileGestures: Boolean,
  })

  const emit = defineEmits([
    'delete',
    'edit',
    'gesture-end',
    'gesture-move',
    'gesture-start',
    'tier-picker',
    'tier-step',
  ])

  const LONG_PRESS_DELAY = 280
  const MOVE_TOLERANCE = 10
  const SWIPE_THRESHOLD = 72
  const MAX_SWIPE_OFFSET = 104

  const TIER_COLORS = {
    0: '#ff4655',
    1: '#ffa94d',
    2: '#ffd43b',
  }

  const TIER_NAMES = ['S', 'A', 'B']

  const trackingPointer = ref(false)
  const longPressActive = ref(false)
  const swipeOffset = ref(0)
  const gesture = reactive({
    pointerId: null,
    startX: 0,
    startY: 0,
    lastX: 0,
    lastY: 0,
    scrolling: false,
    target: null,
    timer: null,
  })

  const displayName = computed(() => (props.comp?.name || '').split('.')[0])
  const tierLevel = computed(() => Number(props.comp?.tierLevel))
  const tierColor = computed(
    () => TIER_COLORS[tierLevel.value] || '#9aa4b2',
  )
  const promoteLabel = computed(() =>
    tierLevel.value > 0 ? `升至 ${TIER_NAMES[tierLevel.value - 1]}` : '已是最高',
  )
  const demoteLabel = computed(() =>
    tierLevel.value < 2 ? `降至 ${TIER_NAMES[tierLevel.value + 1]}` : '已是最低',
  )
  const cardStyle = computed(() => ({
    '--tier-color': tierColor.value,
  }))
  const gestureStyle = computed(() => ({
    transform: longPressActive.value
      ? 'scale(1.025)'
      : `translateX(${swipeOffset.value}px)`,
  }))

  function supportsMobileGesture () {
    return props.mobileGestures
  }

  function clearLongPressTimer () {
    if (gesture.timer) {
      window.clearTimeout(gesture.timer)
      gesture.timer = null
    }
  }

  function resetGesture () {
    clearLongPressTimer()
    trackingPointer.value = false
    longPressActive.value = false
    swipeOffset.value = 0
    gesture.pointerId = null
    gesture.scrolling = false
    gesture.target = null
  }

  function onPointerDown (event) {
    if (
      !supportsMobileGesture()
      || event.button !== 0
      || event.target.closest('.no-drag, button, a, input, textarea, select')
    ) {
      return
    }

    trackingPointer.value = true
    gesture.pointerId = event.pointerId
    gesture.startX = event.clientX
    gesture.startY = event.clientY
    gesture.lastX = event.clientX
    gesture.lastY = event.clientY
    gesture.scrolling = false
    gesture.target = event.currentTarget

    gesture.timer = window.setTimeout(() => {
      longPressActive.value = true
      swipeOffset.value = 0
      gesture.target?.setPointerCapture?.(gesture.pointerId)
      navigator.vibrate?.(10)
      emit('gesture-start', {
        comp: props.comp,
        x: gesture.startX,
        y: gesture.startY,
      })
    }, LONG_PRESS_DELAY)
  }

  function onPointerMove (event) {
    if (!trackingPointer.value || event.pointerId !== gesture.pointerId) return

    gesture.lastX = event.clientX
    gesture.lastY = event.clientY

    const deltaX = event.clientX - gesture.startX
    const deltaY = event.clientY - gesture.startY

    if (longPressActive.value) {
      event.preventDefault()
      emit('gesture-move', {
        comp: props.comp,
        x: event.clientX,
        y: event.clientY,
      })
      return
    }

    if (Math.abs(deltaY) > MOVE_TOLERANCE && Math.abs(deltaY) > Math.abs(deltaX)) {
      gesture.scrolling = true
      clearLongPressTimer()
      swipeOffset.value = 0
      return
    }

    if (Math.abs(deltaX) > MOVE_TOLERANCE) {
      clearLongPressTimer()
      swipeOffset.value = Math.max(
        -MAX_SWIPE_OFFSET,
        Math.min(MAX_SWIPE_OFFSET, deltaX),
      )
    }
  }

  function onPointerUp (event) {
    if (!trackingPointer.value || event.pointerId !== gesture.pointerId) return

    clearLongPressTimer()

    if (longPressActive.value) {
      event.preventDefault()
      emit('gesture-end', {
        comp: props.comp,
        x: event.clientX,
        y: event.clientY,
      })
      resetGesture()
      return
    }

    const deltaX = event.clientX - gesture.startX
    const deltaY = event.clientY - gesture.startY

    if (
      !gesture.scrolling
      && Math.abs(deltaX) >= SWIPE_THRESHOLD
      && Math.abs(deltaX) > Math.abs(deltaY) * 1.25
    ) {
      navigator.vibrate?.(8)
      emit('tier-step', {
        comp: props.comp,
        delta: deltaX > 0 ? -1 : 1,
      })
    }

    resetGesture()
  }

  function onPointerCancel () {
    if (longPressActive.value) {
      emit('gesture-end', {
        comp: props.comp,
        cancelled: true,
        x: gesture.lastX,
        y: gesture.lastY,
      })
    }

    resetGesture()
  }

  function onContextMenu (event) {
    if (props.mobileGestures) event.preventDefault()
  }

  function openTierPicker () {
    if (props.mobileGestures) emit('tier-picker', props.comp)
  }

  onBeforeUnmount(resetGesture)
</script>

<style scoped>
.comp-card-shell {
  position: relative;
  overflow: hidden;
  border-radius: 12px;
}

.comp-card-shell__swipe {
  position: absolute;
  inset-block: 0;
  display: none;
  align-items: center;
  padding-inline: 16px;
  color: rgba(255, 255, 255, 0.88);
  font-size: 13px;
  font-weight: 700;
  pointer-events: none;
}

.comp-card-shell__swipe--promote {
  left: 0;
  color: #3ddc97;
}

.comp-card-shell__swipe--demote {
  right: 0;
  color: #ffd43b;
}

.comp-card-shell--mobile .comp-card-shell__swipe {
  display: flex;
}

.comp-card {
  position: relative;
  z-index: 1;
  user-select: none;
  overflow: hidden;
  background: #141a26;
  border: 1px solid rgba(255, 255, 255, 0.07);
  cursor: grab;
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}

.comp-card--tracking {
  transition: border-color 0.2s ease, background 0.2s ease;
}

.comp-card--gesture-active {
  z-index: 2;
  border-color: color-mix(in srgb, var(--tier-color) 55%, white);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.38);
}

.comp-card::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: var(--tier-color);
  opacity: 0.85;
}

.comp-card:hover {
  border-color: rgba(255, 255, 255, 0.16);
  background: #1a2130;
}

.comp-card__title {
  min-height: 0;
}

.comp-card__tier--interactive {
  min-width: 44px;
  min-height: 44px;
  cursor: pointer;
}

.comp-card__code {
  opacity: 0.55;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  letter-spacing: 0.02em;
}

.comp-card__keyword {
  opacity: 0.75;
}

.comp-card__action {
  opacity: 0.4;
  transition: opacity 0.2s ease;
}

.comp-card:hover .comp-card__action {
  opacity: 1;
}

@media (max-width: 960px), (pointer: coarse) {
  .comp-card-shell--mobile {
    touch-action: pan-y;
    -webkit-touch-callout: none;
  }

  .comp-card-shell--mobile .comp-card {
    cursor: default;
  }

  .comp-card-shell--mobile .comp-card__action {
    min-width: 44px;
    min-height: 44px;
    opacity: 0.72;
  }
}

@media (prefers-reduced-motion: reduce) {
  .comp-card {
    transition: none;
  }
}
</style>
