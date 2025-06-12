<script lang="ts" setup>
import { useUserStore } from '@renderer/stores'
import { InfoBoardConfig, RoomConfig } from '@renderer/types'
import { getSocket } from '@renderer/utils/socket'
import { Socket } from 'socket.io-client'
import { computed, onMounted, Ref, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
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
let socket: Socket | undefined

// 路由
let route = useRoute()

// 用户信息
const { playerName } = useUserStore()

// 属性
const eventFlipList: Ref<boolean[]> = ref([])

// 接受事件
const acceptGlobalEvent = (index: number): void => {
  setWebLoading(true)
  socket?.emit('acceptGlobalEvent', {
    roomId: roomConfig?.value.roomId,
    eventIndex: index
  })
}

// 完成事件
const finishGlobalEvent = (index: number): void => {
  setWebLoading(true)
  socket?.emit('finishGlobalEvent', {
    roomId: roomConfig?.value.roomId,
    eventIndex: index
  })
}

// 初始化
const init = (): void => {
  socket = getSocket()

  eventFlipList.value = Array.from(
    {
      length: roomConfig?.value?.globalEventList.length
    },
    () => false
  )

  const changeEventState = setTimeout(() => {
    for (let i = 0; i < eventFlipList.value.length; i++) {
      eventFlipList.value[i] = true
    }
    clearTimeout(changeEventState)
  }, 100)

  console.log('GlobalEvent', roomConfig?.value.globalEventList)
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
  <div id="globalevent">
    <h2 v-if="roomConfig?.globalEventList?.length == 0" class="event-title">
      {{ t('globalEvent.zeroEvent') }}
    </h2>
    <h2 v-else class="event-title">{{ t('globalEvent.globalEvent') }}</h2>

    <div class="event-list">
      <div
        v-for="(globalEvent, index) in roomConfig?.globalEventList"
        :key="index"
        class="event-box"
      >
        <div class="event-item" :class="{ flip: eventFlipList[index] }">
          <div class="event-card event-front">
            <div class="event-info">
              <div>
                <p class="title">{{ t(`globalEventList.${globalEvent?.itemName}.name`) }}</p>
                <p class="sub-title">{{ t(`globalEventList.${globalEvent?.itemName}.sub`) }}</p>
              </div>
              <div>
                <p class="text">{{ t(`globalEventList.${globalEvent?.itemName}.description`) }}</p>
                <hr v-if="globalEvent.idea !== 'D2RRX'" />
                <p v-if="globalEvent.idea !== 'D2RRX'">
                  {{ t('globalEvent.eventIdea') + globalEvent?.idea }}
                </p>
              </div>
              <div class="buttons">
                <!-- <button class="button confirm" @click="acceptGlobalEvent(index)">接受</button> -->
                <button
                  v-if="globalEvent.eventStatus === 'none' && roomConfig?.roomOwner === playerName"
                  class="button confirm"
                  @click="acceptGlobalEvent(index)"
                >
                  {{ t('accept') }}
                </button>
                <button
                  v-if="
                    globalEvent.eventStatus === 'active' && roomConfig?.roomOwner === playerName
                  "
                  class="button finish"
                  @click="finishGlobalEvent(index)"
                >
                  {{ t('finish') }}
                </button>
              </div>
            </div>
          </div>
          <div class="event-card event-back"></div>
        </div>
        <p class="event-name">- {{ t('globalEvent.globalEvent') }} -</p>
      </div>
    </div>

    <!-- 全局事件信息版 -->
    <InfoBoard type="left" :show-info-board="infoBoard?.gameGlobalEvent">
      <template #close-button>
        <div class="close-button">
          <a @click="infoBoard.gameGlobalEvent = !infoBoard.gameGlobalEvent">{{
            infoBoard.gameGlobalEvent ? t('close') : t('globalEvent.globalEventInfoBoardButton')
          }}</a>
        </div>
      </template>
      <template #title>
        <h1 class="title">{{ t('globalEvent.globalEventInfoBoardTitle') }}</h1>
      </template>
      <template #content>
        <div>
          <p v-for="index in 4" :key="index">
            {{ t(`globalEvent.globalEventInfoBoard.infoText0${index}`) }}
          </p>
        </div>
      </template>
    </InfoBoard>
  </div>
</template>

<style lang="scss" scoped>
@use '@renderer/assets/styles/gamepanel/globalevent';
</style>
