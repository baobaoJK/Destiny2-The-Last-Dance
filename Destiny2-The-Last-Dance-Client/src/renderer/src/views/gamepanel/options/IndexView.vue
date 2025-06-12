<script lang="ts" setup>
import { useUserStore } from '@renderer/stores'
import { InfoBoardConfig, PlayerRole, RaidConfig, RoomConfig, RoomStage } from '@renderer/types'
import { SocketData } from '@renderer/types/socket'
import { getSocket } from '@renderer/utils/socket'
import { storeToRefs } from 'pinia'
import { Socket } from 'socket.io-client'
import { defineProps, computed, Ref, ref, onMounted } from 'vue'
import { getRaidMapImg } from '@renderer/utils'
import { ElMessage } from 'element-plus'
import { useSeatPlayerList } from '@renderer/composables/useSeatPlayerList'
import { useI18n } from 'vue-i18n'
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

// 用户信息仓库
const { playerName } = storeToRefs(useUserStore())

// 地图列表
const mapList: Ref<RaidConfig[]> = ref([])

// 提示框
const mapDialogVisible = ref(false)

// 地图名称
const mapName = computed(() => {
  if (!roomConfig?.value) {
    return '请选择地图'
  }

  return roomConfig?.value?.raidConfig?.raidName
})

// 打开选择地图模态框
const openMapDialog = (): void => {
  // 判断是否为队长
  if (roomConfig?.value?.roomOwner !== playerName.value) return
  mapDialogVisible.value = true
  setWebLoading(true)
  socket?.emit('getMapList', {
    roomId: roomConfig?.value?.roomId
  })
}

// 选择地图
const setMapById = (mapId: string): void => {
  setWebLoading(true)
  socket?.emit('setMap', {
    roomId: roomConfig?.value?.roomId,
    mapId: mapId
  })

  mapDialogVisible.value = false
}

// 地图步骤条
// -----------------------------------------------------
// 步骤
const mapSteps = computed(() => {
  if (!roomConfig?.value?.raidConfig) {
    return 1
  }

  return roomConfig.value.raidConfig.raidLevel
})
// 步骤数
const mapStepNum = computed(() => {
  if (!roomConfig?.value?.raidConfig) {
    return 1
  }

  return roomConfig.value.raidConfig.raidLevelPoint + 1
})
// 步骤条每一步长度
const mapStepWidth = computed(() => {
  if (!roomConfig?.value?.raidConfig) {
    return 0
  }

  return 100 / Number(mapSteps.value)
})

// 检测地图
const checkRaidMap = (): boolean => {
  // 判断突袭地图是否为空
  if (!roomConfig?.value?.raidConfig) {
    ElMessage({
      message: t('options.message.warningText09'),
      grouping: true,
      type: 'error'
    })

    return true
  }
  return false
}

// 遭遇战插旗点
const mapDoorButtonDisabled = computed(() => {
  return roomConfig?.value?.roomStage === RoomStage.NEXT ? true : false
  //   return roomConfig?.value?.roomStage === 'next' ? false : false
})
const mapDoor = (): void => {
  // 检测地图是否为空
  if (checkRaidMap()) return

  setWebLoading(true)
  socket?.emit('mapDoor', {
    roomId: roomConfig.value.roomId
  })
}

// 遭遇战完成按钮
const mapNextButtonDisabled = computed(() => {
  return roomConfig?.value?.roomStage === RoomStage.DOOR ? true : false
  //   return roomConfig?.value?.roomStage === 'door' ? false : false
})
const mapNext = (): void => {
  // 判断突袭地图是否非空
  if (checkRaidMap()) return

  setWebLoading(true)
  socket?.emit('mapNext', {
    roomId: roomConfig.value.roomId
  })
}

// 隐藏箱进度条
// -----------------------------------------------------
// 步骤
const chestSteps = computed(() => {
  if (!roomConfig?.value?.raidConfig) {
    return 1
  }

  return roomConfig.value.raidConfig.raidChest
})
// 步骤数
const chestStepNum = computed(() => {
  if (!roomConfig?.value?.raidConfig) {
    return 1
  }

  return roomConfig?.value?.playerList[playerName.value].raidChest + 1
})
// 步骤条每一步长度
const chestStepWidth = computed(() => {
  if (!roomConfig?.value?.raidConfig) {
    return 0
  }

  return 100 / Number(chestSteps.value)
})

// 获取隐藏箱事件
const chestNextButtonDisabled = ref(false)
const nextChest = (): void => {
  // 判断突袭地图是否为空
  if (checkRaidMap()) return

  setWebLoading(true)
  socket?.emit('getChest', {
    roomId: roomConfig.value.roomId,
    playerName: playerName.value
  })

  chestNextButtonDisabled.value = true
  const changeButtonState = setTimeout(() => {
    chestNextButtonDisabled.value = false
    clearInterval(changeButtonState)
  }, 3000)
}

