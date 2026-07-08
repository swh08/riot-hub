<template>
  <v-card
    class="game-card"
    :class="{ 'game-card--disabled': !game.enabled }"
    :disabled="!game.enabled"
    :ripple="game.enabled"
    rounded="xl"
    :style="cardStyle"
    variant="flat"
    @click="handleClick"
  >
    <div class="game-card__inner pa-6">
      <div class="game-card__accent" />

      <div class="d-flex align-center justify-space-between">
        <span
          class="game-card__id text-overline font-weight-bold"
          :style="{ color: game.color }"
        >
          {{ game.id.toUpperCase() }}
        </span>

        <v-chip
          v-if="!game.enabled"
          class="game-card__badge"
          color="grey"
          size="small"
          variant="tonal"
        >
          敬请期待 / Coming Soon
        </v-chip>
      </div>

      <div class="mt-6">
        <div class="text-h5 font-weight-bold text-white">
          {{ game.displayName }}
        </div>
        <div class="text-subtitle-2 text-medium-emphasis mt-1">
          {{ game.name }}
        </div>
      </div>

      <div class="game-card__description text-body-2 mt-4">
        {{ game.description }}
      </div>

      <div class="d-flex align-center mt-6">
        <template v-if="game.enabled">
          <span class="text-button" :style="{ color: game.color }">进入</span>
          <v-icon class="ml-1" :color="game.color" size="small">
            mdi-arrow-right
          </v-icon>
        </template>
        <span v-else class="text-button text-disabled">开发中</span>
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
  position: relative;
  height: 100%;
  background: rgba(18, 22, 30, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

.game-card__inner {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.game-card__accent {
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: var(--game-color);
  opacity: 0.9;
  border-radius: 0 4px 4px 0;
}

.game-card__description {
  flex: 1;
  color: rgba(255, 255, 255, 0.72);
}

.game-card:not(.game-card--disabled):hover {
  transform: translateY(-6px);
  border-color: var(--game-color);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
  cursor: pointer;
}

.game-card--disabled {
  filter: grayscale(0.9);
  opacity: 0.65;
}
</style>
