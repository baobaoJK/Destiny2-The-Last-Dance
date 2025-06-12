export interface InfoBoardConfig {
  gameMap: boolean
  gamePlay: boolean
  gameChallenge: boolean
  gameDeck: boolean
  gameDeckList: boolean
  gamePlayerEvent: boolean
  gameGlobalEvent: boolean
  gameShop: boolean
}

export const createDefaultInfoBoardConfig = (): InfoBoardConfig => ({
  gameMap: false,
  gamePlay: true,
  gameChallenge: true,
  gameDeck: false,
  gameDeckList: false,
  gamePlayerEvent: false,
  gameGlobalEvent: false,
  gameShop: false
})
