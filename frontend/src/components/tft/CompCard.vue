<template>
  <v-card
    class="mb-2 comp-card"
    rounded="lg"
    :style="cardStyle"
    variant="flat"
  >
    <v-card-title class="comp-card__title d-flex align-center py-2">
      <v-chip
        class="comp-card__tier font-weight-bold flex-shrink-0"
        :color="tierColor"
        size="small"
        variant="tonal"
      >
        {{ comp.tierName }}
      </v-chip>

      <span class="text-subtitle-2 font-weight-bold text-truncate ml-2">
        {{ displayName }}
      </span>

      <v-spacer />

      <v-btn
        class="no-drag comp-card__action"
        color="warning"
        icon
        size="x-small"
        variant="text"
        @click.stop="$emit('edit', comp)"
      >
        <v-icon size="18">mdi-pencil</v-icon>
      </v-btn>

      <v-btn
        class="no-drag comp-card__action"
        color="error"
        icon
        size="x-small"
        variant="text"
        @click.stop="$emit('delete', comp)"
      >
        <v-icon size="18">mdi-delete</v-icon>
      </v-btn>
    </v-card-title>

    <v-card-subtitle class="comp-card__code text-caption pb-2">
      {{ comp.code }}
    </v-card-subtitle>

    <div v-if="(comp.keywords || []).length > 0" class="px-3 pb-3">
      <v-chip
        v-for="kw in comp.keywords.slice(0, 6)"
        :key="kw"
        class="mr-1 mb-1 comp-card__keyword"
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

  defineEmits(['edit', 'delete'])

  const TIER_COLORS = {
    0: '#ff4655',
    1: '#ffa94d',
    2: '#ffd43b',
  }

  const displayName = computed(() => (props.comp?.name || '').split('.')[0])
  const tierColor = computed(
    () => TIER_COLORS[Number(props.comp?.tierLevel)] || '#9aa4b2',
  )
  const cardStyle = computed(() => ({
    '--tier-color': tierColor.value,
  }))
</script>

<style scoped>
.comp-card {
  position: relative;
  user-select: none;
  overflow: hidden;
  background: rgba(20, 26, 38, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.07);
  cursor: grab;
  transition: border-color 0.2s ease, background 0.2s ease;
}

/* Tier-colored accent strip */
.comp-card::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: var(--tier-color);
  opacity: 0.85;
}

.comp-card:hover {
  border-color: rgba(255, 255, 255, 0.16);
  background: rgba(26, 33, 48, 0.9);
}

.comp-card__title {
  min-height: 0;
}

.comp-card__code {
  opacity: 0.55;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  letter-spacing: 0.02em;
}

.comp-card__keyword {
  opacity: 0.75;
}

.comp-card__action {
  opacity: 0.4;
  transition: opacity 0.2s ease;
}

.comp-card:hover .comp-card__action {
  opacity: 1;
}
</style>
