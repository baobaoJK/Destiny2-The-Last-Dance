import { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    electron: ElectronAPI
    api: unknown
    electronAPI: {
      onPrepareClose: (callback: () => void) => void
      notifyCanClose: () => void
    }
  }
}
