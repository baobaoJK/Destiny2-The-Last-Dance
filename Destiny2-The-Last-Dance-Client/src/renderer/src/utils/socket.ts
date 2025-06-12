// src/services/socket.ts
import { io, Socket } from 'socket.io-client'
import router from '@renderer/plugins/router'
import { useUserStore } from '@renderer/stores'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import { useSettingStore } from '@renderer/stores/modules/setting'

// const baseURL = 'http://192.168.1.18:9527/' // 后端服务地址
// const baseURL = 'http://192.168.3.65:9527/' // 后端服务地址
// const baseURL = 'https://flask.ksamar.top/' // 后端服务地址

let socket: Socket | null = null

export const getSocket = (): Socket => {
  const userStore = useUserStore()
  const { ipStr, version } = storeToRefs(useSettingStore())
  const baseURL = ipStr.value

  if (!socket) {
    console.log('[Socket] 创建连接...')
    socket = io(baseURL, {
      transports: ['websocket'], // 优先使用 websocket（防止 CSP 限制 polling）
      reconnection: true,
      reconnectionAttempts: 5,
      timeout: 5000,
      auth: {
        token: 'hqsw-' + version.value,
        version: version.value
      }
    })

    // 连接成功
    socket.off('connect')
    socket.on('connect', () => {
      console.log('[Socket] 已连接:', socket?.id)
      console.log(baseURL)
    })

    // 断开连接
    socket.off('disconnect')
    socket.on('disconnect', (reason) => {
      console.warn('[Socket] 断开连接:', reason)
      router.push('/room')
      userStore.setRoomId('')
      ElMessage({
        message: '连接已断开',
        type: 'warning',
        grouping: true
      })
    })

    // 错误
    socket.off('connect_error')
    socket.on('connect_error', (err) => {
      const userStore = useUserStore()
      const { ipStr } = storeToRefs(useSettingStore())
      const baseURL = ipStr.value

      console.error('[Socket] 连接错误:', err.message)
      console.log(baseURL)
      router.push('/home')
      userStore.setRoomId('')
      ElMessage({
        message: '连接错误',
        type: 'error',
        grouping: true
      })
    })
  }

  return socket
}

// 关闭连接
export const disconnectSocket = (): void => {
  if (socket) {
    console.log('Socket 关闭')
    socket.disconnect()
    socket = null
  }
}
