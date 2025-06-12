<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@renderer/stores/index'
import { playerLight, PlayerRole, type PlayerInfo, type Role } from '@renderer/types'
import { useI18n } from 'vue-i18n'
import { useSettingStore } from '@renderer/stores/modules/setting'
import router from '@renderer/plugins/router'

// 设置信息仓库
const settingStore = useSettingStore()

// i18n
const { t, locale } = useI18n()

// 角色列表
const roleList = computed(() => [
  {
    role: PlayerRole.Titan,
    name: t('roleName.titan'),
    roleSub: t('roleSub'),
    light: playerLight,
    roleImg: new URL('/images/role/titan.png', import.meta.url).href
  },
  {
    role: PlayerRole.Hunter,
    name: t('roleName.hunter'),
    roleSub: t('roleSub'),
    light: playerLight,
    roleImg: new URL('/images/role/hunter.png', import.meta.url).href
  },
  {
    role: PlayerRole.Warlock,
    name: t('roleName.warlock'),
    roleSub: t('roleSub'),
    light: playerLight,
    roleImg: new URL('/images/role/warlock.png', import.meta.url).href
  }
])

// 提示框设置
const roleDialogVisible = ref(false)

// 角色信息
const playerInfo = ref<PlayerInfo>({
  role: PlayerRole.Null,
  playerName: ''
})

// 设置角色图片
const roleImg = ref()
const setRoleImg = (role: Role): void => {
  roleImg.value = role.role
}

// 设置角色
const setRole = (role: PlayerRole): void => {
  playerInfo.value.role = role
  roleDialogVisible.value = true
}

// 设置角色信息
const setRoleInfo = (): void => {
  // 检查是否选择了角色
  if (playerInfo.value.playerName == '') {
    ElMessage({
      message: t('home.message.warningText01'),
      grouping: true,
      type: 'error'
    })
  } else {
    // 存储信息
    const userStore = useUserStore()
    userStore.initInfo(playerInfo.value)

    settingStore.setIpStr(ipInput.value)

    // 跳转游戏面板
    router.push('/room')
  }
}

// 语言切换
const switchToEn = (): void => {
  locale.value = 'en'
  settingStore.setLanguage('en')
}

const switchToZh = (): void => {
  locale.value = 'zh'
  settingStore.setLanguage('zh')
}

const switchToVex = (): void => {
  locale.value = 'vex'
  settingStore.setLanguage('vex')
}

// 服务器地址
const ipInput = ref('')

const changeUrl = (): void => {
  settingStore.setIpStr(ipInput.value)
  ElMessage({
    message: t('home.message.successText01'),
    grouping: true,
    type: 'success'
  })
}

onMounted(() => {
  playerInfo.value.playerName = ''

  ipInput.value = settingStore.ipStr
})
</script>
<template>
  <div id="home">
    <div class="role-box">
      <div class="role-img-box">
        <el-image
          v-for="item in roleList"
          :key="item.role"
          class="role-img"
          :class="{ show: roleImg === item.role }"
          :src="item.roleImg"
          fit="cover"
        ></el-image>
      </div>

      <div class="emblems">
        <div class="title">{{ t('home.title') }}</div>
        <a
          v-for="item in roleList"
          :key="item.role"
          class="emblem"
          @click="setRole(item.role)"
          @mousemove="setRoleImg(item)"
        >
          <div class="role" :class="item.role">
            <div class="description">
              <p class="name">{{ item.name }}</p>
              <p class="sub">{{ item.roleSub }}</p>
            </div>
            <div class="light">{{ item.light }}</div>
          </div>
        </a>
        <div class="list">
          <div class="link">
            <router-link :to="{ name: 'info', params: { page: 'destiny2' } }">{{
              t('home.link.gameDescription')
            }}</router-link>
            <router-link :to="{ name: 'info', params: { page: 'gameplay' } }">{{
              t('home.link.gamePlay')
            }}</router-link>
            <router-link :to="{ name: 'info', params: { page: 'update' } }">{{
              t('home.link.updateLog')
            }}</router-link>
            <router-link :to="{ name: 'info', params: { page: 'copyright' } }">{{
              t('home.link.copyright')
            }}</router-link>
          </div>
        </div>
        <div class="list">
          <div class="link">
            <a href="javascript:void(0)">{{ t('language') }}</a>
            <a
              href="javascript:void(0)"
              :class="{ langActive: locale === 'zh' }"
              @click="switchToZh"
              >简体中文</a
            >
            <a
              href="javascript:void(0)"
              :class="{ langActive: locale === 'en' }"
              @click="switchToEn"
              >English</a
            >
            <a
              href="javascript:void(0)"
              :class="{ langActive: locale === 'vex' }"
              @click="switchToVex"
              >Vex</a
            >
          </div>
        </div>
        <div class="list">
          <div class="link">
            <a href="javascript:void(0)" style="width: 27%">{{ t('server') }}</a>
            <el-input v-model="ipInput" :placeholder="t('server')" style="width: 50%"></el-input>
            <el-button type="primary" @click="changeUrl()">{{ t('confirm') }}</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 角色信息模态框 -->
    <el-dialog
      v-model="roleDialogVisible"
      class="dialog role-dialog"
      width="40rem"
      :close-on-click-modal="false"
      align-center
    >
      <h1 class="title role-title">{{ t('home.roleTitle') }}</h1>

      <div class="box role-name-box">
        <p class="title role-name-title">{{ t('home.roleNameTitle') }}</p>
        <el-input v-model="playerInfo.playerName" :placeholder="t('home.roleNameTitle')"></el-input>
      </div>

      <div class="role-confirm-box">
        <button type="button" class="button role-confirm" @click="setRoleInfo()">
          {{ t('confirm') }}
        </button>
        <button type="button" class="button role-cancel" @click="roleDialogVisible = false">
          {{ t('cancel') }}
        </button>
      </div>
    </el-dialog>

    <!-- 页脚 -->
    <div class="footer">
      <p>{{ t('home.footer', { version: settingStore.version }) }}</p>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@renderer/assets/styles/home';
</style>
