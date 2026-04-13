<template>
  <v-card class="mb-2 comp-card" rounded="lg" variant="tonal">
    <v-card-title class="d-flex align-center">
      <div class="text-subtitle-1 font-weight-bold text-truncate">
        <v-chip>
          {{ comp.tierName }}
        </v-chip>
        {{ displayName }}
      </div>

      <v-spacer />

      <v-btn
        class="no-drag"
        color="warning"
        icon
        size="small"
        variant="text"
        @click.stop="$emit('edit', comp)"
      >
        <v-icon>mdi-pencil</v-icon>
      </v-btn>
    </v-card-title>

    <v-card-subtitle class="text-caption mb-2">
      {{ comp.code }}
    </v-card-subtitle>

    <div v-if="(comp.keywords || []).length > 0" class="px-4 pb-3">
      <v-chip
        v-for="kw in comp.keywords.slice(0, 6)"
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

<script setup>
  import { computed } from 'vue'

  const props = defineProps({
    comp: { type: Object, required: true },
  })

  defineEmits(['edit'])

  const displayName = computed(() => (props.comp?.name || '').split('.')[0])
</script>

<style scoped>
.comp-card {
  user-select: none;
}
</style>
