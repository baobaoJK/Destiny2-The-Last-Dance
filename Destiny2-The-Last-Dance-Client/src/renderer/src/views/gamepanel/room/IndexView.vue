<script lang="ts" setup>
import { useSeatPlayerList } from '@renderer/composables/useSeatPlayerList'
import { useUserStore } from '@renderer/stores'
import { RoomStatus, type Room, type RoomConfig } from '@renderer/types'
import { getSocket } from '@renderer/utils/socket'
import { storeToRefs } from 'pinia'
import type { Socket } from 'socket.io-client'
import { onMounted, ref, computed, type Ref } from 'vue'

import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 父组件信息
const props = defineProps<{
  roomConfig: RoomConfig
  roomList: Room[]
  setWebLoading: (status: boolean) => void
  resetInfo: () => void
}>()
const roomConfig: Ref<RoomConfig> = computed(() => props.roomConfig)
const roomList = computed<Room[]>(() => props.roomList)
const setWebLoading = (status: boolean): void => props.setWebLoading(status)
const resetInfo = (): void => props.resetInfo()

// 用户信息仓库
const { role, playerName, roomId } = storeToRefs(useUserStore())

// Socket
let socket: Socket | null = null

// 玩家列表信息
const { seatPlayerList } = useSeatPlayerList(roomConfig)

// 计算当前人数
const getPlayers = computed(() => {
  if (roomConfig?.value === undefined) {
    return 0
  }
  return Object.keys(roomConfig?.value.playerList).length | 0
})

// 创建房间
const createRoom = (): void => {
  setWebLoading(true)
  socket?.emit('createRoom', {
    playerInfo: {
      role: role.value,
      playerName: playerName.value
    }
  })
}

// 房间号输入框
const roomIdInput = ref('')

// 加入房间
const joinRoom = (joinRoomId: string): void => {
  setWebLoading(true)
  socket?.emit('joinRoom', {
    roomId: joinRoomId,
    playerInfo: {
      role: role.value,
      playerName: playerName.value
    }
  })
}

// 开始游戏
const startGame = (): void => {
  setWebLoading(true)
  socket?.emit('startGame', {
    roomId: roomId.value
  })
}

// 退出房间
const leaveRoom = (): void => {
  socket?.emit('leaveRoom', {
    roomId: roomId.value,
    playerName: playerName.value
  })
  resetInfo()
}

// 坐下
const sit = (i: number): void => {
  const seatIndex = i
  setWebLoading(true)
  socket?.emit('clickSeat', {
    roomId: roomId.value,
    seatIndex: seatIndex,
    playerName: playerName.value
  })
}

// 踢出房间
const kick = (name: string): void => {
  event?.stopPropagation()
  socket?.emit('kickPlayer', {
    roomId: roomId.value,
    playerName: name
  })
}

// 查看手牌
const showPlayerDeckList = (name: string): void => {
  // 禁止冒泡
  event?.stopPropagation()
  socket?.emit('getPlayerDeckList', {
    roomId: roomId.value,
    playerName: name
  })
}

// 初始化
onMounted(() => {
  socket = getSocket()
})
</script>

<template>
  <div id="room">
    <div v-if="roomId === ''" class="room-message">
      <h1>{{ t('room.roomInfo') }}</h1>
      <p>{{ t('title') }}</p>
      <p>{{ t('room.roomMessage') }}</p>
    </div>

    <div v-if="roomId === ''" class="options">
      <el-button type="primary" @click="createRoom">{{ t('room.createRoom') }}</el-button>
      <el-input
        v-model="roomIdInput"
        :placeholder="t('room.roomPlaceholder')"
        maxlength="4"
      ></el-input>
      <el-button type="primary" @click="joinRoom(roomIdInput)">{{
        t('room.joinRoomButton')
      }}</el-button>
    </div>

    <div v-if="roomId === ''" class="room-list">
      <h1>{{ t('room.roomList') }}</h1>
      <div v-for="room in roomList" :key="room.roomId" class="rooms">
        <p>
          {{ t('room.roomListInfo', { roomOwner: room.roomOwner, playerCount: room.playerCount }) }}
        </p>
        <el-button type="success" size="small" @click="joinRoom(room.roomId)">{{
          t('room.joinRoomButton')
        }}</el-button>
      </div>
    </div>

    <div v-else class="room-box">
      <div class="room-info">
        <h2>
          {{ t('room.roomBoxInfo', { roomId: roomId, playerCount: getPlayers }) }}
        </h2>
      </div>
      <div class="room-blocks">
        <div
          v-for="(player, index) in seatPlayerList"
          :key="index"
          class="room-block"
          @click="sit(index + 1)"
        >
          <div class="info-block" :class="{ 'active-block': player?.playerName }">
            <p class="number">{{ t('room.roomSeat', { seatIndex: index + 1 }) }}</p>
            <p v-if="player?.playerName !== undefined" class="name">
              {{ t('room.roomPlayer', { playerName: player?.playerName }) }}
            </p>
            <div v-if="player?.playerName" class="player-info">
              <div class="info">
                <p v-if="player?.role" class="role">
                  {{ t('room.roomRole', { playerRole: t(`roleName.${player?.role}`) }) }}
                </p>
                <p class="money">
                  {{ t('room.roomMoney', { playerMoney: player?.playerMoney }) }}
                </p>
                <p class="draw-count">
                  {{ t('room.roomDrawCount', { drawCount: player?.drawCount }) }}
                </p>
              </div>
            </div>

            <p v-if="player === null" class="sit">{{ t('room.roomSit') }}</p>
            <div
              :class="{
                back: player?.playerName,
                titan: player?.role === 'titan',
                hunter: player?.role === 'hunter',
                warlock: player?.role === 'warlock'
              }"
            ></div>
          </div>

          <div class="button-block">
            <el-button
              v-if="player?.playerName !== undefined"
              type="primary"
              class="show-button"
              @click="showPlayerDeckList(player?.playerName)"
              >{{ t('room.showDeckList') }}</el-button
            >
            <el-button
              v-if="
                roomConfig?.roomOwner === playerName &&
                player?.playerName !== playerName &&
                player?.playerName
              "
              type="danger"
              class="kick-button"
              @click="kick(player?.playerName)"
              >{{ t('room.kick') }}</el-button
            >
          </div>
        </div>
      </div>

      <div class="room-options">
        <el-button
          v-if="
            roomConfig?.roomOwner === playerName && roomConfig?.roomStatus !== RoomStatus.PLAYING
          "
          type="primary"
          size="large"
          @click="startGame"
          >{{ t('room.startGame') }}</el-button
        >
        <el-button type="primary" size="large" @click="leaveRoom">{{
          t('room.leaveRoom')
        }}</el-button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '@renderer/assets/styles/gamepanel/room/index';
</style>
