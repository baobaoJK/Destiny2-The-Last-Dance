<script lang="ts" setup>
import { useUserStore } from '@renderer/stores'
import { storeToRefs } from 'pinia'
import { ref, computed, onMounted, type Ref } from 'vue'
import { lightImg, cardImg, productionBaseURL } from '@renderer/utils'
import {
  playerLight,
  RoomConfig,
  createDefaultRoomConfig,
  RaidConfig,
  Room,
  createDefaultInfoBoardConfig,
  InfoBoardConfig,
  RoomStatus,
  Card,
  CardType,
  SpecialConfig,
  PlayerConfig,
  PlayerRole,
  PlayerStatus
} from '@renderer/types'
import type { Socket } from 'socket.io-client'
import { getSocket } from '@renderer/utils/socket'
import { ElMessage, type MessageOptions } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { SocketData } from '@renderer/types/socket'
import TipsView from '@renderer/components/tips/IndexView.vue'

const { t } = useI18n()

// 路由
const router = useRouter()
const route = useRoute()
console.log(route)
// 导航栏
const activeIndex = computed(() => {
  let index = 0

  const routeName = route.name
  switch (routeName) {
    case 'room':
      index = 0
      break
    case 'map':
      index = 1
      break
    case 'options':
      index = 2
      break
    case 'drawcards':
      index = 3
      break
    case 'decklist':
      index = 4
      break
    case 'playerevent':
      index = 5
      break
    case 'globalevent':
      index = 6
      break
    case 'shop':
      index = 7
      break
    default:
      index = 0
  }
  return index
})

// Socket
let socket: Socket | null = null

// 用户信息
const { role, playerName, roomId } = storeToRefs(useUserStore())
const userStore = useUserStore()
const playerConfig = computed((): PlayerConfig | null => {
  if (roomConfig?.value === undefined && roomId.value === '') {
    return null
  }
  return roomConfig?.value?.playerList[playerName.value]
})
const roleId = computed(() => {
  if (roomConfig?.value === undefined && roomId.value === '') {
    return 0
  }
  return 0 | roomConfig?.value?.playerList[playerName.value]?.roleId
})
const playerMoney = computed(() => {
  if (roomConfig?.value === undefined && roomId.value === '') {
    return 0
  }
  return 0 | roomConfig?.value?.playerList[playerName.value]?.playerMoney
})
const darwCount = computed(() => {
  if (roomConfig?.value === undefined && roomId.value === '') {
    return 0
  }
  return 0 | roomConfig?.value?.playerList[playerName.value]?.drawCount
})

// 网页加载
const webLoading = ref(false)
const loadingText = ref(t('loadingText'))
const setWebLoading = (status: boolean): void => {
  webLoading.value = status
}

// 房间列表
const roomList: Ref<Room[]> = ref([])

// 房间信息
const roomConfig: Ref<RoomConfig> = ref(createDefaultRoomConfig())

// 重置信息
const resetInfo = (): void => {
  userStore.setRoomId('')
  roomConfig.value = createDefaultRoomConfig()
}

// 玩家手卡列表
const playerDeckListDialog = ref(false)
const playerDeckList = ref<Card[]>([])
const playerDeckListName = ref('')

// 信息版配置
const infoBoard: Ref<InfoBoardConfig> = ref(createDefaultInfoBoardConfig())

// 突袭信息
const raidConfig = computed((): RaidConfig => {
  return roomConfig?.value?.raidConfig
})

// 名片
const emblem = computed(() => {
  let specialStr = `/images/emblem/role/${role.value}-w.jpg`
  let iconStr = `/images/emblem/role/${role.value}_icon.png`

  if (playerName.value === '和泉纱雾') {
    specialStr = `/images/emblem/up/hqsw/special.jpg`
    iconStr = `/images/emblem/up/hqsw/overlay.png`
  } else if (playerName.value === '年糕明') {
    specialStr = `/images/emblem/up/ngm/special.jpg`
    iconStr = `/images/emblem/up/ngm/overlay.png`
  } else if (roomId.value == '') {
    specialStr = `/images/emblem/role/${role.value}-w.jpg`
    iconStr = `/images/emblem/role/${role.value}_icon.png`
  } else if (
    roleId.value !== 0 &&
    roomConfig?.value?.roomOwner === playerName.value &&
    roomId.value != ''
  ) {
    specialStr = `/images/emblem/role/captain-w.jpg`
    iconStr = `/images/emblem/role/captain_icon.png`
  }

  if (import.meta.env.MODE === 'development') {
    return {
      special: new URL(specialStr, import.meta.url).href,
      icon: new URL(iconStr, import.meta.url).href
    }
  } else {
    return {
      special: productionBaseURL + specialStr,
      icon: productionBaseURL + iconStr
    }
  }
})

