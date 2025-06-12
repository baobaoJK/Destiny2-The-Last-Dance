<script lang="ts" setup>
import { useUserStore } from '@renderer/stores'
import { Card, DeckType, InfoBoardConfig, PlayerConfig, RoomConfig } from '@renderer/types'
import { SocketData } from '@renderer/types/socket'
import { shuffle } from '@renderer/utils'
import { getSocket } from '@renderer/utils/socket'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import { Socket } from 'socket.io-client'
import { computed, onMounted, Ref, ref } from 'vue'
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
let socket: Socket | undefined

// 玩家信息
const { playerName } = storeToRefs(useUserStore())
const playerConfig = computed((): PlayerConfig | undefined => {
  if (roomConfig?.value?.playerList.length === 0) {
    return undefined
  }

  return roomConfig?.value?.playerList[playerName.value]
})

// 卡牌抽取
const deckInfoDialogVisible = ref(false)
const playerDrawCardsList = ref<Card[]>([])
const deckDialogConfig = ref({
  flips: Array.from({ length: 12 }, () => false),
  deckListName: '',
  canClick: false
})
const deckDialogVisible = computed(() => {
  if (!playerConfig?.value) {
    return false
  }

  return playerName.value == roomConfig?.value.drawCardPlayer
})
const showDeckList = (deckType: DeckType): void => {
  deckDialogConfig.value.flips = Array.from({ length: 12 }, () => false)
  setWebLoading(true)
  socket?.emit('showDeckList', {
    roomId: roomConfig?.value?.roomId,
    playerName: playerName.value,
    deckType: deckType
  })
}
// 卡牌点击事件
const clickCard = (card: Card, index: number): void => {
  // 判断能否点击
  if (!deckDialogConfig.value.canClick) {
    ElMessage({
      message: t('card.message.errorText05'),
      type: 'error',
      grouping: true
    })
    return
  }
  // 判断卡牌是否被抽取过
  if (!deckDialogConfig.value.flips[index] && deckDialogConfig.value.canClick) {
    setWebLoading(true)
    socket?.emit('clickCard', {
      roomId: roomConfig?.value?.roomId,
      playerName: playerName.value,
      card: card
    })
  }
}
// 关闭抽卡界面
const closeDeck = (): void => {
  setWebLoading(true)
  socket?.emit('closeDeckList', {
    roomId: roomConfig?.value?.roomId,
    playerName: playerName.value
  })
}

onMounted(() => {
  socket = getSocket()

  socket?.off('showDeckList')
  socket?.on('showDeckList', (socketData: SocketData) => {
    console.log(socketData)
    deckDialogConfig.value.deckListName = socketData?.data?.deckListName
    playerDrawCardsList.value = socketData?.data?.deckList

    // 观星
    if (playerConfig.value?.playerAttributes.stargazing) {
      deckDialogConfig.value.flips = Array.from({ length: 12 }, () => true)

      const changeCardState = setTimeout(() => {
        deckDialogConfig.value.flips = Array.from({ length: 12 }, () => false)
        clearTimeout(changeCardState)
      }, 5000)

      const shuffleDeckList = setTimeout(() => {
        playerDrawCardsList.value = shuffle(playerDrawCardsList.value)
        deckDialogConfig.value.canClick = true
        clearTimeout(shuffleDeckList)
      }, 5500)
    } else {
      deckDialogConfig.value.canClick = true
    }

    setWebLoading(false)
  })

  socket?.off('clickCard')
  socket?.on('clickCard', (socketData: SocketData) => {
    for (let i = 0; i < playerDrawCardsList.value.length; i++) {
      if (playerDrawCardsList.value[i].cardName === socketData?.data?.card.cardName) {
        deckDialogConfig.value.flips[i] = true
      }
    }
  })
})
</script>

