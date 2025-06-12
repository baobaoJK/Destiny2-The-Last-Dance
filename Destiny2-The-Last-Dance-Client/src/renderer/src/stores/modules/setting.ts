import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSettingStore = defineStore(
  'setting',
  () => {
    // 游戏版本
    const version = ref('1.0.1')

    // 连接地址
    const ipStr = ref('https://flask.ksamar.top')

    // 设置地址
    const setIpStr = (newIp): void => {
      ipStr.value = newIp
    }

    // 用户语言
    const lang = ref('zh')

    // 设置用户语言
    const setLanguage = (value: string): void => {
      lang.value = value
    }

    return {
      version,
      ipStr,
      setIpStr,
      lang,
      setLanguage
    }
  },
  {
    persist: true
  }
)
