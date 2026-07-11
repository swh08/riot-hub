import { http } from './axios'

export async function listSeasons () {
  const res = await http.get('/tft/seasons/')
  const data = res.data
  return Array.isArray(data) ? data : (data?.results ?? [])
}

export async function createSeason (payload) {
  const res = await http.post('/tft/seasons/', payload)
  return res.data
}

export async function getCurrentSeason () {
  const res = await http.get('/tft/seasons/current/')
  return res.data
}

export async function setActiveSeason (uid) {
  const res = await http.post(`/tft/seasons/${uid}/set_active/`)
  return res.data
}

export async function uploadSeasonBackground (uid, file) {
  const formData = new FormData()
  formData.append('background', file)

  const res = await http.post(`/tft/seasons/${uid}/background/`, formData)
  return res.data
}

export async function deleteSeasonBackground (uid) {
  const res = await http.delete(`/tft/seasons/${uid}/background/`)
  return res.data
}

export async function importSeasonCompositions (uid) {
  const res = await http.post(`/tft/seasons/${uid}/import-compositions/`)
  return res.data
}
