import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import * as tftApi from '@/api/comp'
import * as seasonApi from '@/api/season'

export const useTftStore = defineStore('tft', () => {
  const drawer = ref(true)
  const search = ref('')
  const season = ref('')
  const seasons = ref([])
  const activeSeason = ref('')
  const seasonLoading = ref(false)
  const seasonError = ref('')
  const initialized = ref(false)

  const comps = ref([])
  const currentUid = ref(null)

  const copiedKey = ref(null)
  let copiedTimer = null
  let initializePromise = null

  function mapTierName (tierLevel) {
    switch (Number(tierLevel)) {
      case 0: {
        return 'S'
      }
      case 1: {
        return 'A'
      }
      case 2: {
        return 'B'
      }
      default: {
        return String(tierLevel ?? '')
      }
    }
  }

  function mappedPayload (item) {
    return {
      uid: item.uid,
      tierLevel: String(item.tier_level),
      tierName: item.tier_display || mapTierName(item.tier_level),
      name: item.filename,
      keywords: item.keywords || [],
      code: item.comp_code,
      image: item.image_url || item.image,
      raw: item,
    }
  }

  function mapSeason (item) {
    return {
      uid: item.uid,
      version: String(item.version ?? ''),
      isActive: Boolean(item.is_active),
      createdAt: item.created_at,
      title: `赛季 ${item.version}`,
      value: String(item.version ?? ''),
      raw: item,
    }
  }

  function sortSeasons (list) {
    return list.toSorted((a, b) =>
      String(b.version).localeCompare(String(a.version), undefined, {
        numeric: true,
        sensitivity: 'base',
      }),
    )
  }

  function parseSeasonError (error, fallback) {
    return (
      error?.response?.data?.detail
      || error?.response?.data?.version?.[0]
      || error?.message
      || fallback
    )
  }

  const currentComp = computed(() => {
    return comps.value.find(c => c.uid === currentUid.value) || null
  })

  const seasonOptions = computed(() =>
    seasons.value.map(item => ({
      title: item.title,
      value: item.value,
    })),
  )

  const selectedSeasonRecord = computed(() => {
    return seasons.value.find(item => item.version === season.value) || null
  })

  const activeSeasonRecord = computed(() => {
    return seasons.value.find(item => item.version === activeSeason.value) || null
  })

  const filteredComps = computed(() => {
    const keyword = (search.value ?? '').trim().toLowerCase()

    const list = keyword
      ? comps.value.filter(
          comp =>
            (comp.name || '').toLowerCase().includes(keyword)
            || (comp.keywords || []).some(kw =>
              String(kw).toLowerCase().includes(keyword),
            ),
        )
      : comps.value

    return list.toSorted((a, b) => a.tierLevel.localeCompare(b.tierLevel))
  })

  async function loadComps () {
    if (!season.value) {
      comps.value = []
      currentUid.value = null
      return []
    }

    const list = await tftApi.listComps({ season: season.value })
    comps.value = list.map(item => mappedPayload(item))

    if (!comps.value.some(c => c.uid === currentUid.value)) {
      currentUid.value = null
    }

    return comps.value
  }

  async function loadSeasons ({ syncSelectionToActive = false } = {}) {
    seasonLoading.value = true
    seasonError.value = ''

    const [seasonListResult, currentSeasonResult] = await Promise.allSettled([
      seasonApi.listSeasons(),
      seasonApi.getCurrentSeason(),
    ])

    if (seasonListResult.status === 'fulfilled') {
      seasons.value = sortSeasons(seasonListResult.value.map(item => mapSeason(item)))
    } else {
      seasons.value = []
      seasonError.value = parseSeasonError(
        seasonListResult.reason,
        '赛季加载失败',
      )
    }

    if (currentSeasonResult.status === 'fulfilled') {
      activeSeason.value = String(currentSeasonResult.value?.version ?? '')
    } else {
      activeSeason.value = ''

      if (!seasonError.value) {
        seasonError.value = parseSeasonError(
          currentSeasonResult.reason,
          '当前没有激活赛季',
        )
      }
    }

    if (syncSelectionToActive && activeSeason.value) {
      season.value = activeSeason.value
    } else if (!season.value) {
      season.value = activeSeason.value || seasons.value[0]?.version || ''
    } else if (!seasons.value.some(item => item.version === season.value)) {
      season.value = activeSeason.value || seasons.value[0]?.version || ''
    }

    seasonLoading.value = false
    return seasons.value
  }

  async function initializeSeason () {
    if (initialized.value) {
      return loadComps()
    }

    if (!initializePromise) {
      initializePromise = (async () => {
        await loadSeasons()
        initialized.value = true
        return loadComps()
      })().finally(() => {
        initializePromise = null
      })
    }

    return initializePromise
  }

  async function changeSeason (nextSeason) {
    const normalized = String(nextSeason ?? '').trim()
    const previous = season.value

    if (!normalized || normalized === previous) {
      return comps.value
    }

    season.value = normalized

    try {
      return await loadComps()
    } catch (error) {
      season.value = previous
      throw error
    }
  }

  async function createSeason (version) {
    const normalized = String(version ?? '').trim()
    const data = await seasonApi.createSeason({ version: normalized })

    await loadSeasons()
    season.value = String(data.version ?? normalized)
    await loadComps()

    return data
  }

  async function activateSeason (version, { syncSelected = true } = {}) {
    const target = seasons.value.find(item => item.version === String(version))

    if (!target) {
      throw new Error('未找到所选赛季')
    }

    await seasonApi.setActiveSeason(target.uid)
    await loadSeasons({ syncSelectionToActive: false })

    activeSeason.value = target.version

    if (syncSelected) {
      season.value = target.version
      await loadComps()
    }

    return target
  }

  async function ensureSelectedSeasonIsActive () {
    if (!season.value) {
      throw new Error('请先选择赛季')
    }

    if (season.value === activeSeason.value) {
      return selectedSeasonRecord.value
    }

    return activateSeason(season.value, { syncSelected: false })
  }

  function selectComp (comp) {
    currentUid.value = comp.uid
  }

  async function patchComp (uid, payload) {
    const data = await tftApi.patchComp(uid, payload)

    const item = comps.value.find(c => c.uid === uid)
    if (item) {
      if (data.comp_code !== undefined) {
        item.code = data.comp_code
      }
      if (data.keywords !== undefined) {
        item.keywords = data.keywords
      }

      if (data.tier_level !== undefined) {
        item.tierLevel = String(data.tier_level)
      }
      if (data.tier_display !== undefined) {
        item.tierName = data.tier_display
      }

      if (item.raw) {
        Object.assign(item.raw, data)
      }
    }

    return data
  }

  async function deleteComp (uid) {
    await tftApi.deleteComp(uid)
    comps.value = comps.value.filter(comp => comp.uid !== uid)

    if (currentUid.value === uid) {
      currentUid.value = null
    }
  }

  async function handleCopy (code) {
    await navigator.clipboard.writeText(code)
    copiedKey.value = code

    if (copiedTimer) {
      clearTimeout(copiedTimer)
    }
    copiedTimer = setTimeout(() => {
      copiedKey.value = null
      copiedTimer = null
    }, 1500)
  }

  function tierColor (tierLevel) {
    switch (String(tierLevel)) {
      case '0': {
        return 'red'
      }
      case '1': {
        return 'orange'
      }
      case '2': {
        return 'yellow'
      }
      default: {
        return 'grey'
      }
    }
  }

  return {
    drawer,
    search,
    season,
    seasons,
    activeSeason,
    seasonLoading,
    seasonError,
    seasonOptions,
    selectedSeasonRecord,
    activeSeasonRecord,
    comps,
    currentUid,
    currentComp,
    filteredComps,
    // Backward compatible alias (can be removed later)
    filterdComps: filteredComps,
    copiedKey,
    loadSeasons,
    initializeSeason,
    changeSeason,
    createSeason,
    activateSeason,
    ensureSelectedSeasonIsActive,
    loadComps,
    patchComp,
    deleteComp,
    selectComp,
    handleCopy,
    tierColor,
  }
})
