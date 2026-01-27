<template>
  <v-navigation-drawer v-model="drawer" persistent class="nav-drawer">
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
          v-model="search"
          class="mt-4"
          density="compact"
          prepend-inner-icon="mdi-magnify"
          variant="solo-filled"
          label="搜索阵容或装备"
          flat
          clearable
          single-line
          hide-details
        />
      </div>

      <div class="nav-list">
        <v-list nav>
          <v-list-item
            v-for="comp in filterdComps"
            :key="comp.name"
            color="primary"
            :title="comp.name"
            :value="comp.name"
            @click="currentComp = comp"
          >
            <template #prepend>
              <v-chip
                class="ma-2 font-weight-bold"
                :color="tierColor(comp.tier)"
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
                    :color="copiedKey === comp.code ? 'success' : undefined"
                    :icon="
                      copiedKey === comp.code ? 'mdi-check' : 'mdi-content-copy'
                    "
                    @click.stop="handleCopy(comp.code)"
                  />
                </template>
                <span>{{ copiedKey === comp.code ? "已复制" : "复制" }}</span>
              </v-tooltip>
            </template>
          </v-list-item>
        </v-list>
      </div>
    </div>
  </v-navigation-drawer>

  <v-app-bar>
    <v-app-bar-title v-if="currentComp">
      <div class="text-center text-h6 font-weight-bold">
        <v-chip class="font-weight-bold" :color="tierColor(currentComp.tier)">
          {{ currentComp.tierName }}
        </v-chip>
        {{ currentComp.name }}
      </div>
    </v-app-bar-title>
  </v-app-bar>

  <v-card tile>
    <v-img
      v-if="currentComp"
      contain
      max-height="calc(100vh - 64px)"
      :src="currentComp.image"
    />
  </v-card>
</template>

<script setup>
import { computed, ref } from "vue";

const drawer = ref(null);
const search = ref(null);
const currentComp = ref(null);

const copiedKey = ref(null);
let copiedTimer = null;

const comps = ref([
  {
    tier: "0",
    tierName: "S",
    name: "比尔95",
    artifacts: ["黎明核心", "护臂"],
    code: "比尔95",
    image:
      "https://images.pexels.com/photos/33315262/pexels-photo-33315262.jpeg",
  },
  {
    tier: "1",
    tierName: "A",
    name: "炸弹人95",
    artifacts: ["黎明核心"],
    code: "炸弹人95",
    image:
      "https://images.pexels.com/photos/34314127/pexels-photo-34314127.jpeg",
  },
  {
    tier: "1",
    tierName: "A",
    name: "德玛琴女",
    artifacts: ["巫妖之祸"],
    code: "德玛琴女",
    image:
      "https://images.pexels.com/photos/34314126/pexels-photo-34314126.jpeg",
  },
]);

const filterdComps = computed(() => {
  const keyword = (search.value ?? "").trim().toLowerCase();

  const list = keyword
    ? comps.value.filter(
        (comp) =>
          comp.name.toLowerCase().includes(keyword) ||
          comp.artifacts.some((artifact) =>
            artifact.toLowerCase().includes(keyword),
          ),
      )
    : comps.value;

  return [...list].sort((a, b) => a.tier.localeCompare(b.tier));
});

async function handleCopy(code) {
  await navigator.clipboard.writeText(code);

  copiedKey.value = code;

  if (copiedTimer) clearTimeout(copiedTimer);
  copiedTimer = setTimeout(() => {
    copiedKey.value = null;
    copiedTimer = null;
  }, 1500);
}

function tierColor(tier) {
  switch (tier) {
    case "0":
      return "red";
    case "1":
      return "orange";
    case "2":
      return "yellow";
    default:
      return "grey";
  }
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

.v-app-bar,
.v-navigation-drawer,
.v-card {
  background-color: rgba(20, 20, 20, 0.6) !important;
  backdrop-filter: blur(6px);
}
</style>
