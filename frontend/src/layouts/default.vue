<template>
  <v-app class="app-root" :style="appBackgroundStyle">
    <v-navigation-drawer
      v-model="tft.drawer"
      class="nav-drawer transparent"
      elevation="10"
      :persistent="!isMobile"
      :temporary="isMobile"
    >
      <div class="nav-inner">
        <div class="pa-3">
          <RouterLink class="d-flex align-center text-decoration-none" to="/">
            <v-img
              contain
              max-height="40"
              max-width="40"
              src="@/assets/logo.png"
            />
            <span class="text-h6 ml-2 text-white">云顶大学</span>
          </RouterLink>

          <v-text-field
            v-if="!isSettingsRoute"
            v-model="tft.search"
            class="mt-4"
            clearable
            density="compact"
            flat
            hide-details
            label="搜索阵容或关键词"
            prepend-inner-icon="mdi-magnify"
            rounded="lg"
            single-line
            variant="solo-filled"
          />
        </div>

        <div class="nav-list">
          <v-list nav>
            <template v-if="isSettingsRoute">
              <v-list-subheader>设置功能</v-list-subheader>

              <v-list-item
                v-for="section in SETTINGS_SECTIONS"
                :key="section.key"
                :active="currentSettingsSection.key === section.key"
                color="primary"
                rounded="lg"
                :title="section.title"
                @click="goSettings(section.key)"
              >
                <template #prepend>
                  <v-icon :icon="section.icon" />
                </template>
              </v-list-item>
            </template>

            <template v-else>
              <v-list-subheader>阵容</v-list-subheader>

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
                      tft.copiedKey === comp.code ? '已复制' : '复制阵容码'
                    }}</span>
                  </v-tooltip>
                </template>
              </v-list-item>

              <v-list-item
                v-if="tft.filteredComps.length === 0"
                class="nav-empty"
                rounded="lg"
                title="当前赛季暂无阵容"
              >
                <v-list-item-subtitle>
                  可以在设置里的阵容管理中上传新的阵容图。
                </v-list-item-subtitle>
              </v-list-item>
            </template>
          </v-list>
        </div>
      </div>
    </v-navigation-drawer>

    <v-app-bar class="app-bar px-3 transparent">
      <v-app-bar-nav-icon @click="tft.drawer = !tft.drawer" />
      <v-spacer v-if="!isMobile" />

      <v-app-bar-title class="toolbar-title">
        <div class="app-title text-center">
          <div class="app-title__caption text-caption text-medium-emphasis">
            {{ isSettingsRoute ? '设置中心' : '阵容总览' }}
          </div>

          <div
            v-if="!isSettingsRoute && tft.currentComp"
            class="text-h6 font-weight-bold d-flex align-center justify-center ga-2 flex-wrap"
          >
            <v-chip
              class="font-weight-bold"
              :color="tft.tierColor(tft.currentComp.tierLevel)"
              variant="outlined"
            >
              {{ tft.currentComp.tierName }}
            </v-chip>
            <span>{{ tft.currentComp.name }}</span>
          </div>

          <div v-else class="text-h6 font-weight-bold">
            {{ appBarTitle }}
          </div>
        </div>
      </v-app-bar-title>

      <v-spacer v-if="!isMobile" />

      <div class="season-switcher mr-3">
        <v-select
          density="compact"
          :disabled="tft.seasonLoading || tft.seasonOptions.length === 0"
          flat
          hide-details
          :items="tft.seasonOptions"
          :loading="tft.seasonLoading"
          :model-value="tft.season"
          placeholder="赛季"
          rounded="lg"
          variant="solo-filled"
          @update:model-value="handleSeasonChange"
        />
      </div>

      <v-menu v-model="menuOpen" scrim width="220">
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
              v-if="isSettingsRoute"
              color="primary"
              rounded="lg"
              title="返回阵容"
              @click="goHome"
            >
              <template #prepend>
                <v-icon>mdi-view-grid-outline</v-icon>
              </template>
            </v-list-item>

            <v-list-item
              v-else
              color="primary"
              rounded="lg"
              title="设置中心"
              @click="goSettings()"
            >
              <template #prepend>
                <v-icon>mdi-cog-outline</v-icon>
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
  import { computed, onMounted, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useDisplay } from 'vuetify'
  import {
    getSettingsSection,
    normalizeSettingsSection,
    SETTINGS_SECTIONS,
  } from '@/constants/settings'
  import { useTftStore } from '@/stores/tft'

  const route = useRoute()
  const router = useRouter()
  const tft = useTftStore()
  const { smAndDown } = useDisplay()

  const menuOpen = ref(false)

  const isMobile = computed(() => smAndDown.value)
  const isSettingsRoute = computed(() => route.path.startsWith('/settings'))
  const currentSettingsSection = computed(() =>
    getSettingsSection(route.query.section),
  )
  const appBackgroundStyle = computed(() => {
    const appBarHeight = isMobile.value ? '96px' : '64px'

    return {
      '--app-background-image': tft.currentSeasonBackground
        ? `url("${tft.currentSeasonBackground}")`
        : 'none',
      '--app-bar-height': appBarHeight,
    }
  })
  const appBarTitle = computed(() => {
    if (isSettingsRoute.value) {
      return currentSettingsSection.value.title
    }

    return tft.currentComp?.name || '阵容'
  })

  onMounted(async () => {
    await tft.initializeSeason()
  })

  watch(
    () => route.fullPath,
    () => {
      if (isMobile.value) {
        tft.drawer = false
      }
    },
  )

  watch(
    isMobile,
    mobile => {
      tft.drawer = !mobile
    },
    { immediate: true },
  )

  function goSettings (section = normalizeSettingsSection(route.query.section)) {
    menuOpen.value = false
    router.push({
      path: '/settings',
      query: {
        section: normalizeSettingsSection(section),
      },
    })
  }

  function goHome () {
    menuOpen.value = false
    router.push('/')
  }

  async function handleSeasonChange (nextSeason) {
    if (!nextSeason || nextSeason === tft.season) return
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
    var(--app-background-image) center / cover no-repeat fixed;
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

.nav-empty {
  margin: 8px;
  background: rgba(255, 255, 255, 0.03);
}

.app-root {
  height: 100dvh;
  min-height: 100svh;
  overflow: hidden;
}

.main-root {
  height: calc(100dvh - var(--app-bar-height));
  min-height: 0;
  overflow: hidden;
}

.app-title {
  line-height: 1.2;
  min-width: 0;
}

.toolbar-title {
  min-width: 0;
}

.season-switcher {
  width: min(220px, 32vw);
}

@media (max-width: 600px) {
  .app-root {
    overflow: auto;
  }

  .main-root {
    height: auto;
    min-height: calc(100dvh - var(--app-bar-height));
    overflow: auto;
  }

  .season-switcher {
    width: min(132px, 34vw);
    min-width: 108px;
    margin-right: 8px !important;
  }

  .app-bar {
    padding-inline: 8px !important;
  }

  .toolbar-title {
    flex: 1 1 auto;
    min-width: 0;
    margin-inline: 8px 6px;
  }

  .app-title {
    text-align: left !important;
  }

  .app-title__caption {
    display: none;
  }

  .app-title :deep(.text-h6) {
    font-size: 1rem !important;
  }
}
</style>
