<template>
  <div class="hub-page">
    <v-container class="hub-container py-12">
      <div class="hub-brand text-center mb-12">
        <v-img
          class="mx-auto"
          contain
          max-height="88"
          max-width="88"
          src="@/assets/logo.png"
        />
        <h1 class="text-h3 font-weight-bold text-white mt-4">Riot Hub</h1>
        <p class="text-subtitle-1 text-medium-emphasis mt-2">
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
    url('@/assets/background.webp') center / cover no-repeat fixed;
}

.hub-container {
  max-width: 1100px;
}
</style>
