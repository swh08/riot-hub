import { defineStore } from "pinia";
import { ref, computed, watch } from "vue";
import { http } from "@/api/axios";

export const useTftStore = defineStore("tft", () => {
  const drawer = ref(true);
  const search = ref("");
  const season = ref("");

  const comps = ref([]);
  const currentUid = ref(null);

  const copiedKey = ref(null);
  let copiedTimer = null;

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

  const currentComp = computed(() => {
    return comps.value.find((c) => c.uid === currentUid.value) || null;
  });

  const filterdComps = computed(() => {
    const keyword = (search.value ?? "").trim().toLowerCase();

    const list = keyword
      ? comps.value.filter(
          (comp) =>
            (comp.name || "").toLowerCase().includes(keyword) ||
            (comp.keywords || []).some((kw) =>
              String(kw).toLowerCase().includes(keyword),
            ),
        )
      : comps.value;

    return [...list].sort((a, b) => a.tierLevel.localeCompare(b.tierLevel));
  });

  async function loadComps() {
    const params = {};
    if (season.value) params.season = season.value;

    const res = await http.get("/api/images/", { params });
    const list = Array.isArray(res.data) ? res.data : (res.data.results ?? []);

    comps.value = list.map(mappedPayload);
  }

  function selectComp(comp) {
    currentUid.value = comp.uid;
  }

  async function handleCopy(code) {
    await navigator.clipboard.writeText(code);
    copiedKey.value = code;

    if (copiedTimer) clearTimeout(copiedTimer);
    copiedTimer = setTimeout(() => {
      copiedKey.value = null;
      copiedTimer = null;
    }, 1500);
  }

  function tierColor(tierLevel) {
    switch (String(tierLevel)) {
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

  watch(season, () => {
    loadComps();
  });

  return {
    drawer,
    search,
    season,
    comps,
    currentUid,
    currentComp,
    filterdComps,
    copiedKey,
    loadComps,
    selectComp,
    handleCopy,
    tierColor,
  };
});
