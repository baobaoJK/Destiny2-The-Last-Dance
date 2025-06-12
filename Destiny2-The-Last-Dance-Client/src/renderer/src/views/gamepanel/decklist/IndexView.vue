<script lang="ts" setup>
import { ref, computed, Ref, onMounted } from 'vue'
import { Card, InfoBoardConfig, RoomConfig } from '@renderer/types'
import { Socket } from 'socket.io-client'
import { getSocket } from '@renderer/utils/socket'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@renderer/stores'
import { SocketData } from '@renderer/types/socket'
import { CardType } from '@renderer/types'
import { useI18n } from 'vue-i18n'
import { cardImg } from '@renderer/utils'
import TipsView from '@renderer/components/tips/IndexView.vue'
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

// 用户信息
const { playerName } = storeToRefs(useUserStore())

// i18n
const { t } = useI18n()

// socket
let socket: Socket | null

// 提示框
const tipsRef = ref()
const tooltipShow = ref(false)
const tooltipConfig = ref({
  itemName: '',
  itemKind: '',
  itemRarity: '',
  itemDescription: '',
  itemCount: 0,
  itemAllCount: 0,
  itemIdea: ''
})

// 显示提示框
const showTooltip = (card: Card, index: number): void => {
  tooltipShow.value = true

  tooltipConfig.value.itemName = t(`cardList.${card.itemName}.name`)
  tooltipConfig.value.itemKind = t(`cardTypeList.${CardType[index]}`)
  tooltipConfig.value.itemRarity = t('rarityType.legendary')
  tooltipConfig.value.itemDescription = t(`cardList.${card.itemName}.description`)
  tooltipConfig.value.itemCount = card.count
  tooltipConfig.value.itemAllCount = card.allCount
  tooltipConfig.value.itemIdea = card.idea

  tipsRef.value.setToolTips(card)
}

//  关闭提示框
const hideTooltip = (): void => {
  tooltipShow.value = false
}

// 获取玩家卡牌
const getCardCount = computed(() => {
  if (!roomConfig?.value?.playerList[playerName.value]) return 0
  let count = 0

  const playerDeckList = roomConfig?.value?.playerList[playerName.value]?.deckList
  const enumValues = Object.values(CardType)
  for (let i = 0; i < 8; i++) {
    playerDeckList[enumValues[i]].forEach((card) => {
      if (card != null) {
        count += 1
      }
    })
  }
  return count
})

// 添加卡牌
const activeName = ref(CardType.MicroGain)
const allDeckList = ref()
const addCardDialogVisible = ref(false)
const addCardButton = (): void => {
  setWebLoading(true)
  socket?.emit('getCardList', { roomId: roomConfig?.value?.roomId })
  addCardDialogVisible.value = true
}
const addCard = (card: Card): void => {
  setWebLoading(true)
  socket?.emit('saveCard', {
    roomId: roomConfig?.value?.roomId,
    playerName: playerName.value,
    card: card
  })
  socket?.emit('getCardList', { roomId: roomConfig?.value?.roomId })
}

// 删除卡牌
const deleteCardButton = (card: Card): void => {
  setWebLoading(true)
  socket?.emit('deleteCard', {
    roomId: roomConfig?.value?.roomId,
    playerName: playerName.value,
    card: card
  })
}

// 随机卡牌
const randomDialogVisible = ref(false)
const randomCardButton = (): void => {
  randomDialogVisible.value = true
}
const randomCard = (length: number, cardType: CardType, byCount: boolean): void => {
  setWebLoading(true)
  socket?.emit('getRandomCard', {
    roomId: roomConfig?.value?.roomId,
    playerName: playerName.value,
    length: length,
    cardType: cardType,
    byCount: byCount
  })
}

// 转换
const transformationCard = (card: Card): void => {
  setWebLoading(true)
  socket?.emit('transformCard', {
    roomId: roomConfig?.value?.roomId,
    playerName: playerName.value,
    card: card
  })
}

