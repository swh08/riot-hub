<template>
  <div
    class="comp-card-shell"
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
      <div class="comp-card__row">
        <v-chip
          :aria-label="mobileGestures
            ? `当前强度 ${comp.tierName}，点击调整`
            : `当前强度 ${comp.tierName}`"
          class="no-drag comp-card__tier font-weight-bold flex-shrink-0"
          :class="{ 'comp-card__tier--interactive': mobileGestures }"
          :color="tierColor"
          :role="mobileGestures ? 'button' : undefined"
          size="x-small"
          :tabindex="mobileGestures ? 0 : -1"
          variant="tonal"
          @click.stop="openTierPicker"
          @keydown.enter.prevent="openTierPicker"
          @keydown.space.prevent="openTierPicker"
        >
          {{ comp.tierName }}
        </v-chip>

        <span class="comp-card__name" :title="displayName">
          {{ displayName }}
        </span>

        <span v-if="comp.code" class="comp-card__code" :title="comp.code">
          {{ comp.code }}
        </span>

        <span
          v-if="keywordSummary"
          class="comp-card__keywords"
          :title="(comp.keywords || []).join(' / ')"
        >
          {{ keywordSummary }}
        </span>

        <div class="comp-card__actions">
          <v-btn
            aria-label="编辑阵容"
            class="no-drag comp-card__action"
            icon
            size="x-small"
            variant="text"
            @click.stop="$emit('edit', comp)"
          >
            <v-icon size="17">mdi-pencil</v-icon>
          </v-btn>

          <v-btn
            aria-label="删除阵容"
            class="no-drag comp-card__action comp-card__action--danger"
            icon
            size="x-small"
            variant="text"
            @click.stop="$emit('delete', comp)"
          >
            <v-icon size="17">mdi-delete</v-icon>
          </v-btn>
        </div>
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

  const displayName = computed(() => (props.comp?.name || '').split('.', 1)[0])
  const keywordSummary = computed(() => {
    const keywords = props.comp?.keywords || []
    const visible = keywords.slice(0, 2).join(' / ')
    const remaining = keywords.length - 2

    return remaining > 0 ? `${visible} +${remaining}` : visible
  })
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
  margin-bottom: 8px;
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
  z-index: 2;
  inset: 0 auto 0 0;
  width: 2px;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--tier-color) 22%, transparent),
    var(--tier-color) 24%,
    color-mix(in srgb, var(--tier-color) 72%, white) 50%,
    var(--tier-color) 76%,
    color-mix(in srgb, var(--tier-color) 22%, transparent)
  );
  box-shadow:
    2px 0 8px color-mix(in srgb, var(--tier-color) 48%, transparent),
    4px 0 14px color-mix(in srgb, var(--tier-color) 20%, transparent);
  opacity: 0.92;
  transition:
    box-shadow 0.2s ease,
    opacity 0.2s ease;
}

.comp-card::after {
  content: '';
  position: absolute;
  z-index: 0;
  inset: 0;
  background: radial-gradient(
    ellipse 72% 150% at 0% 50%,
    color-mix(in srgb, var(--tier-color) 16%, transparent),
    color-mix(in srgb, var(--tier-color) 8%, transparent) 38%,
    transparent 72%
  );
  opacity: 0.72;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.comp-card:hover {
  border-color: rgba(255, 255, 255, 0.16);
  background: #1a2130;
}

.comp-card:hover::before {
  box-shadow:
    2px 0 10px color-mix(in srgb, var(--tier-color) 64%, transparent),
    5px 0 18px color-mix(in srgb, var(--tier-color) 28%, transparent);
  opacity: 1;
}

.comp-card:hover::after {
  opacity: 1;
}

.comp-card__row {
  position: relative;
  z-index: 1;
  min-height: 54px;
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 7px 7px 7px 11px;
}

.comp-card__tier {
  min-width: 28px;
  justify-content: center;
}

.comp-card__name,
.comp-card__code,
.comp-card__keywords {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.comp-card__name {
  min-width: 58px;
  max-width: 108px;
  flex: 1 1 92px;
  color: rgba(255, 255, 255, 0.92);
  font-size: 14px;
  font-weight: 700;
}

.comp-card__code {
  min-width: 48px;
  flex: 1 1 96px;
  color: rgba(255, 255, 255, 0.44);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 10px;
  letter-spacing: 0.02em;
}

.comp-card__keywords {
  max-width: 82px;
  flex: 0 1 82px;
  color: rgba(255, 255, 255, 0.52);
  font-size: 11px;
}

.comp-card__tier--interactive {
  min-width: 44px;
  min-height: 44px;
  cursor: pointer;
}

.comp-card__actions {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 2px;
}

.comp-card__action {
  color: rgba(255, 255, 255, 0.48);
  opacity: 0;
  pointer-events: none;
  transition:
    color 0.2s ease,
    opacity 0.2s ease;
}

.comp-card:hover .comp-card__action,
.comp-card:focus-within .comp-card__action {
  opacity: 1;
  pointer-events: auto;
}

.comp-card__action:hover {
  color: #c8aa6e;
}

.comp-card__action--danger:hover {
  color: #ff6b77;
}

@container tier-body (max-width: 330px) {
  .comp-card__keywords {
    display: none;
  }
}

@container tier-body (max-width: 275px) {
  .comp-card__code {
    display: none;
  }
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
    pointer-events: auto;
  }
}

@media (max-width: 600px) {
  .comp-card__keywords {
    display: none;
  }

  .comp-card__name {
    max-width: 116px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .comp-card,
  .comp-card::before,
  .comp-card::after {
    transition: none;
  }
}
</style>