// 无暇按钮
const flawlessButtonDisabled = ref(false)
const flawlessButton = (): void => {
  // 判断突袭地图是否为空
  if (checkRaidMap()) return

  setWebLoading(true)
  socket?.emit('flawless', {
    roomId: roomConfig.value.roomId
  })

  // 更改按钮状态
  flawlessButtonDisabled.value = true
  const changeButtonState = setTimeout(() => {
    flawlessButtonDisabled.value = false
    clearInterval(changeButtonState)
  }, 3000)
}

// 玩家抽卡货币设置模态框
const playerSettingDialogVisible = ref(false)
const showPlayerSettingDialog = (): void => {
  playerSettingDialogVisible.value = true
}
const { seatPlayerList } = useSeatPlayerList(roomConfig)
const handleChange = (
  changeType: string,
  changePlayerName: string | undefined,
  value: number
): void => {
  setWebLoading(true)
  socket?.emit('playerSetting', {
    roomId: roomConfig?.value.roomId,
    playerName: changePlayerName,
    settingType: changeType,
    settingCount: value
  })
}

// 净化按钮
const purifyButtonDisabled = ref(false)
const purifyButton = (): void => {
  // 判断突袭地图是否为空
  if (checkRaidMap()) return

  setWebLoading(true)
  socket?.emit('purify', {
    roomId: roomConfig.value.roomId
  })

  // 更改按钮状态
  purifyButtonDisabled.value = true
  const changeButtonState = setTimeout(() => {
    purifyButtonDisabled.value = false
    clearInterval(changeButtonState)
  }, 3000)
}