// 显示提示框
const tipsRef = ref()
const tooltipShow = ref(false)
const tooltipConfig = ref({
  itemName: '',
  itemKind: '',
  itemRarity: '',
  itemDescription: '',
  itemIdea: ''
})
const showTooltip = (card: Card): void => {
  tooltipShow.value = true

  tooltipConfig.value.itemName = t(`cardList.${card.itemName}.name`)
  tooltipConfig.value.itemKind = t(`cardTypeList.${CardType[card.cardType]}`)
  tooltipConfig.value.itemRarity = t(`rarityType.legendary`)
  tooltipConfig.value.itemDescription = t(`cardList.${card.itemName}.description`)
  tooltipConfig.value.itemIdea = card.idea

  tipsRef.value.setToolTips(card)
}

//  关闭提示框
const hideTooltip = (): void => {
  tooltipShow.value = false
}

// 特殊事件模态框
const specialDialogVisible = computed(() => {
  if (!playerConfig?.value?.playerStatus) {
    return false
  }

  if (
    playerConfig?.value?.playerStatus == PlayerStatus.Idle ||
    playerConfig?.value?.playerStatus == PlayerStatus.Draw
  ) {
    return false
  }

  return true
})
const specialConfig = computed((): SpecialConfig | null => {
  if (!playerConfig?.value?.specialConfig) {
    return null
  }

  return playerConfig?.value?.specialConfig
})
// 特殊卡牌执行
const runSpecialByCard = (card: Card): void => {
  const specialConfig = playerConfig?.value?.specialConfig

  if (specialConfig?.eventName === 'Tyrant') {
    specialConfig.to = card.roleId
  }

  if (
    (specialConfig?.eventName === 'Bumper-Harvest' ||
      specialConfig?.eventName === 'Biochemical-Matrix') &&
    playerConfig?.value?.roleId !== specialConfig?.players[specialConfig?.nowPlayer]
  ) {
    ElMessage({
      message: t('gamepanel.message.warningText03'),
      grouping: true,
      type: 'warning'
    })
    return
  }

  setWebLoading(true)
  socket?.emit('runSpecialByCard', {
    roomId: roomId.value,
    specialConfig: specialConfig,
    card: card
  })
}

