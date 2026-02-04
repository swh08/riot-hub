<template>
  <v-navigation-drawer
    v-model="drawer"
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
          v-model="search"
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
            v-for="comp in filterdComps"
            :key="comp.name"
            color="primary"
            rounded="lg"
            :title="comp.name"
            :value="comp.name"
            @click="currentComp = comp"
          >
            <template #prepend>
              <v-chip
                class="ma-2 font-weight-bold"
                :color="tierColor(comp.tierLevel)"
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

  <v-app-bar class="px-3 transparent">
    <v-spacer />
    <v-app-bar-title v-if="currentComp">
      <div class="text-center text-h6 font-weight-bold">
        <v-chip
          class="font-weight-bold"
          :color="tierColor(currentComp.tierLevel)"
          variant="outlined"
        >
          {{ currentComp.tierName }}
        </v-chip>
        {{ currentComp.name }}
      </div>
    </v-app-bar-title>
    <v-spacer />
    <v-menu scrim width="200">
      <template v-slot:activator="{ props }">
        <v-btn icon v-bind="props">
          <v-avatar>
            <v-icon>mdi-widgets</v-icon>
          </v-avatar>
        </v-btn>
      </template>
      <v-card rounded="lg">
        <v-list nav>
          <v-list-item
            v-for="menu in menuItems"
            :key="menu.title"
            color="primary"
            rounded="lg"
            :title="menu.title"
            :value="menu.title"
            @click="handleMenuClick(menu)"
          >
            <template #prepend>
              <v-icon>
                {{ menu.icon }}
              </v-icon>
            </template>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </v-app-bar>

  <v-card tile class="transparent">
    <v-img
      v-if="currentComp"
      contain
      max-height="calc(100vh - 64px)"
      :src="currentComp.image"
    />
  </v-card>
</template>

<script setup>
import { computed, ref, onMounted, watch } from "vue";
import { http } from "@/api/axios";
import { useRouter } from "vue-router";

const router = useRouter();

const drawer = ref(null);
const search = ref(null);
const currentComp = ref(null);

const copiedKey = ref(null);
let copiedTimer = null;

const comps = ref([]);
const season = ref("");

const menuItems = ref([
  { title: "Settings", value: "settings", icon: "mdi-cog" },
]);

function mapTierName(tierLevel) {
  switch (Number(tierLevel)) {
    case 0:
      return "S";
    case 1:
      return "A";
    case 2:
      return "B";
    default:
      return String(tierLevel ?? "");
  }
}

function mappedPayload(item) {
  return {
    uid: item.uid,
    tierLevel: String(item.tier_level),
    tierName: item.tier_display || mapTierName(item.tier_level),
    name: item.filename,
    keywords: item.keywords || [],
    code: item.comp_code,
    image: item.image_url || item.image,
    raw: item,
  };
}

async function loadComps() {
  const params = {};
  if (season.value) params.season = season.value;

  const res = await http.get("/api/images/", { params });

  comps.value = res.data.map(mappedPayload);
}

onMounted(loadComps);

watch(season, () => {
  loadComps();
});

const filterdComps = computed(() => {
  const keyword = (search.value ?? "").trim().toLowerCase();

  const list = keyword
    ? comps.value.filter(
        (comp) =>
          comp.name.toLowerCase().includes(keyword) ||
          comp.keywords.some((kw) => kw.toLowerCase().includes(keyword)),
      )
    : comps.value;

  return [...list].sort((a, b) => a.tierLevel.localeCompare(b.tierLevel));
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

function handleMenuClick(menu) {
  console.log("Clicked menu:", menu);
  if (menu.value === "settings") {
    router.push("/settings");
  }
}

function tierColor(tierLevel) {
  switch (tierLevel) {
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

.transparent {
  background-color: transparent !important;
  backdrop-filter: blur(8px);
}
</style>
