// 卡牌类型名称
export enum CardType {
  MicroGain = 'MicroGain',
  StrongGain = 'StrongGain',
  Opportunity = 'Opportunity',
  MicroDiscomfort = 'MicroDiscomfort',
  StrongDiscomfort = 'StrongDiscomfort',
  Unacceptable = 'Unacceptable',
  Technology = 'Technology',
  Support = 'Support'
}

// 卡组类型名称
export enum DeckType {
  Safe = 'Safe',
  Danger = 'Danger',
  Gambit = 'Gambit',
  Luck = 'Luck',
  Devote = 'Devote'
}

// 卡牌
export interface Card {
  cardId: string
  cardType: string
  cardLabel: string
  cardLevel: number
  itemName: string
  cardName: string
  cardCnName: string
  cardDescription: string
  cardSpecial: string
  weight: number
  count: number
  allCount: number
  idea: string
  roleId: number
}