const selectRoleId = ref<number | number[]>(0)
const showPlayerOptions = computed(() => {
  return selectRoleId.value !== 0
})
const setRoleId = (id: number): void => {
  if (
    id == playerConfig?.value?.roleId &&
    playerConfig?.value.specialConfig.eventName !== 'Transposition'
  ) {
    ElMessage({
      message: t('gamepanel.message.warningText01'),
      grouping: true,
      type: 'warning'
    })
    return
  }

  if (playerConfig.value?.specialConfig.eventName === 'Transposition') {
    if (selectRoleId.value == 0) {
      selectRoleId.value = []
    }

    if (Array.isArray(selectRoleId.value) && selectRoleId.value.length < 2) {
      selectRoleId.value.push(id)
    } else {
      if (Array.isArray(selectRoleId.value) && selectRoleId.value.includes(id)) {
        ElMessage({
          message: t('gamepanel.message.warningText05'),
          grouping: true,
          type: 'warning'
        })
      } else {
        if (Array.isArray(selectRoleId.value)) {
          selectRoleId.value.shift()
          selectRoleId.value.push(id)
        }
      }
    }
  } else {
    selectRoleId.value = id
  }
}
const runSpecialByEvent = (value): void => {
  if (
    specialConfig?.value?.eventName === 'Alex-Mercer' ||
    specialConfig?.value?.eventName === 'Personal' ||
    specialConfig?.value?.eventName === 'This-Is-The-Deal' ||
    specialConfig?.value?.eventName === 'In-The-Name-of-Preservation' ||
    specialConfig?.value?.eventName === 'Risk-Transformation'
  ) {
    if (selectRoleId.value === 0) {
      ElMessage({
        message: t('gamepanel.message.warningText02'),
        grouping: true,
        type: 'warning'
      })
      return
    }
  }

  if (specialConfig?.value?.eventName === 'Transposition') {
    if (Array.isArray(selectRoleId.value) && selectRoleId.value.length < 2) {
      ElMessage({
        message: t('gamepanel.message.warningText04'),
        grouping: true,
        type: 'warning'
      })
      return
    }
  }

  setWebLoading(true)

  socket?.emit('runSpecialByEvent', {
    roomId: roomId.value,
    specialConfig: specialConfig?.value,
    specialData: {
      send:
        typeof selectRoleId.value != 'number' ? selectRoleId.value[0] : playerConfig?.value?.roleId,
      to: typeof selectRoleId.value != 'number' ? selectRoleId.value[1] : selectRoleId.value,
      value: value
    }
  })
}
onMounted(() => {
  socket = getSocket()

  // 接收信息
  socket?.off('message')
  socket?.on('message', (socketData: SocketData): void => {
    console.log(socketData)
    if (
      socketData.message !== undefined &&
      socketData.message !== '' &&
      socketData.message !== null
    ) {
      console.log(socketData)

      let messageStr = t(socketData.message, socketData?.messageData)

      // 开始游戏
      if (socketData.eventType === 'startGame') {
        router.push('/map')
      }

      // 突袭地图
      if (socketData.eventType === 'raidMap') {
        const raidMapNameKey = socketData.messageData?.raidName as string
        const localizedRaidName = t(`map.mapName.${raidMapNameKey}`)
        messageStr = t(socketData.message, { raidName: localizedRaidName })
      }

      // 卡牌
      if (socketData.eventType === 'card') {
        const cardNameKey = socketData.messageData?.cardName as string
        const localizedCardName = t(cardNameKey)

        if (socketData?.messageData?.playerName != undefined) {
          const playerName = socketData.messageData?.playerName as string
          messageStr = t(socketData.message, {
            playerName: playerName,
            cardName: localizedCardName
          })
        } else {
          messageStr = t(socketData.message, { cardName: localizedCardName })
        }
      }

      // 个人事件
      if (socketData.eventType === 'playerEvent') {
        const playerEventNameKey = socketData.messageData?.playerEventName as string
        const localizedPlayerEventName = t(playerEventNameKey)

        if (socketData?.messageData?.water != undefined) {
          const water = socketData?.messageData?.water as string
          const localizedWaterName = t(`item.${water}.name`)
          messageStr = t(socketData.message, {
            playerEventName: localizedPlayerEventName,
            water: localizedWaterName
          })
        } else if (socketData?.messageData?.drawCount != undefined) {
          const drawCount = socketData?.messageData?.drawCount as number
          messageStr = t(socketData.message, {
            playerEventName: localizedPlayerEventName,
            drawCount: drawCount
          })
        } else if (socketData?.messageData?.playerMoney != undefined) {
          const playerMoney = socketData.messageData?.playerMoney as number
          messageStr = t(socketData.message, {
            playerEventName: localizedPlayerEventName,
            money: playerMoney
          })
        } else {
          messageStr = t(socketData.message, {
            playerEventName: localizedPlayerEventName
          })
        }
      }

      // 全局事件
      if (socketData.eventType === 'globalEvent') {
        const globalEventNameKey = socketData.messageData?.globalEventName as string
        const localizedGlobalEventName = t(globalEventNameKey)
        messageStr = t(socketData.message, { globalEventName: localizedGlobalEventName })
      }

      // 五谷丰登 生化母体
      if (
        socketData.eventType === 'Bumper-Harvest' ||
        socketData.eventType === 'Biochemical-Matrix'
      ) {
        const cardNameKey = socketData.messageData?.cardName as string
        const localizedCardName = t(cardNameKey)
        messageStr = t(socketData.message, {
          playerId: socketData.messageData?.playerId as number,
          cardName: localizedCardName
        })
      }

      // 特殊卡牌
      if (socketData.eventType === 'specialCard') {
        const specialCardNameKey = socketData.messageData?.specialCardName as string
        const localizedCardName = t(specialCardNameKey)

        if (socketData?.messageData?.playerName != undefined) {
          const playerName = socketData.messageData?.playerName as string
          messageStr = t(socketData.message, {
            playerName: playerName,
            cardName: localizedCardName
          })
        } else {
          messageStr = t(socketData.message, { cardName: localizedCardName })
        }
      }

      // 商店物品
      if (socketData.eventType === 'shopItem') {
        const shopItemNameKey = socketData.messageData?.itemName as string
        const localizedItemName = t(shopItemNameKey)

        messageStr = t(socketData?.message, {
          playerName: socketData?.messageData?.playerName as string,
          itemName: localizedItemName
        })
      }

      ElMessage({
        message: messageStr,
        grouping: true,
        type: socketData.messageType
      } as MessageOptions)
    }

    // 房间号不存在
    if (socketData.eventType === 'idNone') {
      resetInfo()
      router.replace('/room')
    }

    // 获取房间列表
    if (socketData.eventType === 'roomList') {
      console.log(socketData.data)
      roomList.value = socketData.data?.roomList
    }

    // 加入房间
    if (socketData.eventType === 'joinRoom') {
      console.log(socketData.data?.roomInfo)
      roomId.value = socketData.data?.roomInfo.roomId
      roomConfig.value = socketData.data?.roomInfo
      webLoading.value = true
    }

    // 房间信息更新
    if (socketData.eventType === 'roomInfo') {
      roomConfig.value = socketData.data?.roomInfo
      webLoading.value = true
    }

    // 减除
    if (socketData.eventType === 'kickPlayer') {
      router.push('/home')
      resetInfo()
    }

    // 查看玩家手牌信息
    if (socketData.eventType === 'getPlayerDeckList') {
      console.log(socketData.data?.playerDeckList)
      const deckList = socketData.data.playerDeckList
      if (deckList.length === 0) {
        ElMessage({
          message: t('gamepanel.noCard'),
          grouping: true,
          type: 'info'
        })
        return
      }
      playerDeckListName.value = socketData.data.playerName
      playerDeckList.value = deckList
      playerDeckListDialog.value = true
    }

    webLoading.value = false
  })

  // Doro
  socket?.off('doro')
  socket?.on('doro', (socketData: SocketData): void => {
    if (socketData?.message === 'show') {
      window.electron.ipcRenderer.send('SHOW_DORO')
    }
    if (socketData?.message === 'close') {
      window.electron.ipcRenderer.send('CLOSE_DORO')
    }
  })

  // 判断加入房间
  if (roomId.value !== '') {
    console.log('加入房间')
    setWebLoading(true)
    socket?.emit('joinRoom', {
      roomId: roomId.value,
      playerInfo: {
        role: role.value,
        playerName: playerName.value
      }
    })
  }
})
</script>

