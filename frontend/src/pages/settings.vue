<template>
  <div class="settings-page pa-4">
    <component :is="currentSectionComponent" class="settings-page__content" />
  </div>
</template>

<script setup>
  import { computed, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import CompositionManagementSection from '@/components/tft/settings/CompositionManagementSection.vue'
  import SeasonManagementSection from '@/components/tft/settings/SeasonManagementSection.vue'
  import { normalizeSettingsSection } from '@/constants/settings'

  const route = useRoute()
  const router = useRouter()

  const sectionComponentMap = {
    comps: CompositionManagementSection,
    seasons: SeasonManagementSection,
  }

  const sectionKey = computed(() => normalizeSettingsSection(route.query.section))
  const currentSectionComponent = computed(
    () => sectionComponentMap[sectionKey.value] || CompositionManagementSection,
  )

  watch(
    () => route.query.section,
    value => {
      const normalized = normalizeSettingsSection(value)

      if (value !== normalized) {
        router.replace({
          path: '/settings',
          query: {
            ...route.query,
            section: normalized,
          },
        })
      }
    },
    { immediate: true },
  )
</script>

<style scoped>
.settings-page {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.settings-page__content {
  flex: 1;
  min-height: 0;
}

@media (max-width: 960px) {
  .settings-page {
    padding: 16px !important;
    overflow-y: auto;
  }

  .settings-page__content {
    min-height: unset;
  }
}

@media (max-width: 600px) {
  .settings-page {
    padding: 12px !important;
  }
}
</style>
