import lolCard from '@/assets/games/lol-card.png'
import tftCard from '@/assets/games/tft-card.png'
import valCard from '@/assets/games/val-card.png'

export const GAMES = [
  {
    id: 'tft',
    name: 'Teamfight Tactics',
    displayName: '云顶之弈',
    description: '管理赛季、阵容截图、强度分级和阵容码。',
    route: '/tft',
    enabled: true,
    color: '#c8aa6e',
    art: tftCard,
  },
  {
    id: 'lol',
    name: 'League of Legends',
    displayName: '英雄联盟',
    description: '后续用于英雄出装、符文、对线笔记和策略资料。',
    route: null,
    enabled: false,
    color: '#0ac8b9',
    art: lolCard,
  },
  {
    id: 'val',
    name: 'VALORANT',
    displayName: '无畏契约',
    description: '后续用于特工点位、地图笔记、技能道具和战术资料。',
    route: null,
    enabled: false,
    color: '#ff4655',
    art: valCard,
  },
]