<template>
  <div id="drawcards">
    <h1 class="deck-title">{{ t('card.title', { drawCount: playerConfig?.drawCount }) }}</h1>

    <!-- 卡牌抽奖框 -->
    <div class="deck-list">
      <div v-show="!playerConfig?.playerAttributes?.gambler" class="deck card-item-1">
        <div id="safe" class="deck-1 card" @click="showDeckList(DeckType.Safe)"></div>
        <p class="deck-name">- {{ t('deckListName.safe') }} -</p>
      </div>
      <div v-show="!playerConfig?.playerAttributes?.gambler" class="deck card-item-2">
        <div id="danger" class="deck-2 card" @click="showDeckList(DeckType.Danger)"></div>
        <p class="deck-name">- {{ t('deckListName.danger') }} -</p>
      </div>
      <div class="deck card-item-3">
        <div id="gambit" class="deck-3 card" @click="showDeckList(DeckType.Gambit)"></div>
        <p class="deck-name">- {{ t('deckListName.gambit') }} -</p>
      </div>
      <div v-show="!playerConfig?.playerAttributes?.gambler" class="deck card-item-4">
        <div id="luck" class="deck-4 card" @click="showDeckList(DeckType.Luck)"></div>
        <p class="deck-name">- {{ t('deckListName.luck') }} -</p>
      </div>
      <div v-show="!playerConfig?.playerAttributes?.gambler" class="deck card-item-5">
        <div id="devote" class="deck-5 card" @click="showDeckList(DeckType.Devote)"></div>
        <p class="deck-name">- {{ t('deckListName.devote') }} -</p>
      </div>
    </div>

    <!-- 卡牌数量数量显示 -->
    <p class="deck-count">
      {{
        t('card.deckCount', {
          microGainCount: roomConfig?.cardCountList?.MicroGain,
          strongGainCount: roomConfig?.cardCountList?.StrongGain,
          opportunityCount: roomConfig?.cardCountList?.Opportunity,
          microDiscomfortCount: roomConfig?.cardCountList?.MicroDiscomfort,
          strongDiscomfortCount: roomConfig?.cardCountList?.StrongDiscomfort,
          unacceptableCount: roomConfig?.cardCountList?.Unacceptable,
          technologyCount: roomConfig?.cardCountList?.Technology,
          supportCount: roomConfig?.cardCountList?.Support
        })
      }}
    </p>

    <!-- 卡池信息显示按钮 -->
    <button class="button deck-info" @click="deckInfoDialogVisible = true">
      {{ t('card.deckListInfo') }}
    </button>

    <!-- 卡池信息框 -->
    <el-dialog
      v-model="deckInfoDialogVisible"
      class="dialog deck-info-dialog"
      :close-on-click-modal="false"
      align-center
      width="90rem"
    >
      <div class="deck-list-info">
        <h1>
          {{ t('card.deckListInfo') }}
        </h1>
        <p class="deck-type-info safe">
          {{ t('card.deckListInfoText01') }}
        </p>
        <p class="deck-type-info danger">
          {{ t('card.deckListInfoText02') }}
        </p>
        <p class="deck-type-info gambit">
          {{ t('card.deckListInfoText03') }}
        </p>
        <p class="deck-type-info luck">
          {{ t('card.deckListInfoText04') }}
        </p>
        <p class="deck-type-info devote">
          {{ t('card.deckListInfoText05') }}
        </p>
        <hr class="deck-type-info" />
        <p class="deck-type-info">
          {{ t('card.deckListInfoText06') }}
        </p>
        <p class="deck-type-info">
          {{ t('card.deckListInfoText07') }}
        </p>
        <p class="deck-type-info">
          {{ t('card.deckListInfoText08') }}
        </p>
      </div>
      <div class="deck-confirm-box">
        <button type="button" class="button deck-cancel" @click="deckInfoDialogVisible = false">
          {{ t('close') }}
        </button>
      </div>
    </el-dialog>

    <!-- 卡牌抽奖模态框 -->
    <el-dialog
      v-model="deckDialogVisible"
      class="dialog deck-dialog"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      width="79.25rem"
      align-center
    >
      <div class="deck-list-info">
        <p class="deck-list-name">
          {{ t(deckDialogConfig?.deckListName) }}
        </p>
        <p class="deck-list-draw">{{ t('card.title', { drawCount: playerConfig?.drawCount }) }}</p>
      </div>
      <div class="deck-list-box">
        <div
          v-for="(card, index) in playerDrawCardsList"
          :key="index"
          :class="{
            flip: deckDialogConfig.flips[index],
            'card-item-1': deckDialogConfig.deckListName === 'deckListName.safe',
            'card-item-2': deckDialogConfig.deckListName === 'deckListName.danger',
            'card-item-3': deckDialogConfig.deckListName === 'deckListName.gambit',
            'card-item-4': deckDialogConfig.deckListName === 'deckListName.luck',
            'card-item-5': deckDialogConfig.deckListName === 'deckListName.devote'
          }"
          class="card-item"
          @click="clickCard(card, index)"
        >
          <div class="card card-front">
            <div class="card-info">
              <p class="card-id">{{ t(`cardList.${card.itemName}.name`) }}</p>
              <p class="card-name">{{ t(`cardList.${card.itemName}.sub`) }}</p>
            </div>
          </div>
          <div class="card card-back"></div>
        </div>
      </div>
      <div class="deck-confirm-box">
        <button type="button" class="button deck-cancel" @click="closeDeck">
          {{ t('close') }}
        </button>
      </div>
    </el-dialog>

    <!-- 卡池关闭 -->
    <div
      v-if="
        playerConfig?.playerAttributes?.deckClosed ||
        playerConfig?.playerAttributes?.thirteen ||
        playerConfig?.giveUp
      "
      class="deck-closed"
    ></div>

    <!-- 卡池信息版 -->
    <InfoBoard type="left" :show-info-board="infoBoard.gameDeck">
      <template #close-button>
        <div class="close-button">
          <a @click="infoBoard.gameDeck = !infoBoard.gameDeck">{{
            infoBoard.gameDeck ? t('close') : t('card.deckListInfoBoardText')
          }}</a>
        </div>
      </template>
      <template #title>
        <h1 class="title">{{ t('card.deckListInfoBoardTitle') }}</h1>
      </template>
      <template #content>
        <div>
          <p v-for="index in 6" :key="index">
            {{ t(`card.deckListInfoBoard.infoText0${index}`) }}
          </p>
          <hr />
          <p v-for="index in 5" :key="index">
            {{
              t(`card.deckListInfoBoard.infoText${index + 6 < 10 ? '0' + (index + 6) : index + 6}`)
            }}
          </p>
        </div>
      </template>
    </InfoBoard>
  </div>
</template>

<style lang="scss" scoped>
@use '@renderer/assets/styles/gamepanel/drawcards';
</style>
