<template>
  <v-dialog v-model="open" max-width="640">
    <v-card rounded="lg">
      <v-card-title class="d-flex align-center">
        <span class="text-h6 font-weight-bold">上传阵容图片</span>
        <v-spacer />
        <v-btn icon variant="text" @click="open = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-card-text>
        <v-file-input
          v-model="form.file"
          accept="image/*"
          label="选择图片"
          variant="outlined"
          prepend-inner-icon="mdi-image"
          prepend-icon=""
          show-size
          :disabled="saving"
        />

        <v-text-field
          v-model="form.compCode"
          label="阵容码"
          variant="outlined"
          class="mt-3"
          :disabled="saving"
        />

        <v-select
          v-model="form.tierName"
          :items="['S', 'A', 'B']"
          label="强度"
          variant="outlined"
          class="mt-3"
          :disabled="saving"
        />

        <div class="mt-4">
          <KeywordsInput v-model="form.keywords" :disabled="saving" />
        </div>

        <v-alert v-if="error" type="error" density="compact" class="mt-4">
          {{ error }}
        </v-alert>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" :disabled="saving" @click="open = false">
          取消
        </v-btn>
        <v-btn color="primary" variant="flat" :loading="saving" @click="submit">
          上传
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, reactive, watch, ref } from "vue";
import * as compApi from "@/api/comp";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue", "uploaded"]);

const open = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});

const saving = ref(false);
const error = ref("");

const form = reactive({
  file: null,
  compCode: "",
  tierName: "A",
  keywords: [],
});

function normalize(s) {
  return (s ?? "").trim();
}

function tierToLevel(tierName) {
  return tierName === "S" ? 0 : tierName === "A" ? 1 : 2;
}

watch(
  () => open.value,
  (v) => {
    if (!v) return;
    error.value = "";
    form.file = null;
    form.compCode = "";
    form.tierName = "A";
    form.keywords = [];
  },
);

async function submit() {
  error.value = "";

  const file = form.file;
  const comp_code = normalize(form.compCode);
  if (!file) {
    error.value = "请选择图片";
    return;
  }
  if (!comp_code) {
    error.value = "阵容码不能为空";
    return;
  }

  const tier_level = tierToLevel(form.tierName);
  const tier_display = form.tierName;
  const keywords = (form.keywords || []).map(normalize).filter(Boolean);

  saving.value = true;
  try {
    await compApi.uploadComp({
      file,
      comp_code,
      tier_level,
      tier_display,
      keywords,
    });

    open.value = false;
    emit("uploaded");
  } catch (e) {
    const data = e?.response?.data;
    error.value =
      data?.detail ||
      data?.comp_code?.[0] ||
      data?.image?.[0] ||
      data?.keywords?.[0] ||
      e?.message ||
      "上传失败";
  } finally {
    saving.value = false;
  }
}
</script>
