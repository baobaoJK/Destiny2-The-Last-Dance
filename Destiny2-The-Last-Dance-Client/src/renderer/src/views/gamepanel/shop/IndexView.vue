<script lang="ts" setup>
import { useUserStore } from '@renderer/stores'
import { Card, InfoBoardConfig, PlayerConfig, RoomConfig, ShopConfig } from '@renderer/types'
import { ShopItem } from '@renderer/types/shop'
import { SocketData } from '@renderer/types/socket'
import { productionBaseURL, lightImg } from '@renderer/utils'
import { getSocket } from '@renderer/utils/socket'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import { Socket } from 'socket.io-client'
import { computed, onMounted, Ref, ref } from 'vue'
import { useI18n } from 'vue-i18n'
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
const playerConfig: Ref<PlayerConfig> = computed(
  () => roomConfig?.value?.playerList[playerName.value]
)
const shopConfig: Ref<ShopConfig> = computed(() => roomConfig?.value?.shopConfig)

// i18n
const { t } = useI18n()

// socekt
let socket: Socket | null

// 用户信息
const { playerName } = storeToRefs(useUserStore())

// 背包下标
const backpackIndex = ref(0)

// 圣水提示框
const waterDialogVisible = ref(false)
const waterDeckList = ref<Card[]>([])

// 提示框
const tipsRef = ref()
const tooltipShow = ref(false)
const tooltipConfig = ref({
  itemName: '',
  itemKind: '',
  itemRarity: '',
  itemDescription: '',
  sellMoney: 0,
  itemCount: 0,
  tipType: ''
})

// 显示提示框
const showTooltip = (item: Card | ShopItem, tipType: string): void => {
  tooltipShow.value = true

  if (tipType === 'deleteCard') {
    tooltipConfig.value.itemName = t(`cardList.${item.itemName}.name`)
    tooltipConfig.value.itemKind = t('cards')
    tooltipConfig.value.itemRarity = t('cardTypeList.MicroDiscomfort')
    tooltipConfig.value.itemDescription = t(`cardList.${item.itemName}.description`)
  } else if ('cnName' in item) {
    tooltipConfig.value.itemName = t(`item.${item.itemName}.name`)
    tooltipConfig.value.itemKind = t(`itemType.${item.kind}`)
    tooltipConfig.value.itemRarity = t(`rarityType.${item.rarity}`)
    tooltipConfig.value.itemDescription = t(`item.${item.itemName}.description`)
    tooltipConfig.value.sellMoney = playerConfig?.value?.zeroBuy > 0 ? 0 : item.sell
    tooltipConfig.value.itemCount = item.count
    tooltipConfig.value.tipType = tipType

    if (playerConfig?.value?.playerAttributes.promotions) {
      tooltipConfig.value.sellMoney = tooltipConfig.value.sellMoney / 2
    }

    if (playerConfig?.value?.playerAttributes.profiteer) {
      tooltipConfig.value.sellMoney = tooltipConfig.value.sellMoney + 1
    }
  }
  tipsRef.value.setToolTips(item)
}

// 关闭提示框
const hideTooltip = (): void => {
  tooltipShow.value = false
}

// 获取物品图片
const getItemImg = (item: ShopItem): string => {
  let imageStr = ''
  if (item.typeName === 'weapons') {
    imageStr = `/images/shop/exotic/weapons/${item.cnName}.jpg`
  } else if (item.typeName === 'armor') {
    imageStr = `/images/shop/exotic/${item.role}/${item.itemName}.jpg`
  } else if (item.typeName === 'water' || item.typeName === 'drawCount') {
    imageStr = `/images/shop/${item.itemName}.jpg`
  } else if (item.typeName === 'weapon') {
    imageStr = `/images/shop/weapons/${item.itemName}.jpg`
  }

  if (import.meta.env.MODE === 'development') {
    return new URL(imageStr, import.meta.url).href
  } else {
    return productionBaseURL + imageStr
  }
}

// 购买物品
const buyItem = (typeList: string, index: number): void => {
  setWebLoading(true)
  socket?.emit('buyItem', {
    roomId: roomConfig?.value?.roomId,
    playerName: playerName.value,
    typeList: typeList,
    itemIndex: index
  })
}

// 使用圣水
const useItem = (index: number): void => {
  setWebLoading(true)
  socket?.emit('useItem', {
    roomId: roomConfig?.value.roomId,
    playerName: playerName.value,
    backpackIndex: index
  })
  backpackIndex.value = index
}

// 删除卡牌
const deleteCardItem = (card: Card, index: number): void => {
  setWebLoading(true)
  socket?.emit('deleteCardItem', {
    roomId: roomConfig?.value.roomId,
    playerName: playerName.value,
    cardType: card.cardType,
    cardIndex: index,
    backpackIndex: backpackIndex.value
  })
}

