<template>
  <v-app class="app-root">
    <v-navigation-drawer
      v-model="tft.drawer"
      class="nav-drawer transparent"
      elevation="10"
      persistent
    >
      <div class="nav-inner">
        <div class="pa-3">
          <a class="d-flex align-center text-decoration-none" href="/">
            <v-img
              contain
              max-height="40"
              max-width="40"
              src="@/assets/logo.png"
            />
            <span class="text-h6 ml-2">云顶大学</span>
          </a>

          <v-text-field
            v-model="tft.search"
            class="mt-4"
            clearable
            density="compact"
            flat
            hide-details
            label="搜索阵容或装备"
            prepend-inner-icon="mdi-magnify"
            rounded="lg"
            single-line
            variant="solo-filled"
          />
        </div>

        <div class="nav-list">
          <v-list nav>
            <v-list-item
              v-for="comp in tft.filteredComps"
              :key="comp.uid"
              color="primary"
              rounded="lg"
              :title="comp.name"
              :value="comp.uid"
              @click="tft.selectComp(comp)"
            >
              <template #prepend>
                <v-chip
                  class="ma-2 text-h5 font-weight-bold"
                  :color="tft.tierColor(comp.tierLevel)"
                  variant="text"
                >
                  {{ comp.tierName }}
                </v-chip>
              </template>

              <template #append>
                <v-tooltip location="left">
                  <template #activator="{ props }">
                    <v-icon
                      v-bind="props"
                      class="cursor-pointer"
                      :color="
                        tft.copiedKey === comp.code ? 'success' : undefined
                      "
                      :icon="
                        tft.copiedKey === comp.code
                          ? 'mdi-check'
                          : 'mdi-content-copy'
                      "
                      @click.stop="tft.handleCopy(comp.code)"
                    />
                  </template>
                  <span>{{
                    tft.copiedKey === comp.code ? "已复制" : "复制"
                  }}</span>
                </v-tooltip>
              </template>
            </v-list-item>
          </v-list>
        </div>
      </div>
    </v-navigation-drawer>

    <v-app-bar class="px-3 transparent">
      <v-spacer />
      <v-app-bar-title v-if="tft.currentComp">
        <div class="text-center text-h6 font-weight-bold">
          <v-chip
            class="font-weight-bold"
            :color="tft.tierColor(tft.currentComp.tierLevel)"
            variant="outlined"
          >
            {{ tft.currentComp.tierName }}
          </v-chip>
          {{ tft.currentComp.name }}
        </div>
      </v-app-bar-title>
      <v-spacer />

      <div class="season-switcher mr-3">
        <v-select
          density="compact"
          :disabled="tft.seasonLoading || tft.seasonOptions.length === 0"
          flat
          hide-details
          :items="tft.seasonOptions"
          label="赛季"
          :loading="tft.seasonLoading"
          :model-value="tft.season"
          rounded="lg"
          variant="solo-filled"
          @update:model-value="handleSeasonChange"
        />
      </div>

      <v-menu v-model="menuOpen" scrim width="200">
        <template #activator="{ props }">
          <v-btn icon v-bind="props">
            <v-avatar>
              <v-icon>mdi-widgets</v-icon>
            </v-avatar>
          </v-btn>
        </template>

        <v-card rounded="lg" variant="tonal">
          <v-list class="pa-2" nav>
            <v-list-item
              color="primary"
              rounded="lg"
              title="Settings"
              @click="goSettings"
            >
              <template #prepend>
                <v-icon>mdi-cog</v-icon>
              </template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-menu>
    </v-app-bar>

    <v-main class="main-root">
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
  import { onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useTftStore } from '@/stores/tft'

  const router = useRouter()
  const tft = useTftStore()

  const menuOpen = ref(false)

  onMounted(async () => {
    await tft.initializeSeason()
  })

  function goSettings () {
    menuOpen.value = false
    router.push('/settings')
  }

  async function handleSeasonChange (nextSeason) {
    if (!nextSeason) return
    await tft.changeSeason(nextSeason)
  }
</script>

<style scoped>
.app-root :deep(.v-application__wrap) {
  background:
    radial-gradient(
      ellipse at center,
      rgba(0, 0, 0, 0) 40%,
      rgba(0, 0, 0, 0.45) 70%,
      rgba(0, 0, 0, 0.75) 100%
    ),
    url("@/assets/background.webp") center / cover no-repeat fixed;
}

.nav-drawer :deep(.v-navigation-drawer__content) {
  overflow: hidden;
}

.nav-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.nav-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  scrollbar-width: thin;
}

.app-root {
  height: 100vh;
  overflow: hidden;
}

.main-root {
  height: calc(100vh - 64px);
  overflow: hidden;
}

.season-switcher {
  width: min(220px, 32vw);
}
</style>
