<script lang="ts" setup>
import { defineProps, computed, Ref, onMounted, ref, watch } from 'vue'
import { RoomConfig } from '@renderer/types/room'
import { getSocket } from '@renderer/utils/socket'
import { Socket } from 'socket.io-client'
import { useUserStore } from '@renderer/stores'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { InfoBoardConfig } from '@renderer/types'
import InfoBoard from '@renderer/components/infoboard/IndexView.vue'

// 父组件信息
const props = defineProps<{
  roomConfig: RoomConfig
  infoBoard: InfoBoardConfig
  setWebLoading: (status: boolean) => void
}>()
const roomConfig: Ref<RoomConfig> = computed(() => props.roomConfig)
const infoBoard = computed(() => props.infoBoard)
const setWebLoading = (status: boolean): void => props.setWebLoading(status)

// i18n
const { t } = useI18n()

// socket
let socket: Socket | null

// 路由
let route = useRoute()

// 用户仓库
const { playerName } = storeToRefs(useUserStore())
// 属性
const eventFlipList: Ref<boolean[]> = ref([])

// 接受事件
const acceptPlayerEvent = (index: number): void => {
  setWebLoading(true)
  socket?.emit('acceptPlayerEvent', {
    roomId: roomConfig?.value?.roomId,
    playerName: playerName.value,
    eventIndex: index
  })
}

// 完成事件
const finishEvent = (index: number): void => {
  setWebLoading(true)
  socket?.emit('finishPlayerEvent', {
    roomId: roomConfig?.value?.roomId,
    playerName: playerName.value,
    eventIndex: index
  })
}

// 放弃事件
const dropEvent = (index: number): void => {
  setWebLoading(true)
  socket?.emit('dropPlayerEvent', {
    roomId: roomConfig?.value?.roomId,
    playerName: playerName.value,
    eventIndex: index
  })
}

const init = (): void => {
  socket = getSocket()

  eventFlipList.value = Array.from(
    {
      length: roomConfig?.value?.playerList[playerName.value]?.playerEventList?.length
    },
    () => false
  )

  const changeEventState = setTimeout(() => {
    for (let i = 0; i < eventFlipList.value.length; i++) {
      eventFlipList.value[i] = true
    }
    clearTimeout(changeEventState)
  }, 100)
}

onMounted(() => {
  init()
})

watch(
  () => [route.params.page],
  () => {
    init()
  }
)
</script>

<template>
  <div id="playerevent">
    <h2 v-if="roomConfig?.playerList[playerName]?.playerEventList?.length == 0" class="event-title">
      {{ t('playerEvent.zeroEvent') }}
    </h2>
    <h2 v-else class="event-title">{{ t('playerEvent.playerEvent') }}</h2>

    <div class="event-list">
      <div
        v-for="(playerEvent, index) in roomConfig?.playerList[playerName]?.playerEventList"
        :key="index"
        class="event-box"
      >
        <div class="event-item" :class="{ flip: eventFlipList[index] }">
          <div class="event-card event-front">
            <div class="event-info">
              <div>
                <p class="title">{{ t(`playerEventList.${playerEvent.itemName}.name`) }}</p>
                <p class="sub-title">{{ t(`playerEventList.${playerEvent.itemName}.sub`) }}</p>
              </div>
              <div>
                <p class="text">
                  {{ t(`playerEventList.${playerEvent.itemName}.description`) }}
                </p>
                <hr v-if="playerEvent.idea !== 'D2RRX'" />
                <p v-if="playerEvent.idea !== 'D2RRX'">
                  {{ t('playerEvent.eventIdea') + playerEvent.idea }}
                </p>
              </div>
              <div class="buttons">
                <!-- <button class="button confirm" @click="acceptPlayerEvent(index)">接受</button> -->
                <button
                  v-if="playerEvent.eventStatus === 'none'"
                  class="button confirm"
                  @click="acceptPlayerEvent(index)"
                >
                  {{ t('accept') }}
                </button>
                <button v-else class="button finish" @click="finishEvent(index)">
                  {{ t('finish') }}
                </button>
              </div>
            </div>
          </div>
          <div class="event-card event-back"></div>
        </div>
        <button
          v-if="playerEvent.eventStatus === 'none'"
          class="button quit"
          @click="dropEvent(index)"
        >
          {{ t('giveUp') }}
        </button>
        <p class="event-name">- {{ t('playerEvent.playerEvent') }} -</p>
      </div>
    </div>

    <!-- 个人事件信息版 -->
    <InfoBoard type="left" :show-info-board="infoBoard.gamePlayerEvent">
      <template #close-button>
        <div class="close-button">
          <a @click="infoBoard.gamePlayerEvent = !infoBoard.gamePlayerEvent">{{
            infoBoard.gamePlayerEvent ? t('close') : t('playerEvent.playerEventInfoBoardButton')
          }}</a>
        </div>
      </template>
      <template #title>
        <h1 class="title">{{ t('playerEvent.playerEventInfoBoardTitle') }}</h1>
      </template>
      <template #content>
        <div>
          <p v-for="item in 5" :key="item">
            {{ t(`playerEvent.playerEventInfoBoard.infoText0${item}`) }}
          </p>
        </div>
      </template>
    </InfoBoard>
  </div>
</template>

<style lang="scss" scoped>
@use '@renderer/assets/styles/gamepanel/playerevent/index';
</style>