<template>
  <div
    id="gamepanel"
    v-loading.fullscreen.lock="webLoading"
    :element-loading-text="loadingText"
    element-loading-background="rgba(0, 0, 0, 0.8)"
    @mousemove="tipsRef?.moveTooltip($event)"
  >
    <!-- 提示框 -->
    <TipsView ref="tipsRef" :tooltip-show="tooltipShow">
      <template #header>
        <div class="name">{{ tooltipConfig.itemName }}</div>
        <div class="type">
          <div class="kind">{{ tooltipConfig.itemKind }}</div>
          <div class="rarity">{{ tooltipConfig.itemRarity }}</div>
        </div>
      </template>
      <template #main>
        <div class="description">
          <div class="text">
            <p class="type">{{ tooltipConfig.itemDescription }}</p>
            <p v-if="tooltipConfig.itemIdea !== 'D2RRX'">
              {{ t('idea') + tooltipConfig.itemIdea }}
            </p>
          </div>
          <div class="line"></div>
        </div>
      </template>
    </TipsView>

    <div class="header">
      <div class="image" :style="{ 'background-image': `url(${emblem.special})` }"></div>
      <div class="role">
        <div class="icon" :style="{ 'background-image': `url(${emblem.icon})` }"></div>
        <div class="info">
          <router-link class="emblem" to="home">
            <p class="name">{{ playerName }}</p>
            <div class="sub">
              <p class="number">{{ t('gamepanel.numberPlayer', { playerId: roleId }) }}</p>
              <p class="line">/</p>
              <p class="light">{{ playerLight }}</p>
              <p class="line">/</p>
              <p class="money">
                <img class="light" :src="lightImg" alt="light.png" />
                {{ t('light') }}: {{ playerMoney }}
              </p>
              <p class="line">/</p>
              <p class="draw-count">
                <img class="draw" :src="cardImg" alt="card.png" />
                {{ t('drawCount') }}: {{ darwCount }}
              </p>
            </div>
          </router-link>
        </div>
      </div>

      <div class="menu">
        <ul>
          <li key="0" class="menu-link" :class="{ active: activeIndex === 0 }">
            <router-link to="room" target="windows">{{ t('gamepanel.room') }}</router-link>
          </li>
          <li
            v-if="roomConfig?.roomStatus === RoomStatus.PLAYING"
            key="1"
            class="menu-link"
            :class="{ active: activeIndex === 1 }"
          >
            <router-link to="map" target="windows">{{ t('gamepanel.map') }}</router-link>
          </li>
          <li v-if="raidConfig" key="2" class="menu-link" :class="{ active: activeIndex === 2 }">
            <router-link to="options" target="windows">{{ t('gamepanel.options') }}</router-link>
          </li>
          <li v-if="raidConfig" key="3" class="menu-link" :class="{ active: activeIndex === 3 }">
            <router-link to="drawcards" target="windows">{{
              t('gamepanel.drawcards')
            }}</router-link>
          </li>
          <li v-if="raidConfig" key="4" class="menu-link" :class="{ active: activeIndex === 4 }">
            <router-link to="decklist" target="windows">{{ t('gamepanel.decklist') }}</router-link>
          </li>
          <li v-if="raidConfig" key="5" class="menu-link" :class="{ active: activeIndex === 5 }">
            <router-link to="playerevent" target="windows">{{
              t('gamepanel.playerevent')
            }}</router-link>
          </li>
          <li v-if="raidConfig" key="6" class="menu-link" :class="{ active: activeIndex === 6 }">
            <router-link to="globalevent" target="windows">{{
              t('gamepanel.globalevent')
            }}</router-link>
          </li>
          <li v-if="raidConfig" key="7" class="menu-link" :class="{ active: activeIndex === 7 }">
            <router-link to="shop" target="windows">{{ t('gamepanel.shop') }}</router-link>
          </li>
        </ul>
      </div>
    </div>

    <div class="main">
      <RouterView
        :room-config="roomConfig"
        :room-list="roomList"
        :reset-info="resetInfo"
        :web-loading="webLoading"
        :set-web-loading="setWebLoading"
        :info-board="infoBoard"
      />
    </div>

    <!-- 特殊事件模态框 -->
    <el-dialog
      v-model="specialDialogVisible"
      class="dialog special-dialog"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      width="85rem"
      align-center
    >
      <div class="box">
        <!-- 标头 -->
        <div class="title-box">
          <h1 class="title">{{ t(`${specialConfig?.title}`) }}</h1>
          <p class="sub-title">
            {{ t(`${specialConfig?.description}`, { playerId: specialConfig?.to }) }}
          </p>
          <p v-if="showPlayerOptions" class="tips">
            {{ t('gamepanel.selectPlayerId', { playerId: selectRoleId }) }}
          </p>
        </div>

        <!-- 卡牌选取列表 -->
        <div
          v-if="
            specialConfig?.eventType === 'cardList' && specialConfig?.eventName !== 'Take-Others'
          "
          class="deck-list-box"
        >
          <div
            v-for="(card, index2) in specialConfig?.deckList"
            :key="index2"
            :class="{
              'card-item-1': card.cardType === 'MicroGain' || card.cardType === 'StrongGain',
              'card-item-2':
                card.cardType === 'MicroDiscomfort' || card.cardType === 'StrongDiscomfort',
              'card-item-3': card.cardType === 'Opportunity' || card.cardType === 'Unacceptable',
              'card-item-4': card.cardType === 'Technology',
              'card-item-5': card.cardType === 'Support'
            }"
            class="item card-item"
          >
            <div
              v-if="specialConfig?.eventName !== 'Money'"
              class="card"
              @click="runSpecialByCard(card)"
            >
              <div class="info card-info">
                <p class="card-name">{{ t(`cardList.${card.itemName}.name`) }}</p>
                <p class="card-sub">{{ t(`cardList.${card.itemName}.sub`) }}</p>
                <p v-if="card.roleId" class="card-role-id">
                  {{ card.roleId + t('gamepanel.numberPlayer') }}
                </p>
              </div>
            </div>
            <div v-else class="card" @click="runSpecialByCard(card)">
              <div class="info card-info">
                <p class="card-name">{{ t(card.cardName) }}</p>
                <p class="card-sub">{{ t(card.cardDescription) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 顺手牵羊 -->
        <div v-if="specialConfig?.eventName === 'Take-Others'" class="deck-list-box">
          <div
            v-for="(card, index2) in specialConfig?.deckList"
            :key="index2"
            class="item card-item card-item-1"
          >
            <div class="card" @click="runSpecialByCard(card)">
              <div class="info card-info">
                <p v-if="card.roleId" class="card-role-id">
                  {{ card.roleId }} {{ t('numberPlayer') }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 玩家列表 -->
        <div v-if="specialConfig?.eventType === 'playerList'" class="player-list-box">
          <div v-for="(player, index) in specialConfig?.playerList" :key="index" class="player-box">
            <div
              :class="{
                back: player?.playerName == undefined,
                titan: player?.role === PlayerRole.Titan,
                hunter: player?.role === PlayerRole.Hunter,
                warlock: player?.role === PlayerRole.Warlock
              }"
              class="player-info"
              @click="setRoleId(player?.roleId)"
            >
              <p class="role-id">{{ t('gamepanel.number') + player?.roleId }}</p>
              <p class="player-name">{{ t('gamepanel.player') + player?.playerName }}</p>
              <p class="player-role">{{ t('gamepanel.role') + player?.role }}</p>
            </div>
          </div>
          <div class="player-options">
            <button
              v-for="(option, index) in specialConfig?.optionsList"
              :key="index"
              type="button"
              class="button"
              @click="runSpecialByEvent(option.value)"
            >
              {{ t(`${option.text}`) }}
            </button>
            <button type="button" class="button" @click="specialDialogVisible = false">
              {{ t('gamepanel.bug') }}
            </button>
          </div>
        </div>

        <!-- 选项列表 -->
        <div v-if="specialConfig?.eventType === 'optionsList'" class="options-list-box">
          <button
            v-for="(option, index) in specialConfig?.optionsList"
            :key="index"
            type="button"
            class="button"
            @click="runSpecialByEvent(option.value)"
          >
            {{ t(`${option.text}`) }}
          </button>
          <button type="button" class="button" @click="specialDialogVisible = false">
            {{ t('gamepanel.bug') }}
          </button>
        </div>
      </div>
    </el-dialog>

    <!-- 玩家卡牌列表框 -->
    <el-dialog
      v-model="playerDeckListDialog"
      class="dialog player-deck-dialog"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      width=" 75rem"
      align-center
    >
      <div class="box">
        <div class="title-box">
          <h1 class="title">
            {{ t('gamepanel.playerDeckList', { playerName: playerDeckListName }) }}
          </h1>
        </div>
        <div class="deck-list-box">
          <el-scrollbar
            height="25rem"
            native
            view-style="display: flex; flex-wrap: wrap; justify-content: center; width: 65rem; overfloy-x: hidden;"
          >
            <div
              v-for="card in playerDeckList"
              :key="card.cardId"
              :class="{
                'card-item-1': card.cardType === 'MicroGain' || card.cardType === 'StrongGain',
                'card-item-2':
                  card.cardType === 'MicroDiscomfort' || card.cardType === 'StrongDiscomfort',
                'card-item-3': card.cardType === 'Opportunity' || card.cardType === 'Unacceptable',
                'card-item-4': card.cardType === 'Technology',
                'card-item-5': card.cardType === 'Support'
              }"
              class="item card-item"
              @mousemove="showTooltip(card)"
              @mouseout="hideTooltip()"
            >
              <div class="card">
                <div class="info card-info">
                  <p class="card-name">{{ t(`cardList.${card.itemName}.name`) }}</p>
                  <p class="card-sub">{{ t(`cardList.${card.itemName}.sub`) }}</p>
                </div>
              </div>
            </div>
          </el-scrollbar>
        </div>
        <button type="button" class="button" @click="playerDeckListDialog = false">
          {{ t('close') }}
        </button>
      </div>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
@use '@renderer/assets/styles/gamepanel';
</style>
