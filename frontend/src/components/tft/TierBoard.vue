<template>
  <div class="tier-board-root">
    <v-alert
      v-if="errorMsg"
      class="mb-4"
      density="compact"
      style="flex: 0 0 auto"
      type="error"
    >
      {{ errorMsg }}
    </v-alert>

    <v-row class="tier-board-row" dense>
      <v-col
        v-for="t in tiers"
        :key="t.level"
        class="h-100"
        cols="12"
        md="4"
      >
        <TierColumn
          group="tiers"
          :items="t.items"
          :title="t.title"
          @change="(evt) => onDrop(evt, t.level)"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
  import { onMounted, ref, watch } from 'vue'
  import { useTftStore } from '@/stores/tft'

  const tft = useTftStore()

  const loading = ref(false)
  const saving = ref(false)
  const errorMsg = ref('')

  const sList = ref([])
  const aList = ref([])
  const bList = ref([])
  const uidToPrevTier = ref(new Map())

  const tiers = [
    {
      title: 'S',
      level: 0,
      get items () {
        return sList.value
      },
    },
    {
      title: 'A',
      level: 1,
      get items () {
        return aList.value
      },
    },
    {
      title: 'B',
      level: 2,
      get items () {
        return bList.value
      },
    },
  ]

  function buildLocalListsFromStore () {
    const s = []
    const a = []
    const b = []
    const m = new Map()

    for (const c of tft.comps) {
      const tier = String(c.tierLevel)
      m.set(c.uid, tier)

      if (tier === '0') s.push(c)
      else if (tier === '1') a.push(c)
      else b.push(c)
    }

    uidToPrevTier.value = m
    sList.value = s
    aList.value = a
    bList.value = b
  }

  async function reload () {
    loading.value = true
    errorMsg.value = ''

    try {
      await tft.loadComps()
      buildLocalListsFromStore()
    } catch (error) {
      errorMsg.value = error?.response?.data?.detail || error?.message || '刷新失败'
    } finally {
      loading.value = false
    }
  }

  onMounted(async () => {
    if (tft.comps.length === 0) {
      await reload()
    } else {
      buildLocalListsFromStore()
    }
  })

  watch(
    () => tft.comps,
    () => {
      buildLocalListsFromStore()
    },
  )

  async function onDrop (evt, newTierLevel) {
    if (evt?.moved) return
    if (!evt?.added) return

    const item = evt.added.element
    if (!item?.uid) return

    const prevTier = uidToPrevTier.value.get(item.uid)
    const nextTier = String(newTierLevel)
    if (prevTier === nextTier) return

    saving.value = true
    errorMsg.value = ''

    try {
      const display = { 0: 'S', 1: 'A', 2: 'B' }[newTierLevel]
      await tft.patchComp(item.uid, {
        tier_level: newTierLevel,
        tier_display: display,
      })

      uidToPrevTier.value.set(item.uid, nextTier)
    } catch (error) {
      errorMsg.value
        = error?.response?.data?.detail || error?.message || '更新强度失败，已回滚'
      await tft.loadComps()
      buildLocalListsFromStore()
    } finally {
      saving.value = false
    }
  }

  defineExpose({
    reload,
    loading,
    saving,
    errorMsg,
  })
</script>

<style scoped>
.tier-board-root {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.tier-board-row {
  flex: 1;
  min-height: 0;
}

.h-100 {
  height: 100%;
  min-height: 0;
}
</style>