// 刷新商店按钮
const refreshShop = (): void => {
  setWebLoading(true)
  socket?.emit('refreshShop', {
    roomId: roomConfig?.value.roomId
  })
}

// 开启商店
const openShop = (): void => {
  setWebLoading(true)
  socket?.emit('openShop', {
    roomId: roomConfig?.value.roomId,
    playerName: playerName.value
  })
}

// 初始化
onMounted(() => {
  socket = getSocket()

  // 圣水列表显示
  socket?.off('showWaterDeckList')
  socket?.on('showWaterDeckList', (socketData: SocketData) => {
    waterDeckList.value = socketData.data.deckList
    waterDialogVisible.value = true
    setWebLoading(false)
  })

  // 圣水列表隐藏
  socket?.off('hideWaterDeckList')
  socket?.on('hideWaterDeckList', () => {
    waterDialogVisible.value = false
    setWebLoading(false)
  })

  let messageStr = ''

  // 净水监狱
  if (playerConfig?.value?.playerAttributes?.shopClosed) {
    messageStr = 'shop.message.errorText07'
  }
  // 价格检测
  if (playerConfig?.value?.playerAttributes?.profiteer) {
    messageStr = 'shop.message.errorText08'
  }
  // 恶魔契约
  if (playerConfig?.value?.devilspact != 0) {
    messageStr = 'shop.message.errorText09'
  }
  // 未来市场
  if (playerConfig?.value?.playerAttributes?.market) {
    messageStr = 'shop.message.errorText10'
  }
  // 开摆
  if (playerConfig?.value?.giveUp) {
    messageStr = 'shop.message.errorText11'
  }
  if (messageStr != '') {
    ElMessage({
      message: t(messageStr),
      type: 'warning',
      grouping: true,
      duration: 0,
      showClose: true
    })
  }
})
</script>
<template>
  <div id="shop" @mousemove="tipsRef?.moveTooltip($event)">
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
          </div>
          <hr />
          <div class="text">
            <p>{{ t('shop.inventory', { count: tooltipConfig.itemCount }) }}</p>
          </div>
        </div>
        <div class="line"></div>
        <div v-if="tooltipConfig.tipType !== 'backpack'" class="monetary">
          <div class="name">
            <img class="light" :src="lightImg" alt="light.png" />
            <p>{{ t('light') }}</p>
          </div>
          <div class="info">
            <p class="text">
              <span class="money">{{ playerConfig?.playerMoney }}</span> /
              <span class="sell">{{ tooltipConfig.sellMoney }}</span>
            </p>
          </div>
        </div>
      </template>
    </TipsView>

    <div class="shop-list">
      <div class="shop-top">
        <h1 class="shop-title">{{ t('shop.title') }}</h1>
        <div class="shop-options">
          <button
            v-if="roomConfig?.roomOwner == playerName"
            class="button refresh-button"
            @click="refreshShop"
          >
            {{ t('shop.refreshShop') }}
          </button>
          <p id="refresh-count">
            {{ t('shop.freeRefreshShopCount', { count: shopConfig?.refreshCount }) }}
          </p>
          <p id="pay-count">
            {{ t('shop.payRefreshShopCount', { money: shopConfig?.refreshMoney / 6 }) }}
          </p>
        </div>
        <hr class="shop-line" />
      </div>

      <div class="shop-main">
        <!-- 售卖栏 -->
        <div class="shop-sell-list">
          <div v-if="shopConfig?.itemList.length === 0" class="item-list">
            <h2 class="shop-title">{{ t('shop.itemBar') }}</h2>
            <hr class="shop-line" />
            <div class="item-list">
              <h1 class="tips">{{ t('shop.sold') }}</h1>
            </div>
          </div>
          <div v-else class="item-list">
            <h2 class="shop-title">{{ t('shop.itemBar') }}</h2>
            <hr class="shop-line" />
            <div class="item-list">
              <div
                v-for="(item, index) in shopConfig?.itemList"
                :key="index"
                :style="{ 'background-image': `url(${getItemImg(item)})` }"
                class="item"
                @mousemove="showTooltip(item, 'item')"
                @mouseout="hideTooltip()"
                @click="buyItem('itemList', index)"
              ></div>
            </div>
          </div>

          <div v-if="shopConfig?.weaponList.length === 0" class="weapon-list">
            <h2 class="shop-title">{{ t('shop.weaponItemBar') }}</h2>
            <hr class="shop-line" />
            <div class="item-list">
              <h1 class="tips">{{ t('shop.sold') }}</h1>
            </div>
          </div>
          <div v-else class="weapon-list">
            <h2 class="shop-title">{{ t('shop.weaponItemBar') }}</h2>
            <hr class="shop-line" />
            <div class="item-list">
              <div
                v-for="(item, index) in shopConfig?.weaponList"
                :key="index"
                :style="{ 'background-image': `url(${getItemImg(item)})` }"
                class="item"
                @mousemove="showTooltip(item, 'item')"
                @mouseout="hideTooltip()"
                @click="buyItem('weaponList', index)"
              ></div>
            </div>
          </div>

          <div v-if="shopConfig?.exoticList.length === 0" class="exotic-list">
            <h2 class="shop-title">{{ t('shop.exoticItemBar') }}</h2>
            <hr class="shop-line" />
            <div class="item-list">
              <h1 class="tips">{{ t('shop.sold') }}</h1>
            </div>
          </div>
          <div v-else class="exotic-list">
            <h2 class="shop-title">{{ t('shop.exoticItemBar') }}</h2>
            <hr class="shop-line" />
            <div class="item-list">
              <div
                v-for="(item, index) in shopConfig?.exoticList"
                :key="index"
                :style="{
                  'background-image': `url('${getItemImg(item)}')`
                }"
                class="item"
                @mousemove="showTooltip(item, 'item')"
                @mouseout="hideTooltip()"
                @click="buyItem('exoticList', index)"
              ></div>
            </div>
          </div>
        </div>

        <!-- 背包 -->
        <div class="backpack">
          <h1 class="backpack-title">{{ t('shop.backpack') }}</h1>
          <hr class="backpack-line" />
          <div v-if="playerConfig?.backpack.length === 0" class="item-list">
            <h1>{{ t('shop.backpackIsEmpty') }}</h1>
          </div>
          <div v-else class="item-list">
            <div
              v-for="(item, index) in playerConfig?.backpack"
              :key="index"
              :style="{ 'background-image': `url('${getItemImg(item)}')` }"
              class="item"
              @mousemove="showTooltip(item, 'backpack')"
              @mouseout="hideTooltip()"
              @click="useItem(index)"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 圣水提示框 -->
    <el-dialog
      v-model="waterDialogVisible"
      class="card-dialog"
      :close-on-click-modal="false"
      width="79.25rem"
      align-center
    >
      <h1 class="title">{{ t('shop.selectDeleteCard') }}</h1>
      <div class="card-list-box">
        <div
          v-for="(card, index) in waterDeckList"
          :key="index"
          :class="{
            'card-item-2':
              card.cardType === 'MicroDiscomfort' || card.cardType === 'StrongDiscomfort',
            'card-item-3': card.cardType === 'Unacceptable',
            'card-item-4': card.cardType === 'Technology'
          }"
          class="card-item"
          @mousemove="showTooltip(card, 'deleteCard')"
          @mouseout="hideTooltip()"
          @click="deleteCardItem(card, index)"
        >
          <div class="card">
            <div class="card-info">
              <p class="card-id">{{ card.cardCnName }}</p>
              <p class="card-name">{{ card.cardName }}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="card-confirm-box">
        <button type="button" class="button card-cancel" @click="waterDialogVisible = false">
          {{ t('cancel') }}
        </button>
      </div>
    </el-dialog>

    <!-- 商店关闭模态框 -->
    <div
      v-if="playerConfig?.playerAttributes.shopClosed || playerConfig?.giveUp"
      class="shop-closed"
    >
      <button
        v-if="playerConfig?.playerAttributes.shopClosed"
        class="button open-shop"
        @click="openShop"
      >
        {{ t('shop.openShop') }}
      </button>

      <button v-if="playerConfig?.isCaptain" class="button refresh-button" @click="refreshShop">
        {{ t('shop.refreshShop') }}
      </button>
    </div>

    <!-- 商店信息版 -->
    <InfoBoard type="right" :show-info-board="infoBoard.gameShop">
      <template #close-button>
        <div class="close-button">
          <a @click="infoBoard.gameShop = !infoBoard.gameShop">{{
            infoBoard.gameShop ? t('close') : t('shop.shopInfoBoardButton')
          }}</a>
        </div>
      </template>
      <template #title>
        <h1 class="title">{{ t('shop.shopInfoBoardTitle') }}</h1>
      </template>
      <template #content>
        <div>
          <p v-for="index in 3" :key="index">
            {{ t(`shop.shopInfoBoard.infoText0${index}`) }}
          </p>
          <hr />
          <p v-for="index in 6" :key="index">
            {{ t(`shop.shopInfoBoard.infoText0${index + 3}`) }}
          </p>
          <hr />
          <p v-for="index in 6" :key="index">
            {{ t(`shop.shopInfoBoard.infoText${index + 9 < 10 ? '0' + (index + 9) : index + 9}`) }}
          </p>
        </div>
      </template>
    </InfoBoard>
  </div>
</template>
<style lang="scss" scoped>
@use '@renderer/assets/styles/gamepanel/shop';
</style>
