export const SETTINGS_SECTIONS = [
  {
    key: 'comps',
    title: '阵容管理',
    icon: 'mdi-view-grid-outline',
  },
  {
    key: 'seasons',
    title: '赛季管理',
    icon: 'mdi-calendar-multiselect-outline',
  },
]

export function normalizeSettingsSection (value) {
  const candidate = Array.isArray(value) ? value[0] : value

  return SETTINGS_SECTIONS.some(section => section.key === candidate)
    ? candidate
    : SETTINGS_SECTIONS[0].key
}

export function getSettingsSection (value) {
  const sectionKey = normalizeSettingsSection(value)

  return (
    SETTINGS_SECTIONS.find(section => section.key === sectionKey)
    || SETTINGS_SECTIONS[0]
  )
}
