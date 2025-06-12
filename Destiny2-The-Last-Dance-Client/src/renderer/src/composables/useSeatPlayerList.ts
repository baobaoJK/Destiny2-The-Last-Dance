// composables/useSeatPlayerList.ts
import { computed } from 'vue'
import type { Ref } from 'vue'
import type { RoomConfig, PlayerConfig } from '@renderer/types'

export const useSeatPlayerList = (
  roomConfig: Ref<RoomConfig | null>
): {
  playerListKeys: Ref<string[]>
  findPlayerBySeat: (seatNumber: number) => PlayerConfig | null
  seatPlayerList: Ref<(PlayerConfig | null)[]>
} => {
  // 玩家列表 key
  const playerListKeys = computed(() => Object.keys(roomConfig.value?.playerList || {}))

  // 根据座位号查找玩家
  const findPlayerBySeat = (seatNumber: number): PlayerConfig | null => {
    const keys = playerListKeys.value
    for (const key of keys) {
      const player = roomConfig.value?.playerList[key]
      if (player?.roleId === seatNumber) {
        return player
      }
    }
    return null
  }

  // 生成座位对应玩家列表
  const seatPlayerList = computed(() => {
    const seats: (PlayerConfig | null)[] = []
    for (let i = 1; i <= 6; i++) {
      seats.push(findPlayerBySeat(i))
    }
    return seats
  })

  return {
    playerListKeys,
    findPlayerBySeat,
    seatPlayerList
  }
}
