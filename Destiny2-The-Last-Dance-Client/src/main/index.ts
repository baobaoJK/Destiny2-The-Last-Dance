import { app, shell, BrowserWindow, ipcMain, screen } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'
import { Menu, globalShortcut } from 'electron'
function createWindow(): void {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    minWidth: 1616,
    minHeight: 939,
    width: 1616,
    height: 939,
    // fullscreen: true,
    show: false,
    icon: icon,
    autoHideMenuBar: true,
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  })
  // 移除默认菜单栏
  Menu.setApplicationMenu(null)

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // 打开开发者工具（控制台）
  // mainWindow.webContents.openDevTools()

  // 如果你希望按 F12 快捷键打开控制台
  mainWindow.webContents.on('devtools-opened', () => {
    console.log('DevTools 已经打开')
  })

  mainWindow.on('close', (e) => {
    // 先通知渲染进程准备关闭
    mainWindow.webContents.send('prepare-window-close')

    // 阻止默认关闭行为
    e.preventDefault()

    // 等待渲染进程完成清理
    ipcMain.once('can-close-window', () => {
      mainWindow.destroy()
    })
  })

  mainWindow.on('closed', () => {
    doroWindowSet.forEach((win) => {
      if (!win.isDestroyed()) win.close()
    })
    doroWindowSet.clear()
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // 注册 F11 切换全屏
  globalShortcut.register('F11', () => {
    const focusedWindow = BrowserWindow.getFocusedWindow()
    if (focusedWindow) {
      focusedWindow.setFullScreen(!focusedWindow.isFullScreen())
    }
  })

  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron')

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // IPC test
  ipcMain.on('ping', () => console.log('pong'))

  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })

  // 在应用退出时强制清理
  app.on('before-quit', () => {
    doroWindowSet.forEach((win) => {
      if (!win.isDestroyed()) win.destroy() // 更彻底的关闭方式
    })
  })

  // 处理窗口意外崩溃
  doroWindowSet.forEach((win) => {
    win.webContents.on('render-process-gone', () => {
      win.destroy()
      doroWindowSet.delete(win)
    })
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('will-quit', () => {
  globalShortcut.unregisterAll()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.

// Doro
let doroWindow: BrowserWindow
const doroWindowSet: Set<BrowserWindow> = new Set()

function createDoroWindow(): BrowserWindow {
  doroWindow = new BrowserWindow({
    width: 164,
    height: 142,
    transparent: true,
    frame: false,
    hasShadow: false,
    thickFrame: false,
    resizable: false,
    backgroundColor: '#00FFFFFF',
    alwaysOnTop: true,
    skipTaskbar: true,
    focusable: false, // 不抢焦点
    webPreferences: { nodeIntegration: true, backgroundThrottling: false }
  })

  doroWindow.setIgnoreMouseEvents(true)
  doroWindow.setAlwaysOnTop(true, 'screen-saver')

  doroWindow.loadFile(join(__dirname, '../../src/renderer/public/doro.html'))

  doroWindow.on('ready-to-show', () => {
    if (process.platform === 'win32') {
      // Windows边框消除魔法
      const bounds = doroWindow.getBounds()
      doroWindow.setBounds({ ...bounds, width: bounds.width + 1, height: bounds.height + 1 })
      setTimeout(() => doroWindow.setBounds(bounds), 50)
    }
    // 主进程
    if (process.platform === 'win32') {
      app.commandLine.appendSwitch('disable-windows10-custom-titlebar')
      app.commandLine.appendSwitch('disable-features', 'Windows10CustomTitlebar')
    }
  })

  // 让窗口随机移动（动态效果）
  moveWindowWithBounce(doroWindow)

  doroWindow.on('closed', () => {
    doroWindowSet.delete(doroWindow)
  })

  return doroWindow
}

function moveWindowWithBounce(window: Electron.BrowserWindow): void {
  const screenSize = screen.getPrimaryDisplay().workAreaSize
  const windowSize = window.getSize()

  // 初始随机位置（确保在屏幕范围内）
  let x = Math.floor(Math.random() * (screenSize.width - windowSize[0]))
  let y = Math.floor(Math.random() * (screenSize.height - windowSize[1]))

  // 初始随机速度（方向和速度）
  let dx = (Math.random() > 0.5 ? 1 : -1) * (2 + Math.random() * 3)
  let dy = (Math.random() > 0.5 ? 1 : -1) * (2 + Math.random() * 3)

  window.setPosition(x, y)

  const moveInterval = setInterval(() => {
    // 更新位置
    x += dx
    y += dy

    // 检查是否碰到左右边缘
    if (x <= 0 || x + windowSize[0] >= screenSize.width) {
      dx = -dx * (0.9 + Math.random() * 0.2) // 反转x方向并添加随机速度变化
      x = Math.max(0, Math.min(x, screenSize.width - windowSize[0])) // 确保不会卡在边缘
    }

    // 检查是否碰到上下边缘
    if (y <= 0 || y + windowSize[1] >= screenSize.height) {
      dy = -dy * (0.9 + Math.random() * 0.2) // 反转y方向并添加随机速度变化
      y = Math.max(0, Math.min(y, screenSize.height - windowSize[1])) // 确保不会卡在边缘
    }

    window.setPosition(Math.round(x), Math.round(y))
  }, 16) // ~60fps (1000ms/60 ≈ 16ms)

  window.on('closed', () => clearInterval(moveInterval))
}
ipcMain.on('SHOW_DORO', () => {
  // console.log(event)

  for (let i = 0; i < 10; i++) {
    doroWindowSet.add(createDoroWindow())
  }
})

ipcMain.on('CLOSE_DORO', () => {
  doroWindowSet.forEach((win) => {
    if (!win.isDestroyed()) win.close()
  })
  doroWindowSet.clear()
})
