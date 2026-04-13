import { http } from './axios'

export async function listSeasons () {
  const res = await http.get('/seasons/')
  const data = res.data
  return Array.isArray(data) ? data : (data?.results ?? [])
}

export async function createSeason (payload) {
  const res = await http.post('/seasons/', payload)
  return res.data
}

export async function getCurrentSeason () {
  const res = await http.get('/seasons/current/')
  return res.data
}

export async function setActiveSeason (uid) {
  const res = await http.post(`/seasons/${uid}/set_active/`)
  return res.data
}
