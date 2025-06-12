import { Card } from './card'
import { ShopItem } from './shop'

export const playerLight = 2025

export enum PlayerRole {
  Null = 'null',
  Titan = 'titan',
  Hunter = 'hunter',
  Warlock = 'warlock'
}

// 玩家状态
export enum PlayerStatus {
  Idle = 'Idle',
  Draw = 'Draw'
}

export interface Role {
  role: PlayerRole
  name: string
  roleSub: string
  light: number
  roleImg: string
}

export interface PlayerInfo {
  role: PlayerRole
  playerName: string
}

export interface PlayerConfig {
  roleId: number
  role: PlayerRole
  playerName: string
  playerMoney: number
  playerStatus: PlayerStatus
  raidChest: number
  drawCount: number
  isCaptain: boolean
  zeroBuy: number
  giveUp: boolean
  specialConfig: SpecialConfig
  deckList: Array<string>
  playerAttributes: PlayerAttributes
  backpack: Array<ShopItem>
  devilspact: number
}

// 玩家属性
interface PlayerAttributes {
  gambler: boolean // 赌徒
  promotions: boolean // 促销
  profiteer: boolean // 纨绔子弟
  shopClosed: boolean // 关闭商店
  deckClosed: boolean // 关闭抽卡
  thirteen: boolean // 十三幺
  market: boolean // 未来市场
  stargazing: boolean // 观星
}

// 玩家特殊事件信息
export interface SpecialConfig {
  title: string
  description: string
  eventName: string
  eventType: string
  send: number
  to: number
  players: Array<number>
  nowPlayer: number
  deckList: Array<Card>
  playerList: Array<PlayerConfig>
  optionsList: Array<{ text: string; value: boolean | string }>
  value
}
