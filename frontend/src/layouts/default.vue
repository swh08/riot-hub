<template>
  <v-app>
    <v-navigation-drawer
      v-model="tft.drawer"
      persistent
      class="nav-drawer transparent"
      elevation="10"
    >
      <div class="nav-inner">
        <div class="pa-3">
          <a href="/" class="d-flex align-center text-decoration-none">
            <v-img
              src="@/assets/logo.png"
              max-width="40"
              max-height="40"
              contain
            />
            <span class="text-h6 ml-2">云顶大学</span>
          </a>

          <v-text-field
            v-model="tft.search"
            class="mt-4"
            density="compact"
            prepend-inner-icon="mdi-magnify"
            variant="solo-filled"
            label="搜索阵容或装备"
            rounded="lg"
            flat
            clearable
            single-line
            hide-details
          />
        </div>

        <div class="nav-list">
          <v-list nav>
            <v-list-item
              v-for="comp in tft.filterdComps"
              :key="comp.uid"
              color="primary"
              rounded="lg"
              :title="comp.name"
              :value="comp.uid"
              @click="tft.selectComp(comp)"
            >
              <template #prepend>
                <v-chip
                  class="ma-2 font-weight-bold"
                  :color="tft.tierColor(comp.tierLevel)"
                  variant="outlined"
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

      <v-menu v-model="menuOpen" scrim width="200">
        <template #activator="{ props }">
          <v-btn icon v-bind="props">
            <v-avatar>
              <v-icon>mdi-widgets</v-icon>
            </v-avatar>
          </v-btn>
        </template>

        <v-card rounded="lg">
          <v-list nav>
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

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useTftStore } from "@/stores/tft";

const router = useRouter();
const tft = useTftStore();

const menuOpen = ref(false);

onMounted(() => {
  if (tft.comps.length === 0) tft.loadComps();
});

function goSettings() {
  menuOpen.value = false;
  router.push("/settings");
}
</script>

<style scoped>
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

.transparent {
  background-color: transparent !important;
  backdrop-filter: blur(8px);
}
</style>
