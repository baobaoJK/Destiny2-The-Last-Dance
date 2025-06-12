import { type PlayerConfig } from './player'
import { type RaidConfig } from './raid'
import { ShopItem } from './shop'

// 房间阶段状态
export enum RoomStage {
  NEXT = 'NEXT',
  DOOR = 'DOOR'
}

// 房间状态
export enum RoomStatus {
  WAITING = 'WATING',
  PLAYING = 'PLAYING'
}

// 房间配置信息
export interface RoomConfig {
  roomId: string
  roomOwner: string
  roomStage: RoomStage
  roomStatus: RoomStatus
  drawCardPlayer: string | null
  randomSeats: boolean
  playerList: Array<PlayerConfig>
  globalEventList: Array<GlobalEvent>
  raidConfig: RaidConfig
  shopConfig: ShopConfig
  cardCountList
}

// 房间信息
export interface Room {
  roomId: string
  roomOwner: string
  playerName: string
  playerCount: number
}

// 全局事件
export interface GlobalEvent {
  eventId: string
  eventType: string
  itemName: string
  eventName: string
  eventDescription: string
  eventStatus: string
  idea: string
}

// 商店
export interface ShopConfig {
  refreshCount: number
  refreshMoney: number
  itemList: Array<ShopItem>
  weaponList: Array<ShopItem>
  exoticList: Array<ShopItem>
}

// 默认配置
export const createDefaultRoomConfig = (): RoomConfig => ({
  roomId: '',
  roomOwner: '',
  playerList: []
})
