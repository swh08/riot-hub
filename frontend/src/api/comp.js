import { http } from "./axios";

/**
 * Backend calls for TFT comps (images).
 * Keep raw HTTP details in this API layer.
 */

// --- Preferred API (new) ---

export async function listComps({ season } = {}) {
  const params = {};
  if (season) params.season = season;

  const res = await http.get("/api/images/", { params });
  const data = res.data;
  return Array.isArray(data) ? data : data?.results ?? [];
}

export async function patchComp(uid, payload) {
  const res = await http.patch(`/api/images/${uid}/`, payload);
  return res.data;
}

export async function uploadComp({ file, comp_code, tier_level, tier_display, keywords = [] }) {
  const fd = new FormData();
  fd.append("image", file);
  fd.append("comp_code", comp_code);
  fd.append("tier_level", String(tier_level));
  fd.append("tier_display", tier_display);
  for (const kw of keywords) fd.append("keywords", kw);

  const res = await http.post("/api/images/", fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

// --- Legacy exports (kept for compatibility) ---

export async function fetchImages({ season } = {}) {
  return listComps({ season });
}

export async function uploadImage(file, payload = {}) {
  // If caller already uses { file, ... } prefer uploadComp instead.
  const form = new FormData();
  form.append("image", file);

  Object.entries(payload).forEach(([k, v]) => {
    if (Array.isArray(v)) {
      v.forEach((item) => form.append(k, item));
    } else if (v !== undefined && v !== null) {
      form.append(k, v);
    }
  });

  const res = await http.post("/api/images/", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}
