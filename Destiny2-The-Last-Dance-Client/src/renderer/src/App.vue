<script setup lang="ts">
// import { storeToRefs } from 'pinia'
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
// import { useUserStore } from './stores'
// import { getSocket } from './utils/socket'

const { t } = useI18n()

const title = computed((): string => {
  document.title = t('title')
  return t('title')
})

watch(title, (newTitle) => {
  document.title = newTitle
})

onMounted(() => {
  // const socket = getSocket()
  // 判断客户端关闭
  window.electronAPI?.onPrepareClose(() => {
    window.electronAPI.notifyCanClose()
    // const { roomId, playerName } = storeToRefs(useUserStore())
    // if (roomId.value !== '') {
    //   // 退出房间
    //   socket?.emit('disconnect', {
    //     roomId: roomId.value,
    //     playerName: playerName.value
    //   })
    // }
  })
})
onUnmounted(() => {
  window.electron.ipcRenderer.removeAllListeners('prepare-window-close')
})
</script>

<template>
  <RouterView />
</template>

<style lang="scss"></style>
