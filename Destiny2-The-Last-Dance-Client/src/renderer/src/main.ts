import { createApp } from 'vue'
import pinia from '@renderer/stores/index'

import App from './App.vue'
import router from './plugins/router'
import i18n from './plugins/i18n'

import './assets/styles/base.scss'
import './assets/styles/element-plus.scss'

//Element Plus
import ElementPlus from 'element-plus' // 导入 element-plus
import 'element-plus/theme-chalk/index.css' // 根据 node_modules 文件夹选择对应的 theme-chalk/index.css 文件
import zhCn from 'element-plus/es/locale/lang/zh-cn' // 设置 element-plus 语言
import en from 'element-plus/es/locale/lang/en'
import { useSettingStore } from '@renderer/stores/modules/setting'

const app = createApp(App)

app.use(pinia)
app.use(i18n)

const settingStore = useSettingStore()
i18n.global.locale.value = settingStore.lang === 'zh' ? 'zh' : 'en'
app.use(ElementPlus, {
  locale: settingStore.lang === 'zh' ? zhCn : en
})
app.use(router)

app.mount('#app')