// 初始化
onMounted(() => {
  socket = getSocket()

  socket?.off('getCardList')
  socket?.on('getCardList', (socketData: SocketData) => {
    console.log(socketData.data)
    allDeckList.value = socketData.data.cardList
    setWebLoading(false)
  })
})
</script>

<template>
  <div id="decklist" @mousemove="tipsRef?.moveTooltip($event)">
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
              {{ t('deckList.cardIdea') + tooltipConfig.itemIdea }}
            </p>
          </div>
        </div>
        <div class="line"></div>
        <div class="monetary">
          <div class="name">
            <img class="card" :src="cardImg" alt="cardImg.png" />
            <p>{{ t('deckList.remainingCardPool') }}</p>
          </div>
          <div class="info">
            <p class="text">
              <span class="count">{{ tooltipConfig.itemCount }}</span> /
              <span class="all-count">{{ tooltipConfig.itemAllCount }}</span>
            </p>
          </div>
        </div>
      </template>
    </TipsView>

    <div class="decks">
      <div class="deck-top">
        <h1 class="deck-title">{{ t('deckList.playerDeckListTitle') }}</h1>
        <div class="deck-options">
          <button class="button get-button" @click="addCardButton()">
            {{ t('deckList.deckListButtonText01') }}
          </button>
          <button class="button random-button" @click="randomCardButton()">
            {{ t('deckList.deckListButtonText02') }}
          </button>
          <!-- <button class="button shuffle-button" @click="shuffleCardButton()">打乱卡牌顺序 {{ t('deckList.deckListButtonText03') }} </button> -->
        </div>
        <hr class="deck-line" />
      </div>

      <div v-if="getCardCount == 0" class="card-list">
        <h2 class="deck-title">{{ t('deckList.youDontHaveCard') }}</h2>
      </div>
      <div
        v-for="(cardList, index) in roomConfig?.playerList[playerName]?.deckList"
        :key="index"
        class="card-list"
      >
        <div
          class="card-list-header"
          :style="{ display: cardList.length === 0 ? 'none' : 'block' }"
        >
          <h2 class="deck-title">
            {{ t(`cardTypeList.${CardType[index]}`) }} -
            {{ t('deckList.holdCard', { count: cardList.length }) }}
          </h2>
          <hr class="deck-line" />
        </div>

        <div
          v-for="card in cardList"
          :key="card.id"
          :class="{
            'card-item-1': card.cardType === 'MicroGain' || card.cardType === 'StrongGain',
            'card-item-2':
              card.cardType === 'MicroDiscomfort' || card.cardType === 'StrongDiscomfort',
            'card-item-3': card.cardType === 'Opportunity' || card.cardType === 'Unacceptable',
            'card-item-4': card.cardType === 'Technology',
            'card-item-5': card.cardType === 'Support'
          }"
          class="card-item"
        >
          <div v-if="cardList.length != 0" class="card">
            <div class="card-info">
              <div>
                <p class="card-name">- {{ t(`cardList.${card.itemName}.name`) }} -</p>
                <p class="card-sub">- {{ t(`cardList.${card.itemName}.sub`) }}-</p>
              </div>
              <div>
                <p class="card-text">{{ t(`cardList.${card.itemName}.description`) }}</p>
                <hr v-if="card.idea !== 'D2RRX'" />
                <p v-if="card.idea !== 'D2RRX'">{{ t('deckList.cardIdea') + card.idea }}</p>
              </div>
            </div>
          </div>
          <button class="button delete-button" @click="deleteCardButton(card)">
            {{ t('delete') }}
          </button>
          <button
            v-if="card.itemName == 'transformation'"
            class="button use-button"
            @click="transformationCard(card)"
          >
            {{ t('use') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 卡牌选取模态框 -->
    <el-dialog
      v-model="addCardDialogVisible"
      class="dialog card-dialog"
      :close-on-click-modal="false"
      width="105.25rem"
      align-center
    >
      <h1 class="title">{{ t('deckList.deckListButtonText01') }}</h1>
      <div class="box card-list-box">
        <el-tabs v-model="activeName" class="card-tabs">
          <el-tab-pane
            v-for="(deckList, index) in allDeckList"
            :key="index"
            :label="
              t('deckList.addCardDialogLabel', {
                cardType: t(`cardTypeList.${CardType[index]}`),
                cardCount: deckList.length
              })
            "
            :name="CardType[index]"
          >
            <el-scrollbar
              height="35rem"
              native
              view-style="display: flex; flex-wrap: wrap; justify-content: center; width: 100rem; overfloy-x: hidden;"
            >
              <div
                v-for="(card, index2) in deckList"
                :key="index2"
                :class="{
                  'card-item-1': card.cardType === 'MicroGain' || card.cardType === 'StrongGain',
                  'card-item-2':
                    card.cardType === 'MicroDiscomfort' || card.cardType === 'StrongDiscomfort',
                  'card-item-3':
                    card.cardType === 'Opportunity' || card.cardType === 'Unacceptable',
                  'card-item-4': card.cardType === 'Technology',
                  'card-item-5': card.cardType === 'Support'
                }"
                class="item card-item"
                @mousemove="showTooltip(card, index)"
                @mouseout="hideTooltip()"
              >
                <div class="card" @click="addCard(card)">
                  <div class="info card-info">
                    <div>
                      <p class="card-name">{{ t(`cardList.${card.itemName}.name`) }}</p>
                      <p class="card-sub">{{ t(`cardList.${card.itemName}.sub`) }}</p>
                    </div>
                    <div>
                      <p class="card-level">
                        {{ t('deckList.cardLevel', { cardLevel: card.cardLevel }) }}
                      </p>
                      <p class="card-description">
                        {{ t('deckList.cardPoolRemaining', { cardCount: card.count }) }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </el-scrollbar>
          </el-tab-pane>
        </el-tabs>
      </div>

      <button
        type="button"
        class="button card-cancel card-close"
        @click="addCardDialogVisible = false"
      >
        {{ t('cancel') }}
      </button>
    </el-dialog>

    <!-- 获取随机卡牌 -->
    <el-dialog
      v-model="randomDialogVisible"
      class="dialog random-dialog"
      :close-on-click-modal="false"
      width="75.25rem"
      align-center
    >
      <h1 class="title">{{ t('deckList.deckListButtonText02') }}</h1>
      <div class="box random-list-box">
        <div class="random-flex random-left">
          <div class="item random-item card-item-4">
            <div class="card" @click="randomCard(1, CardType.Technology, false)">
              <div class="info random-info">
                {{ t('deckList.takeOne') }}
                <p class="card-id">{{ t(`cardTypeList.${CardType.Technology}`) }}</p>
              </div>
            </div>
          </div>
        </div>
        <div class="random-flex random-center">
          <div class="item random-item card-item-1">
            <div class="card" @click="randomCard(1, CardType.MicroGain, false)">
              <div class="info random-info">
                {{ t('deckList.takeOne') }}
                <p class="card-id">{{ t(`cardTypeList.${CardType.MicroGain}`) }}</p>
              </div>
            </div>
          </div>
          <div class="item random-item card-item-3">
            <div class="card" @click="randomCard(1, CardType.Opportunity, false)">
              <div class="info random-info">
                {{ t('deckList.takeOne') }}
                <p class="card-id">{{ t(`cardTypeList.${CardType.Opportunity}`) }}</p>
              </div>
            </div>
          </div>
          <div class="item random-item card-item-2">
            <div class="card" @click="randomCard(1, CardType.MicroDiscomfort, false)">
              <div class="info random-info">
                {{ t('deckList.takeOne') }}
                <p class="card-id">{{ t(`cardTypeList.${CardType.MicroDiscomfort}`) }}</p>
              </div>
            </div>
          </div>
          <div class="item random-item card-item-1">
            <div class="card" @click="randomCard(1, CardType.StrongGain, false)">
              <div class="info random-info">
                {{ t('deckList.takeOne') }}
                <p class="card-id">{{ t(`cardTypeList.${CardType.StrongGain}`) }}</p>
              </div>
            </div>
          </div>
          <div class="item random-item card-item-3">
            <div class="card" @click="randomCard(1, CardType.Unacceptable, false)">
              <div class="info random-info">
                {{ t('deckList.takeOne') }}
                <p class="card-id">{{ t(`cardTypeList.${CardType.Unacceptable}`) }}</p>
              </div>
            </div>
          </div>
          <div class="item random-item card-item-2">
            <div class="card" @click="randomCard(1, CardType.StrongDiscomfort, false)">
              <div class="info random-info">
                {{ t('deckList.takeOne') }}
                <p class="card-id">{{ t(`cardTypeList.${CardType.StrongDiscomfort}`) }}</p>
              </div>
            </div>
          </div>
        </div>
        <div class="random-flex random-right">
          <div class="item random-item card-item-5">
            <div class="card" @click="randomCard(1, CardType.Support, false)">
              <div class="info random-info">
                {{ t('deckList.takeOne') }}
                <p class="card-id">{{ t(`cardTypeList.${CardType.Support}`) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <button type="button" class="button random-cancel" @click="randomDialogVisible = false">
        {{ t('cancel') }}
      </button>
    </el-dialog>

    <!-- 打乱顺序 -->
    <!-- <el-dialog
      class="dialog shuffle-dialog"
      v-model="shuffleDialogVisible"
      :close-on-click-modal="false"
      width="75.25rem"
      align-center
    >
      <h1 class="title">打乱顺序</h1>
      <div class="box shuffle-list-box">
        <div
          class="item shuffle-item"
          v-for="(card, index) in allDeck"
          :key="index"
          :class="{
            'card-item-1': card.cardType === 'MicroGain' || card.cardType === 'StrongGain',
            'card-item-2':
              card.cardType === 'MicroDiscomfort' || card.cardType === 'StrongDiscomfort',
            'card-item-3': card.cardType === 'Opportunity' || card.cardType === 'Unacceptable',
            'card-item-4': card.cardType === 'Technology',
            'card-item-5': card.cardType === 'Support'
          }"
        >
          <div class="card">
            <div class="info shuffle-info">
              <p class="card-id">{{ card.cardCnName }}</p>
              <p class="card-name">{{ card.cardName }}</p>
              <p class="card-name">- {{ index + 1 }} -</p>
            </div>
          </div>
        </div>
      </div>
      <button type="button" class="button shuffle-cancel" @click="shuffleDialogVisible = false">
        取消
      </button>
    </el-dialog> -->

    <!-- 持有卡牌帮助信息版 -->
    <InfoBoard type="left" :show-info-board="infoBoard.gameDeckList">
      <template #close-button>
        <div class="close-button">
          <a @click="infoBoard.gameDeckList = !infoBoard.gameDeckList">{{
            infoBoard.gameDeckList ? t('close') : t('deckList.deckListInfoBoardButton')
          }}</a>
        </div>
      </template>
      <template #title>
        <h1 class="title">{{ t('deckList.deckListInfoBoardTitle') }}</h1>
      </template>
      <template #content>
        <div>
          <p>{{ t('deckList.deckListInfoBoard.infoText01') }}</p>
          <hr />
          <p v-for="index in 4" :key="index">
            {{ t(`deckList.deckListInfoBoard.infoText0${index + 1}`) }}
          </p>
        </div>
      </template>
    </InfoBoard>
  </div>
</template>

<style lang="scss" scoped>
@use '@renderer/assets/styles/gamepanel/decklist';
</style>
