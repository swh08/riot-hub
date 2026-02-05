<template>
  <div class="settings-root pa-4">
    <div class="d-flex align-center mb-4">
      <div class="text-h5 font-weight-bold">阵容编辑</div>
      <v-spacer />

      <v-btn class="mr-2 rounded-lg" :loading="loading" @click="reload">
        刷新
      </v-btn>

      <v-progress-circular
        v-if="saving"
        indeterminate
        size="22"
        width="2"
        class="ml-2"
      />
    </div>

    <v-alert v-if="errorMsg" type="error" class="mb-4" density="compact">
      {{ errorMsg }}
    </v-alert>

    <v-row class="settings-row" dense>
      <v-col cols="12" md="4" class="h-100">
        <TierColumn
          title="S"
          :items="sList"
          group="tiers"
          @change="(evt) => onDrop(evt, 0)"
        />
      </v-col>

      <v-col cols="12" md="4" class="h-100">
        <TierColumn
          title="A"
          :items="aList"
          group="tiers"
          @change="(evt) => onDrop(evt, 1)"
        />
      </v-col>

      <v-col cols="12" md="4" class="h-100">
        <TierColumn
          title="B"
          :items="bList"
          group="tiers"
          @change="(evt) => onDrop(evt, 2)"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useTftStore } from "@/stores/tft";
import TierColumn from "@/components/tft/TierColumn.vue";

const tft = useTftStore();

const loading = ref(false);
const saving = ref(false);
const errorMsg = ref("");

/**
 * 这里用“本地三份数组”是为了拖拽手感最好：
 * draggable 会直接 mutate list。
 * 然后 drop 完才把变化同步到后端 & store。
 */
const sList = ref([]);
const aList = ref([]);
const bList = ref([]);

/**
 * 用来判断“放手后强度是否真的变化”
 * uid -> "0"/"1"/"2"
 */
const uidToPrevTier = ref(new Map());

function buildLocalListsFromStore() {
  const s = [];
  const a = [];
  const b = [];
  const m = new Map();

  for (const c of tft.comps) {
    const tier = String(c.tierLevel);
    m.set(c.uid, tier);

    if (tier === "0") s.push(c);
    else if (tier === "1") a.push(c);
    else b.push(c);
  }

  uidToPrevTier.value = m;
  sList.value = s;
  aList.value = a;
  bList.value = b;
}

async function reload() {
  loading.value = true;
  errorMsg.value = "";
  try {
    await tft.loadComps();
    buildLocalListsFromStore();
  } catch (e) {
    errorMsg.value = e?.response?.data?.detail || e?.message || "刷新失败";
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  // 进入 settings 时，确保 store 有数据
  //（如果 layout 已经 load 过，这里不会多打请求）
  if (tft.comps.length === 0) {
    await reload();
  } else {
    buildLocalListsFromStore();
  }
});

/**
 * draggable @change 事件：
 * - evt.moved：同列排序（不改 tier）
 * - evt.added：从别列拖进来（tier 可能变化）
 *
 * 注意：我们“返回空就行”的策略里，season 不存在会给空 list，
 * 这里也能正常工作。
 */
async function onDrop(evt, newTierLevel) {
  // 同列排序：不更新强度
  if (evt?.moved) return;

  // 只有跨列 added 才会触发强度变更
  const added = evt?.added;
  if (!added) return;

  const item = added.element; // 被拖拽的 comp
  if (!item?.uid) return;

  const prevTier = uidToPrevTier.value.get(item.uid); // "0"/"1"/"2"
  const nextTier = String(newTierLevel);

  // tier 没变：不 call 后端
  if (prevTier === nextTier) return;

  saving.value = true;
  errorMsg.value = "";

  try {
    // ✅ 更新后端 + 同步 store
    await tft.patchComp(item.uid, {
      tier_level: newTierLevel,
      tier_display: { 0: "S", 1: "A", 2: "B" }[newTierLevel],
    });

    // ✅ 更新 map，避免重复 PATCH
    uidToPrevTier.value.set(item.uid, nextTier);
  } catch (e) {
    errorMsg.value =
      e?.response?.data?.detail || e?.message || "更新强度失败，已回滚";

    // ❗ 回滚：重新拉后端，重建本地三列
    await tft.loadComps();
    buildLocalListsFromStore();
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
/* ✅ 页面不滚动 */
.settings-root {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* ✅ 三列区域占满剩余高度 */
.settings-row {
  flex: 1;
  min-height: 0;
}

/* v-col 需要可收缩，否则内部滚动容易失效 */
.h-100 {
  height: 100%;
  min-height: 0;
}
</style>
