<template>
  <v-dialog v-model="open" max-width="560">
    <v-card rounded="lg">
      <v-card-title class="d-flex align-center">
        <span class="text-h6 font-weight-bold">编辑阵容</span>
        <v-spacer />
        <v-btn icon variant="text" @click="open = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-card-text>
        <v-text-field
          class="no-drag"
          label="阵容码"
          variant="outlined"
          v-model="form.compCode"
          hide-details
          :disabled="saving"
        />

        <div class="mt-4">
          <KeywordsInput
            class="no-drag"
            v-model="form.keywords"
            :disabled="saving"
          />
        </div>

        <v-alert v-if="error" type="error" density="compact" class="mt-4">
          {{ error }}
        </v-alert>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          class="no-drag"
          variant="text"
          :disabled="saving"
          @click="open = false"
        >
          取消
        </v-btn>
        <v-btn
          class="no-drag"
          color="primary"
          variant="flat"
          :loading="saving"
          @click="submit"
        >
          保存
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, reactive, watch, ref } from "vue";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  comp: { type: Object, default: null },
});

const emit = defineEmits(["update:modelValue", "save"]);

const saving = ref(false);
const error = ref("");

const open = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});

const form = reactive({
  uid: null,
  compCode: "",
  keywords: [],
});

function normalize(s) {
  return (s ?? "").trim();
}

watch(
  () => props.comp,
  (c) => {
    error.value = "";
    form.uid = c?.uid ?? null;
    form.compCode = c?.code || "";
    form.keywords = Array.isArray(c?.keywords) ? [...c.keywords] : [];
  },
  { immediate: true },
);

async function submit() {
  error.value = "";

  const comp_code = normalize(form.compCode);
  const keywords = (form.keywords || []).map(normalize).filter(Boolean);

  if (!comp_code) {
    error.value = "阵容码不能为空";
    return;
  }
  if (!form.uid) {
    error.value = "缺少 uid";
    return;
  }

  saving.value = true;
  try {
    await emit("save", { uid: form.uid, comp_code, keywords });
    open.value = false;
  } catch (e) {
    const data = e?.response?.data;
    error.value =
      typeof e === "string"
        ? e
        : data?.detail ||
          data?.comp_code?.[0] ||
          data?.keywords?.[0] ||
          e?.message ||
          "保存失败";
  } finally {
    saving.value = false;
  }
}
</script>
