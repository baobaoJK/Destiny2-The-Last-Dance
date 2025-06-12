import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PlayerInfo } from '@renderer/types'

export const useUserStore = defineStore(
  'user',
  () => {
    // 房间id
    const roomId = ref('')
    // 角色
    const role = ref('')
    // 角色 Id
    const roleId = ref(0)
    // 用户名
    const playerName = ref('')

    // 初始化信息
    const initInfo = async (playerInfo: PlayerInfo): Promise<void> => {
      roomId.value = ''
      role.value = playerInfo.role
      playerName.value = playerInfo.playerName
    }

    // 设置房间号
    const setRoomId = (newRoomId: string): void => {
      roomId.value = newRoomId
    }

    return {
      roomId,
      roleId,
      role,
      playerName,
      initInfo,
      setRoomId
    }
  },
  {
    persist: true
  }
)