// 初始化
onMounted(() => {
  socket = getSocket()

  socket?.off('getMapList')
  socket?.on('getMapList', (socketData: SocketData) => {
    console.log(socketData)
    mapList.value = socketData.data.mapList
    setWebLoading(false)
  })
})
</script>
<template>
  <div id="options">
    <div class="map-pane">
      <div class="map-info">
        <div class="map-img" @click="openMapDialog">
          <img :src="getRaidMapImg(mapName)" alt="地图" />
        </div>
        <p class="map-text">- {{ t(`map.mapName.${mapName}`) }} -</p>
        <button
          v-if="roomConfig?.roomOwner === playerName"
          class="button map-button"
          @click="openMapDialog"
        >
          {{ t('options.selectMap') }}
        </button>
      </div>

      <div class="map-level-box">
        <p>-{{ t('options.mapLevelText') }}-</p>
        <div class="map-step-bar">
          <div class="map-bar" :style="{ width: (mapStepNum - 1) * mapStepWidth + '%' }"></div>
          <div
            v-for="index in mapSteps + 1"
            :key="index"
            :class="{ active: mapStepNum >= index }"
            class="step map-step"
          >
            {{ index - 1 }}
          </div>
        </div>
        <div v-if="roomConfig?.roomOwner === playerName" class="step-options map-options">
          <button id="map-door" :disabled="mapDoorButtonDisabled" class="button" @click="mapDoor">
            {{ t('options.mapDoor') }}
          </button>
          <button id="map-next" :disabled="mapNextButtonDisabled" class="button" @click="mapNext">
            {{ t('options.mapNext') }}
          </button>
        </div>
      </div>

      <div class="map-chest-box">
        <p>-{{ t('options.mapChestText') }}-</p>
        <div class="chest-step-bar">
          <div
            class="chest-bar"
            :style="{ width: (chestStepNum - 1) * chestStepWidth + '%' }"
          ></div>
          <div
            v-for="index in chestSteps + 1"
            :key="index"
            :class="{ active: chestStepNum >= index }"
            class="step map-step"
          >
            {{ index - 1 }}
          </div>
        </div>
        <div class="step-options chest-options">
          <button
            id="chest-next"
            class="button"
            :disabled="chestNextButtonDisabled"
            @click="nextChest"
          >
            {{ t('options.mapGetChest') }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="roomConfig?.roomOwner === playerName" class="options-pane">
      <button id="player-setting-button" class="button" @click="showPlayerSettingDialog">
        {{ t('options.optionButtonText01') }}
      </button>
      <button
        id="flawless"
        class="button"
        :disabled="flawlessButtonDisabled"
        @click="flawlessButton"
      >
        {{ t('options.optionButtonText02') }}
      </button>
      <button id="purify" class="button" :disabled="purifyButtonDisabled" @click="purifyButton">
        {{ t('options.optionButtonText03') }}
      </button>
    </div>

    <!-- 地图选择模态框 -->
    <el-dialog
      v-model="mapDialogVisible"
      class="dialog map-dialog"
      :close-on-click-modal="false"
      width="90rem"
      align-center
    >
      <div class="map-title">
        <h1>{{ t('options.mapTitle') }}</h1>
      </div>

      <div class="map-list-box">
        <div
          v-for="(map, index) in mapList"
          :key="index"
          class="map-item"
          @click="setMapById(map.raidId)"
        >
          <img :src="getRaidMapImg(map.raidName)" :alt="map.raidName" />
          <p>{{ t(`map.mapName.${map.raidName}`) }}</p>
        </div>
      </div>

      <div class="map-confirm-box">
        <button type="button" class="button map-cancel" @click="mapDialogVisible = false">
          {{ t('close') }}
        </button>
      </div>
    </el-dialog>

    <!-- 玩家抽卡，货币设置模态框 -->
    <el-dialog
      v-model="playerSettingDialogVisible"
      class="dialog player-setting-dialog"
      :close-on-click-modal="false"
      width="90rem"
      align-center
    >
      <div class="player-setting-title">
        <h1>{{ t('options.playerSettingTitle') }}</h1>
      </div>

      <div class="player-list-box">
        <div v-for="(player, index) in seatPlayerList" :key="index" class="player-box">
          <div
            :class="{
              back: player?.playerName == undefined,
              titan: player?.role === PlayerRole.Titan,
              hunter: player?.role === PlayerRole.Hunter,
              warlock: player?.role === PlayerRole.Warlock
            }"
            class="player-info"
          >
            <p class="role-id">{{ t('options.number') + player?.roleId }}</p>
            <p class="player-name">{{ t('options.player') + player?.playerName }}</p>
            <p class="player-role">{{ t('options.role') + t(`roleName.${player?.role}`) }}</p>
          </div>

          <div v-if="player?.playerName != undefined" class="player-config-box">
            <p>{{ t('options.playerDrawCount') }}</p>
            <el-input-number
              id="drawCardCountValue"
              v-model="player.drawCount"
              :min="-100"
              :max="100"
              @change="(value) => handleChange('drawCard', player?.playerName, value)"
            />
            <p>{{ t('options.playerMoney') }}</p>
            <el-input-number
              id="drawCardCountValue"
              v-model="player.playerMoney"
              :min="-100"
              :max="100"
              @change="(value) => handleChange('playerMoney', player?.playerName, value)"
            />
          </div>
        </div>
      </div>

      <div class="player-setting-confirm-box">
        <button
          type="button"
          class="button player-setting-cancel"
          @click="playerSettingDialogVisible = false"
        >
          {{ t('close') }}
        </button>
      </div>
    </el-dialog>

    <!-- 游戏挑战信息版 -->
    <InfoBoard type="left" :show-info-board="infoBoard.gameChallenge">
      <template #close-button>
        <div class="close-button">
          <a @click="infoBoard.gameChallenge = !infoBoard.gameChallenge">{{
            infoBoard.gameChallenge ? t('close') : t('infoBoardButtonText01')
          }}</a>
        </div>
      </template>
      <template #title>
        <h1 class="title">{{ t('options.infoBoardTitleText01') }}</h1>
      </template>
      <template #content>
        <div>
          <div v-for="item in 8" :key="item">
            <p class="title">
              {{ t(`options.gameChallengeInfoBoard.item0${item}.mapName`) }} -
              {{ t(`options.gameChallengeInfoBoard.item0${item}.level`) }} -
              {{ t(`options.gameChallengeInfoBoard.item0${item}.name`) }}
            </p>
            <p class="description">
              {{ t(`options.gameChallengeInfoBoard.item0${item}.description`) }}
            </p>
            <hr />
          </div>
        </div>
      </template>
    </InfoBoard>

    <!-- 游戏规则信息版 -->
    <InfoBoard type="right" :show-info-board="infoBoard.gamePlay">
      <template #close-button>
        <div class="close-button">
          <a @click="infoBoard.gamePlay = !infoBoard.gamePlay">{{
            infoBoard.gamePlay ? t('close') : t('infoBoardButtonText02')
          }}</a>
        </div>
      </template>
      <template #title>
        <h1 class="title">{{ t('options.infoBoardTitleText02') }}</h1>
      </template>
      <template #content>
        <div>
          <p v-for="item in 8" :key="item">
            {{ t(`options.gamePlayInfoBoard.infoText0${item}`) }}
          </p>
          <hr />
          <p v-for="item in 5" :key="item">
            {{
              t(`options.gamePlayInfoBoard.infoText${item + 8 < 10 ? '0' + (item + 8) : item + 8}`)
            }}
          </p>
          <hr />
          <p v-for="item in 4" :key="item">
            {{ t(`options.gamePlayInfoBoard.infoText${item + 13}`) }}
          </p>
        </div>
      </template>
    </InfoBoard>
  </div>
</template>

<style lang="scss" scoped>
@use '@renderer/assets/styles/gamepanel/options/index';
</style>
