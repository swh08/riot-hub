<template>
  <v-app>
    <router-view />
  </v-app>
</template>

<script setup>
//
</script>

<style scoped>
.v-application {
  background:
    radial-gradient(
      ellipse at center,
      rgba(0, 0, 0, 0) 40%,
      rgba(0, 0, 0, 0.45) 70%,
      rgba(0, 0, 0, 0.75) 100%
    ),
    url("@/assets/background.webp") center / cover no-repeat fixed;
}
</style>
