<script lang="ts" setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

// i18n
const { t } = useI18n()

// 游戏开始模态框
const gameDialogVisible = ref(false)
// 使用 import.meta.url 动态导入图片
const gameLogo = new URL('/images/Raid.png', import.meta.url).href

// DoroButton
// const openOrClose = ref(false)
// const doroButton = (): void => {
//   if (!openOrClose.value) {
//     window.electron.ipcRenderer.send('SHOW_DORO')
//     openOrClose.value = true
//   } else {
//     window.electron.ipcRenderer.send('CLOSE_DORO')
//     openOrClose.value = false
//   }
// }
</script>

<template>
  <div id="index">
    <div class="background"></div>
    <a class="start-button" @click="gameDialogVisible = true">{{ t('index.gameStart') }}</a>

    <!-- 游戏检测 -->
    <el-dialog
      v-model="gameDialogVisible"
      class="dialog game-dialog"
      :close-on-click-modal="false"
      align-center
    >
      <img class="game-logo" :src="gameLogo" alt="Logo" />
      <p class="title game-title">{{ t('index.gameTitle') }}</p>
      <p class="text game-config">{{ t('index.gameConfig') }}</p>
      <p class="text game-time">{{ t('index.gameTime') }}</p>
      <div class="links">
        <router-link class="link" :to="{ name: 'info', params: { page: 'destiny2' } }">{{
          t('index.gameDescription')
        }}</router-link>
        <router-link class="link" :to="{ name: 'info', params: { page: 'gameplay' } }">{{
          t('index.gamePlay')
        }}</router-link>
      </div>
      <router-link class="button game-confirm" to="home">{{ t('index.gameStart') }}</router-link>
      <!-- <el-button @click="doroButton">Doro</el-button> -->
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
@use '@renderer/assets/styles/index';
</style>
