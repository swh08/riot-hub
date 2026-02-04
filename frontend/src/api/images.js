import { http } from "./axios";

export async function fetchImages({ season } = {}) {
  const params = {};
  if (season) params.season = season;

  const res = await http.get("/api/images/", { params });
  return res.data;
}

export async function uploadImage(file, payload = {}) {
  const form = new FormData();
  form.append("image", file);

  Object.entries(payload).forEach(([k, v]) => {
    if (Array.isArray(v)) {
      // DRF 常见写法：数组用多次 append
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
