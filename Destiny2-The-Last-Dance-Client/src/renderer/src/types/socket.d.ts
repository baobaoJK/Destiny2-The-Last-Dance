export interface SocketData {
  status: string
  eventType: string
  message: string
  messageType: string
  messageData: Record<string, unknown>
  data: obejct | undefined
  to: string | undefined
}
