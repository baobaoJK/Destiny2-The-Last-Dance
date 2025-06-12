import { Card } from '@renderer/types'
import { ref } from 'vue'
import { computed } from 'vue'

export const productionBaseURL = `${import.meta.env.BASE_URL}`

// 货币图片
export const lightImg = computed(() => {
  if (import.meta.env.MODE === 'development') {
    return new URL('/images/light.png', import.meta.url).href
  } else {
    return productionBaseURL + 'images/light.png'
  }
})

// 卡片图片
export const cardImg = computed(() => {
  if (import.meta.env.MODE === 'development') {
    return new URL('/images/card.png', import.meta.url).href
  } else {
    return productionBaseURL + 'images/card.png'
  }
})

// 获取突袭地图图片
export const getRaidMapImg = (mapName: string): string => {
  if (import.meta.env.MODE === 'development') {
    return new URL('/images/maps/raid/' + mapName + '.jpg', import.meta.url).href
  } else {
    return productionBaseURL + 'images/maps/raid/' + mapName + '.jpg'
  }
}

// 打乱
export const shuffle = (array: Card[]): Card[] => {
  const res = ref<Array<Card>>([])
  let random
  while (array.length > 0) {
    random = Math.floor(Math.random() * array.length)
    res.value.push(array[random])
    array.splice(random, 1)
  }
  return res.value
}
