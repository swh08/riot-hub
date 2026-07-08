<template>
  <v-card
    class="game-card"
    :class="{ 'game-card--disabled': !game.enabled }"
    :ripple="game.enabled"
    rounded="xl"
    :style="cardStyle"
    variant="flat"
    @click="handleClick"
  >
    <div class="game-card__art">
      <v-img
        :alt="game.name"
        :aspect-ratio="16 / 10"
        cover
        :src="game.art"
      />

      <v-chip
        class="game-card__badge font-weight-medium"
        :color="game.color"
        size="small"
        :variant="game.enabled ? 'flat' : 'tonal'"
      >
        {{ game.enabled ? '已可用' : '规划中' }}
      </v-chip>
    </div>

    <div class="game-card__body pa-5">
      <div class="d-flex align-baseline ga-2">
        <span class="text-h6 font-weight-bold text-white">
          {{ game.displayName }}
        </span>
        <span
          class="game-card__tag text-caption font-weight-medium"
          :style="{ color: game.color }"
        >
          {{ game.id.toUpperCase() }}
        </span>
      </div>

      <p class="game-card__description text-body-2 mt-2 mb-0">
        {{ game.description }}
      </p>

      <v-divider class="game-card__divider my-4" />

      <div class="game-card__action d-flex align-center justify-space-between">
        <template v-if="game.enabled">
          <span class="text-body-2 font-weight-medium text-white">进入模块</span>
          <v-icon color="white" size="small">mdi-arrow-right</v-icon>
        </template>
        <template v-else>
          <span class="text-body-2 text-disabled">敬请期待</span>
          <v-icon color="grey-darken-1" size="small">mdi-lock-outline</v-icon>
        </template>
      </div>
    </div>
  </v-card>
</template>

<script setup>
  import { computed } from 'vue'
  import { useRouter } from 'vue-router'

  const props = defineProps({
    game: {
      type: Object,
      required: true,
    },
  })

  const router = useRouter()

  const cardStyle = computed(() => ({
    '--game-color': props.game.color,
  }))

  function handleClick () {
    if (props.game.enabled && props.game.route) {
      router.push(props.game.route)
    }
  }
</script>

<style scoped>
.game-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: rgba(15, 18, 25, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(8px);
  transition:
    transform 0.3s cubic-bezier(0.22, 1, 0.36, 1),
    border-color 0.3s ease,
    box-shadow 0.3s ease;
}

.game-card__art {
  position: relative;
}

/* Soften the seam between the art and the card body */
.game-card__art::after {
  content: '';
  position: absolute;
  inset: auto 0 0 0;
  height: 40%;
  background: linear-gradient(to top, rgba(15, 18, 25, 0.9), transparent);
  pointer-events: none;
}

.game-card__art :deep(.v-img__img) {
  transition: transform 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}

.game-card__badge {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 1;
  letter-spacing: 0.05em;
}

.game-card__body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.game-card__tag {
  letter-spacing: 0.14em;
  opacity: 0.9;
}

.game-card__description {
  flex: 1;
  color: rgba(255, 255, 255, 0.64);
  line-height: 1.6;
}

.game-card__divider {
  opacity: 0.08;
}

.game-card__action {
  min-height: 24px;
}

.game-card:not(.game-card--disabled) {
  cursor: pointer;
}

.game-card:not(.game-card--disabled):hover {
  transform: translateY(-8px);
  border-color: color-mix(in srgb, var(--game-color) 65%, transparent);
  box-shadow:
    0 20px 44px rgba(0, 0, 0, 0.55),
    0 0 0 1px color-mix(in srgb, var(--game-color) 25%, transparent),
    0 0 36px color-mix(in srgb, var(--game-color) 18%, transparent);
}

.game-card:not(.game-card--disabled):hover .game-card__art :deep(.v-img__img) {
  transform: scale(1.05);
}

.game-card--disabled .game-card__art {
  opacity: 0.85;
}

.game-card--disabled:hover {
  border-color: rgba(255, 255, 255, 0.14);
}
</style>
