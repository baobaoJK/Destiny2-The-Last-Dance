<script lang="ts" setup>
import { defineProps, computed, ref, onMounted, type Ref } from 'vue'
import type { InfoBoardConfig, RaidConfig, RoomConfig } from '@renderer/types'
import { Socket } from 'socket.io-client'
import { getSocket } from '@renderer/utils/socket'
import { SocketData } from '@renderer/types/socket'
import { getRaidMapImg } from '@renderer/utils'
import { useI18n } from 'vue-i18n'
import InfoBoard from '@renderer/components/infoboard/IndexView.vue'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@renderer/stores'

// 用户仓库
const { playerName } = storeToRefs(useUserStore())

// i18n
const { t } = useI18n()

// 地图加载事件
const rollMapTime = ref(16000) // 16000

// Socket
let socket: Socket | null

// 父组件信息
const props = defineProps<{
  roomConfig: RoomConfig
  infoBoard: InfoBoardConfig
  setWebLoading: (status: boolean) => void
}>()

// 房间信息
const roomConfig = computed(() => props.roomConfig)
const infoBoard = computed((): InfoBoardConfig => props.infoBoard)
// const setWebLoading = (status: boolean): void => props.setWebLoading(status)

// 网页元素
const mapListRef = ref<HTMLStyleElement>()
const mapNameRef = ref<HTMLStyleElement>()
const buttonDisabled = ref(false)
const opacityValue = ref(0)
const mapList: Ref<RaidConfig[]> = ref([])
const defaultMapName = ref('请选择地图')

// 抽取地图事件
const rollMap = (): void => {
  socket?.emit('rollMap', {
    roomId: roomConfig?.value?.roomId,
    rollTime: rollMapTime.value / 1000
  })
}

// 初始化
onMounted(() => {
  socket = getSocket()

  socket?.off('rollMap')
  socket?.on('rollMap', (socketData: SocketData): void => {
    buttonDisabled.value = true
    mapList.value = []
    opacityValue.value = 0
    if (mapListRef.value) {
      mapListRef.value.style.transform = ''
      mapListRef.value.style.transition = 'none'
    }
    if (mapNameRef.value) {
      mapNameRef.value.innerHTML = ''
    }

    if (socketData.eventType === 'rollMap') {
      console.log(socketData)
      mapList.value = socketData.data.mapList

      // 设置动画
      requestAnimationFrame(() => {
        if (mapListRef.value) {
          mapListRef.value.style.transition = `all ${rollMapTime.value / 1000 - 1}s cubic-bezier(0.35, 0, 0.01, 1)`
          mapListRef.value.style.transform = 'translateX(-2507.875rem)'
        }
      })

      // 抽取地图
      const rollMapTimeout = setTimeout(() => {
        if (mapNameRef.value) {
          opacityValue.value = 1

          // 获取地图
          const map = mapList.value[43]
          defaultMapName.value = map.raidName
          mapNameRef.value.innerHTML = t('map.mapName.' + map.raidName)
          buttonDisabled.value = false

          clearTimeout(rollMapTimeout)
        }
      }, rollMapTime.value)
    }
  })

  if (roomConfig?.value?.raidConfig) {
    defaultMapName.value = roomConfig.value.raidConfig.raidName
    if (mapNameRef.value) {
      mapNameRef.value.innerHTML = t('map.mapName.' + roomConfig.value.raidConfig.raidName)
    }
    opacityValue.value = 1
  }
})
</script>

<template>
  <div id="map">
    <h1 class="map-title">{{ t('map.title') }}</h1>
    <div class="map-roll-list">
      <div ref="mapListRef" class="map-list">
        <div class="map-img">
          <img :src="getRaidMapImg(defaultMapName)" :alt="defaultMapName + '.jpg'" />
        </div>
        <div v-for="(map, index) in mapList" :key="index" class="map-img">
          <img :src="getRaidMapImg(map.raidName)" :alt="map.raidName + '.jpg'" />
        </div>
      </div>
    </div>
    <div class="map-text">
      <h1 ref="mapNameRef" :style="{ opacity: opacityValue, transition: 'opacity 1s' }"></h1>
    </div>
    <button
      v-if="roomConfig?.roomOwner == playerName"
      :disabled="buttonDisabled"
      class="button"
      @click="rollMap()"
    >
      {{ t('map.rollMap') }}
    </button>

    <!-- 地图信息版 -->
    <InfoBoard type="left" :show-info-board="infoBoard.gameMap">
      <template #close-button>
        <div class="close-button">
          <a @click="infoBoard.gameMap = !infoBoard.gameMap">{{
            infoBoard.gameMap ? t('close') : t('map.infoBoardButton')
          }}</a>
        </div>
      </template>
      <template #title>
        <h1 class="title">{{ t('map.infoBoard.titleText01') }}</h1>
      </template>
      <template #content>
        <div>
          <h2>{{ t('map.infoBoard.titleText02') }}</h2>
          <p>
            {{ t('map.infoBoard.infoText01') }}
          </p>
        </div>
      </template>
    </InfoBoard>
  </div>
</template>

<style lang="scss" scoped>
@use '@renderer/assets/styles/gamepanel/map/index';
</style>
