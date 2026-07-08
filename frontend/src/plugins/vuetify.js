/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Composables
import { createVuetify } from 'vuetify'
// Styles
import '@mdi/font/css/materialdesignicons.css'

import 'vuetify/styles'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: 'system',
    themes: {
      // TFT 专属主题：深蓝黑底 + 金色主色，只在 tft 布局内生效
      tft: {
        dark: true,
        colors: {
          'background': '#0a0d14',
          'surface': '#10151f',
          'surface-variant': '#1a2130',
          'primary': '#c8aa6e',
          'on-primary': '#1f1808',
          'secondary': '#0ac8b9',
          'error': '#ff4655',
          'warning': '#ffa94d',
          'success': '#3ddc97',
          'info': '#4da3ff',
        },
      },
    },
  },
})
