<template>
  <v-card class="tier-card transparent" rounded="lg">
    <v-card-title class="tier-header d-flex align-center my-2">
      <v-chip class="text-h6 font-weight-bold">{{ title }}</v-chip>
      <v-spacer />
      <v-chip variant="outlined">{{ items.length }}</v-chip>
    </v-card-title>

    <v-divider />

    <v-card-text class="tier-body">
      <Draggable
        class="drop-zone"
        :list="items"
        item-key="uid"
        :group="{ name: group, pull: true, put: true }"
        :animation="150"
        :force-fallback="true"
        :fallback-on-body="true"
        :fallback-tolerance="8"
        :scroll="true"
        :scroll-sensitivity="80"
        :scroll-speed="14"
        :swap-threshold="0.85"
        :invert-swap="true"
        :empty-insert-threshold="24"
        ghost-class="drag-ghost"
        chosen-class="drag-chosen"
        drag-class="drag-dragging"
        :filter="'.no-drag, button, input, textarea, select, a'"
        :prevent-on-filter="false"
        @change="$emit('change', $event)"
      >
        <template #item="{ element }">
          <v-card class="mb-2 comp-card" rounded="lg" variant="tonal">
            <v-card-title class="d-flex align-center">
              <div class="text-subtitle-1 font-weight-bold text-truncate">
                <v-chip>
                  {{ element.tierName }}
                </v-chip>
                {{ element.name.split(".")[0] }}
              </div>

              <v-spacer />

              <v-btn
                class="no-drag"
                icon
                size="small"
                variant="text"
                color="warning"
                @click.stop="openEdit(element)"
              >
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
            </v-card-title>

            <v-card-subtitle class="text-caption mb-2">
              {{ element.code }}
            </v-card-subtitle>

            <div v-if="(element.keywords || []).length" class="px-4 pb-3">
              <v-chip
                v-for="kw in element.keywords.slice(0, 6)"
                :key="kw"
                class="mr-1 mb-1"
                size="x-small"
                variant="outlined"
              >
                {{ kw }}
              </v-chip>
            </div>
          </v-card>
        </template>
      </Draggable>

      <div v-if="items.length === 0" class="empty-overlay">拖拽阵容到这里</div>
    </v-card-text>
  </v-card>

  <v-dialog v-model="edit.open" max-width="560">
    <v-card rounded="lg">
      <v-card-title class="d-flex align-center">
        <span class="text-h6 font-weight-bold">编辑阵容</span>
        <v-spacer />
        <v-btn icon variant="text" @click="edit.open = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-card-text>
        <v-text-field
          class="no-drag"
          label="阵容码"
          variant="outlined"
          v-model="edit.compCode"
          hide-details
        />

        <div class="mt-4">
          <div class="d-flex align-center">
            <v-text-field
              class="no-drag"
              v-model="edit.keywordInput"
              label="添加关键词"
              variant="outlined"
              hide-details
              @keyup.enter="addKeyword"
            />
            <v-btn
              class="no-drag ml-2"
              icon
              variant="outlined"
              @click="addKeyword"
              :disabled="!edit.keywordInput.trim()"
            >
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </div>

          <div class="mt-3">
            <v-chip
              v-for="keyword in edit.keywords"
              :key="keyword"
              class="mr-2 mb-2"
              closable
              @click:close="removeKeyword(keyword)"
              variant="outlined"
            >
              {{ keyword }}
            </v-chip>

            <div
              v-if="edit.keywords.length === 0"
              class="text-caption text-medium-emphasis"
            >
              暂无关键词
            </div>
          </div>
        </div>

        <v-alert v-if="edit.error" type="error" density="compact" class="mt-4">
          {{ edit.error }}
        </v-alert>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn class="no-drag" variant="text" @click="edit.open = false">
          取消
        </v-btn>
        <v-btn
          class="no-drag"
          color="primary"
          variant="flat"
          :loading="edit.saving"
          @click="saveEdit"
        >
          保存
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import Draggable from "vuedraggable";
import { reactive } from "vue";
import { useTftStore } from "@/stores/tft";

defineProps({
  title: { type: String, required: true },
  items: { type: Array, required: true },
  group: { type: String, default: "tiers" },
});

defineEmits(["change"]);

const tft = useTftStore();

const edit = reactive({
  open: false,
  uid: null,
  compCode: "",
  keywords: [],
  keywordInput: "",
  saving: false,
  error: "",
});

function openEdit(element) {
  edit.open = true;
  edit.error = "";
  edit.uid = element.uid;
  edit.compCode = element.code || "";
  edit.keywords = Array.isArray(element.keywords) ? [...element.keywords] : [];
  edit.keywordInput = "";
}

function normalizeKeyword(s) {
  return (s ?? "").trim();
}

function addKeyword() {
  const kw = normalizeKeyword(edit.keywordInput);
  if (!kw) return;

  // 去重（大小写不敏感）
  const exists = edit.keywords.some(
    (x) => x.toLowerCase() === kw.toLowerCase(),
  );
  if (!exists) edit.keywords.push(kw);

  edit.keywordInput = "";
}

function removeKeyword(kw) {
  edit.keywords = edit.keywords.filter((x) => x !== kw);
}

async function saveEdit() {
  edit.error = "";

  const comp_code = normalizeKeyword(edit.compCode);
  const keywords = edit.keywords.map(normalizeKeyword).filter(Boolean);

  if (!comp_code) {
    edit.error = "阵容码不能为空";
    return;
  }

  edit.saving = true;
  try {
    await tft.patchComp(edit.uid, {
      comp_code,
      keywords,
    });

    edit.open = false;
  } catch (e) {
    // 后端 UniqueConstraint 冲突等，DRF 通常会返回 {comp_code: ["..."]} 或 detail
    const data = e?.response?.data;
    edit.error =
      data?.detail ||
      data?.comp_code?.[0] ||
      data?.keywords?.[0] ||
      e?.message ||
      "保存失败";
  } finally {
    edit.saving = false;
  }
}
</script>

<style scoped>
.tier-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tier-body {
  position: relative;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px;
}

:global(.sortable-fallback) {
  z-index: 200000 !important;
}

:global(.sortable-drag) {
  z-index: 200000 !important;
}

.empty-overlay {
  position: absolute;
  inset: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  border: 1px dashed rgba(255, 255, 255, 0.25);
  border-radius: 12px;
  pointer-events: none;
}

.drop-zone {
  min-height: 100%;
  padding-bottom: 140px;
}

.comp-card {
  user-select: none;
}

/* 给 “不触发拖拽” 的控件一个明确标记 */
.no-drag {
  cursor: auto;
}

.drag-ghost {
  opacity: 0.35;
}
.drag-chosen {
  outline: 2px dashed rgba(255, 255, 255, 0.35);
}
</style>
