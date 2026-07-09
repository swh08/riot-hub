<template>
  <div class="game-card-stack">
    <div
      ref="deckEl"
      class="game-card-stack__deck"
      :class="{ 'game-card-stack__deck--dragging': dragging }"
      @click.capture="handleClickCapture"
      @pointercancel="endDrag"
      @pointerdown="startDrag"
      @pointermove="moveDrag"
      @pointerup="endDrag"
    >
      <div
        v-for="(game, index) in games"
        :key="game.id"
        class="game-card-stack__item"
        :style="itemStyle(index)"
      >
        <GameCard :game="game" />
      </div>
    </div>

    <div class="game-card-stack__dots">
      <button
        v-for="(game, index) in games"
        :key="game.id"
        :aria-label="`切换到 ${game.displayName}`"
        class="game-card-stack__dot"
        :class="{ 'game-card-stack__dot--active': index === activeIndex }"
        type="button"
        @click="goTo(index)"
      />
    </div>
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import GameCard from '@/components/hub/GameCard.vue'

  const props = defineProps({
    games: {
      type: Array,
      required: true,
    },
  })

  // Depth step between stacked cards, in px / scale / opacity units.
  const STEP_Y = 18
  const STEP_SCALE = 0.055
  const STEP_OPACITY = 0.16
  const SWIPE_DISTANCE = 90
  const FLICK_VELOCITY = 0.55

  const deckEl = ref(null)
  const activeIndex = ref(0)
  const dragX = ref(0)
  const dragging = ref(false)

  let pointerId = null
  let startX = 0
  let startY = 0
  let lastX = 0
  let lastTime = 0
  let velocity = 0
  let axis = null
  let suppressClick = false

  const count = computed(() => props.games.length)

  function slotOffset (index) {
    return (index - activeIndex.value + count.value) % count.value
  }

  function itemStyle (index) {
    const offset = slotOffset(index)

    if (offset === 0) {
      return {
        zIndex: count.value,
        transform: `translate3d(${dragX.value}px, 0, 0) rotate(${dragX.value * 0.04}deg)`,
      }
    }

    // While the front card is dragged away, cards behind slide one slot forward.
    const progress = Math.min(Math.abs(dragX.value) / 240, 1)
    const depth = offset - progress

    return {
      zIndex: count.value - offset,
      opacity: Math.max(1 - depth * STEP_OPACITY, 0),
      transform: `translate3d(0, ${depth * -STEP_Y}px, 0) scale(${1 - depth * STEP_SCALE})`,
      pointerEvents: 'none',
    }
  }

  function startDrag (event) {
    if (!event.isPrimary || pointerId !== null) {
      return
    }

    pointerId = event.pointerId
    startX = event.clientX
    startY = event.clientY
    lastX = event.clientX
    lastTime = event.timeStamp
    velocity = 0
    axis = null
    suppressClick = false
    dragging.value = true
  }

  function moveDrag (event) {
    if (event.pointerId !== pointerId) {
      return
    }

    const dx = event.clientX - startX
    const dy = event.clientY - startY

    if (!axis) {
      if (Math.abs(dx) < 6 && Math.abs(dy) < 6) {
        return
      }

      axis = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y'

      if (axis === 'y') {
        // Let the browser keep handling vertical scrolling.
        resetPointerState()
        return
      }

      try {
        deckEl.value?.setPointerCapture(pointerId)
      } catch {
        // Synthetic pointers cannot be captured; dragging still works.
      }
    }

    if (event.timeStamp > lastTime) {
      velocity = (event.clientX - lastX) / (event.timeStamp - lastTime)
    }
    lastX = event.clientX
    lastTime = event.timeStamp

    dragX.value = dx

    if (Math.abs(dx) > 10) {
      suppressClick = true
    }
  }

  function endDrag (event) {
    if (event.pointerId !== pointerId) {
      return
    }

    const dx = dragX.value
    const flicked = Math.abs(velocity) > FLICK_VELOCITY && Math.abs(dx) > 24

    let direction = 0
    if (Math.abs(dx) > SWIPE_DISTANCE) {
      direction = dx < 0 ? 1 : -1
    } else if (flicked) {
      direction = velocity < 0 ? 1 : -1
    }

    resetPointerState()

    if (direction) {
      completeSwipe(direction)
    } else {
      dragX.value = 0
    }
  }

  function resetPointerState () {
    pointerId = null
    axis = null
    dragging.value = false
  }

  function completeSwipe (exitDirection) {
    // Phase 1: let the card keep flying in the swipe direction, then
    // phase 2 retargets the still-running transition into the back slot.
    const exitX = (deckEl.value?.clientWidth || 320) * 0.6
    dragX.value = exitDirection === 1 ? -exitX : exitX

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        activeIndex.value = (activeIndex.value + 1) % count.value
        dragX.value = 0
      })
    })
  }

  function goTo (index) {
    activeIndex.value = index
    dragX.value = 0
  }

  function handleClickCapture (event) {
    if (suppressClick) {
      event.stopPropagation()
      event.preventDefault()
      suppressClick = false
    }
  }
</script>

<style scoped>
.game-card-stack {
  max-width: 400px;
  margin-inline: auto;
}

.game-card-stack__deck {
  position: relative;
  display: grid;
  /* Headroom for the cards peeking out above the front one */
  padding-top: calc(18px * 2 + 6px);
  touch-action: pan-y;
  user-select: none;
  -webkit-user-select: none;
}

.game-card-stack__item {
  grid-area: 1 / 1;
  /* Scale from the top edge so back cards actually peek out above */
  transform-origin: 50% 0;
  transition:
    transform 0.55s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.55s cubic-bezier(0.22, 1, 0.36, 1);
  will-change: transform, opacity;
}

.game-card-stack__deck--dragging .game-card-stack__item {
  transition: none;
}

/* The wrapper owns all motion; disable the card's own hover lift here. */
.game-card-stack__item :deep(.game-card:hover) {
  transform: none;
}

/* Cards overlap in the deck, so the glassy translucent background would
   let the cards behind bleed through. Make it opaque here. */
.game-card-stack__item :deep(.game-card) {
  background: rgb(18, 21, 29);
  box-shadow: 0 -10px 28px rgba(0, 0, 0, 0.45);
}

.game-card-stack__dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
}

.game-card-stack__dot {
  width: 8px;
  height: 8px;
  padding: 0;
  border: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.28);
  cursor: pointer;
  transition:
    width 0.3s cubic-bezier(0.22, 1, 0.36, 1),
    background-color 0.3s ease;
}

.game-card-stack__dot--active {
  width: 24px;
  background: rgba(255, 255, 255, 0.85);
}
</style>
