<template>
  <div class="hub-page" :style="hubStyle">
    <v-container class="hub-container py-12">
      <div class="hub-brand text-center mb-12">
        <h1 class="hub-brand__title mx-auto">
          <v-img
            alt="Riot Hub"
            contain
            max-width="280"
            src="@/assets/brand/riot-hub-logo.png"
          />
        </h1>
        <p class="hub-brand__subtitle text-subtitle-1 mt-5">
          选择一个游戏开始
        </p>
      </div>

      <v-row justify="center">
        <v-col
          v-for="game in GAMES"
          :key="game.id"
          cols="12"
          md="4"
          sm="6"
        >
          <GameCard :game="game" />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
  import GameCard from '@/components/hub/GameCard.vue'
  import { GAMES } from '@/constants/games'

  // Every image dropped into assets/hub-backgrounds/ automatically
  // joins the random rotation; no code changes needed.
  const backgrounds = Object.values(
    import.meta.glob('@/assets/hub-backgrounds/*', {
      eager: true,
      import: 'default',
    }),
  )

  const background = backgrounds[Math.floor(Math.random() * backgrounds.length)]

  const hubStyle = {
    '--hub-background-image': background ? `url("${background}")` : 'none',
  }
</script>

<style scoped>
.hub-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  background:
    radial-gradient(
      ellipse at center,
      rgba(0, 0, 0, 0.35) 0%,
      rgba(0, 0, 0, 0.65) 70%,
      rgba(0, 0, 0, 0.85) 100%
    ),
    var(--hub-background-image) center / cover no-repeat fixed;
}

.hub-container {
  max-width: 1100px;
}

.hub-brand__title {
  max-width: 280px;
  filter:
    drop-shadow(0 2px 6px rgba(0, 0, 0, 0.9))
    drop-shadow(0 8px 28px rgba(0, 0, 0, 0.65));
}

.hub-brand__subtitle {
  color: rgba(255, 255, 255, 0.92);
  text-shadow:
    0 1px 3px rgba(0, 0, 0, 0.9),
    0 4px 14px rgba(0, 0, 0, 0.7);
}
</style>
