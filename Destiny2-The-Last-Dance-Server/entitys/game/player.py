from enum import Enum
from typing import List

from entitys.game.special_conig import SpecialConfig
from entitys.sql.card import Card, DeckType, CardType
from entitys.sql.player_event import PlayerEvent


# 玩家状态
class PlayerStatus(Enum):
    Idle = "Idle"
    Draw = "Draw"

    Tribute = "Tribute" # 上贡
    Tyrant = "Tyrant" # 暴君
    Personal = "Personal" # 这不是个人恩怨
    Money = "Money" # 人为财死
    TakeOthers = "Take-Others" # 顺手牵羊
    WinOrLoss = "Win-or-Loss" # 赢或输
    LuckyNumber = "Lucky-Number" # 幸运数字
    Spy = "Spy" # 内鬼
    BySelf = "By-Self" # 噶点放心飞，出事自己背
    AlexMercer = "Alex-Mercer" # Alex-Mercer
    ThisIsTheDeal = "This-Is-The-Deal" # 你知道的，这是交易
    Preservation = "In-The-Name-of-Preservation" # 以存护之名
    BumperHarvest = "Bumper-Harvest" # 五谷丰登
    Transposition = "Transposition" # 移型换位
    BiochemicalMatrix = "Biochemical-Matrix" # 生化母体
    We = "We" # 我们，我不明白
    RiskTransformation = "Risk-Transformation" # 风险转化



class Player:
    def __init__(self, data):
        self.sid: str | None = None
        self.role: str = data['role']  # 角色
        self.role_id: int = 0  # 角色 Id
        self.is_captain: bool = False  # 是否是队长
        self.player_name: str = data['playerName']  # 玩家名称
        self.player_money: int = 0  # 玩家金钱
        self.draw_count: int = 0  # 抽卡次数
        self.player_status: PlayerStatus = PlayerStatus.Idle  # 玩家状态
        self.special_config: SpecialConfig = SpecialConfig()  # 特殊事件信息
        self.draw_card_type: DeckType | None = None  # 抽卡类型
        self.raid_chest: int = 0  # 获取隐藏箱数量
        self.devilspact: int = 0  # 恶魔契约
        self.blessing: int = 0  # 有福同享
        self.disaster: int = 0  # 有难同当
        self.zero_buy: int = 0  # 零元购
        self.give_up: bool = False  # 开摆
        self.sab_list = []  # 苦尽甘来列表
        self.deck_list = DeckListManager()  # 卡牌列表
        self.player_event_list = PlayerEventManager()  # 个人事件列表
        self.backpack = []  # 背包

    def __str__(self):
        return f"ID：{self.role_id} | 名称：{self.player_name}"

    def to_dict(self):
        return {
            "sid": self.sid,
            "role": self.role,
            "roleId": self.role_id,
            "isCaptain": self.is_captain,
            "playerName": self.player_name,
            "playerMoney": self.player_money,
            "drawCount": self.draw_count,
            "playerStatus": self.player_status.name,
            "specialConfig": self.special_config.to_dict(),
            "drawCardType": self.draw_card_type,
            "raidChest": self.raid_chest,
            "devilspact": self.devilspact,
            "blessing": self.blessing,
            "disaster": self.disaster,
            "zeroBuy": self.zero_buy,
            "giveUp": self.give_up,
            "sabList": [card.to_dict() for card in self.sab_list],
            "deckList": self.deck_list.to_dict(),
            "playerEventList": self.player_event_list.to_dict(),
            "backpack": [item.to_dict() for item in self.backpack],
            "playerAttributes": self.player_attributes
        }

    # 玩家属性
    @property
    def player_attributes(self):
        return {
            "market": self.market,  # 未来市场
            "profiteer": self.profiteer,  # 纨绔子弟
            "shopClosed": self.shop_closed,  # 静水监狱
            "gambler": self.gambler,  # 赌徒
            "deckClosed": self.deck_closed,  # 戒赌
            "compensate": self.compensate,  # 免死金牌
            "selfless": self.selfless,  # 舍己为人
            "torture": self.torture,  # 苦肉计
            "isRandom": self.is_random,  # 不，你不能
            "program": self.program,  # 卡牌回收计划
            "stargazing": self.stargazing,  # 观星
            "noDeal": self.no_deal,  # 不吃这套
            "noBuddy": self.no_buddy,  # 不是哥们
            "thirteen": self.thirteen,  # 十三幺
            "counteract": self.counteract,  # 免死金牌与帝王禁令
            "difficult": self.difficult,  # 重重难关
            "easy": self.easy,  # 这不是很简单吗
            "promotions": self.promotions,  # 商店促销
            "blood": self.blood,  # 堕落之血
            "levelUp": self.level_up # 等级提升
        }

    # 未来市场
    @property
    def market(self):
        return any(item.card_name == "Future's-Market" for item in self.deck_list[CardType.Technology.name])

    # 纨绔子弟
    @property
    def profiteer(self):
        return any(item.card_name == "Reicher-Playboy" for item in self.deck_list[CardType.StrongDiscomfort.name])

    # 静水监狱
    @property
    def shop_closed(self):
        return any(item.card_name == "Stillwater-Prison" for item in self.deck_list[CardType.Unacceptable.name])

    # 赌徒
    @property
    def gambler(self):
        return any(item.card_name == "Gambler" for item in self.deck_list[CardType.Technology.name])

    # 戒赌
    @property
    def deck_closed(self):
        return any(item.card_name == "Quit-Gambling" for item in self.deck_list[CardType.Unacceptable.name])

    # 免死金牌
    @property
    def compensate(self):
        return any(item.card_name == 'The-Medallion' for item in self.deck_list[CardType.Opportunity.name])

    # 舍己为人
    @property
    def selfless(self):
        return any(item.card_name == 'Altruism' for item in self.deck_list[CardType.Unacceptable.name])

    # 苦肉计
    @property
    def torture(self):
        return any(item.card_name == 'The-Self-Torture-Scheme' for item in self.deck_list[CardType.Technology.name])

    # 不，你不能
    @property
    def is_random(self):
        return any(item.card_name == 'You-Cant' for item in self.deck_list[CardType.Technology.name])

    # 卡牌回收计划
    @property
    def program(self):
        return any(item.card_name == 'Card-Recycling-Program' for item in self.deck_list[CardType.Technology.name])

    # 观星
    @property
    def stargazing(self):
        return any(item.card_name == 'Stargazing' for item in self.deck_list[CardType.Technology.name])

    # 不吃这套
    @property
    def no_deal(self):
        return any(item.card_name == 'I-Wont-Eat-This' for item in self.deck_list[CardType.Technology.name])

    # 不是哥们
    @property
    def no_buddy(self):
        return any(item.card_name == 'No-Buddy' for item in self.deck_list[CardType.Technology.name])

    # 十三幺
    @property
    def thirteen(self):
        return any(item.card_name == 'Thirteen-Orphans' for item in self.deck_list[CardType.Technology.name])

    # 免死金牌和帝王禁令
    @property
    def counteract(self):
        return (any(item.card_name == 'The-Medallion' for item in self.deck_list[CardType.Opportunity.name])
                and
                any(item.card_name == 'Imperial-Ban' for item in self.deck_list[CardType.Unacceptable.name]))

    # 重重难关
    @property
    def difficult(self):
        return any(item.card_name == 'Many-Difficulties' for item in self.deck_list[CardType.Unacceptable.name])

    # 这不是很简单吗
    @property
    def easy(self):
        return any(item.card_name == 'Easy' for item in self.deck_list[CardType.Opportunity.name])

    # 商店促销
    @property
    def promotions(self):
        return any(item.card_name == 'Store-Promotions' for item in self.deck_list[CardType.Technology.name])

    # 堕落之血
    @property
    def blood(self):
        return any(item.card_name == 'Corrupted-Blood' for item in self.deck_list[CardType.Unacceptable.name])

    # 等级提升
    @property
    def level_up(self):
        return any(item.card_name == 'Level-Up' for item in self.deck_list[CardType.Technology.name])

# 玩家管理
class PlayerManager:
    def __init__(self):
        self.players: dict[str, Player] = {}

    def add_player(self, key: str, player: Player) -> bool:
        """添加玩家，若 key 已存在则返回 False"""
        if key in self.players:
            return False
        self.players[key] = player
        return True

    def remove_player(self, key: str) -> bool:
        """移除玩家"""
        return self.players.pop(key, None) is not None

    def get_player(self, key: str) -> Player | None:
        """获取玩家，如果不存在返回 None"""
        return self.players.get(key)

    def get_player_by_id(self, player_id: int) -> Player | None:
        """通过 player_id 获取玩家，如果不存在返回 None"""
        for player in self.players.values():
            if player.role_id == player_id:
                return player

    def update_player(self, key: str, player: Player) -> bool:
        """更新玩家信息"""
        if key not in self.players:
            return False
        self.players[key] = player
        return True

    def has_player(self, key: str) -> bool:
        """判断是否存在该玩家"""
        return key in self.players

    def all_players(self) -> list[Player]:
        """返回所有玩家对象"""
        return list(self.players.values())

    def clear(self):
        """清空所有玩家"""
        self.players.clear()

    def to_dict(self):
        """输出玩家信息"""
        return {player_id: player.to_dict() for player_id, player in self.players.items()}

# 玩家卡牌管理
class DeckListManager:
    def __init__(self):
        self.deck_list: dict[CardType.name, list[Card]] = {
            CardType.MicroGain.name: [],
            CardType.StrongGain.name: [],
            CardType.Opportunity.name: [],
            CardType.MicroDiscomfort.name: [],
            CardType.StrongDiscomfort.name: [],
            CardType.Unacceptable.name: [],
            CardType.Technology.name: [],
            CardType.Support.name: []
        }

    def __getitem__(self, item):
        return self.deck_list[item]

    def add_card(self, card: Card) -> bool:
        """添加卡牌，若卡牌已存在则返回 False"""
        if card in self.deck_list[card.card_type]:
            return False
        self.deck_list[card.card_type].append(card)
        return True

    def remove_card(self, card: Card) -> bool:
        """移除卡牌"""
        return self.deck_list[card.card_type].remove(card) is not None

    def get_card(self, card: Card) -> Card | None:
        """获取卡牌，如果不存在返回 None"""
        return next((item for item in self.deck_list[card.card_type] if item == card), None)

    def get_card_by_name(self, card_type: CardType, card_name: str) -> Card | None:
        """通过卡牌名称获取卡牌，如果不存在返回 None"""
        return next((item for item in self.deck_list[card_type] if item.card_name == card_name), None)

    def get_card_count(self):
        """获取卡牌数量"""
        card_count = 0
        for card_type, card_list in self.deck_list.items():
            card_count += len(card_list)
        return card_count

    def has_card(self, card: Card) -> bool:
        """判断是否存在该卡牌"""
        return card in self.deck_list[card.card_type]

    def clear(self):
        """清空所有卡牌"""
        self.deck_list = {
            CardType.MicroGain.name: [],
            CardType.StrongGain.name: [],
            CardType.Opportunity.name: [],
            CardType.MicroDiscomfort.name: [],
            CardType.StrongDiscomfort.name: [],
            CardType.Unacceptable.name: [],
            CardType.Technology.name: [],
            CardType.Support.name: []
        }

    def get_card_type_list(self, card_type: CardType) -> list[Card]:
        """获取卡牌类型列表"""
        return self.deck_list[card_type]

    def set_card_type_list(self, card_type: CardType, card_list: list[Card]):
        """设置卡牌类型列表"""
        self.deck_list[card_type.name] = card_list

    def items(self):
        """返回 (k, v)"""
        return self.deck_list.items()

    def __iter__(self):
        """支持直接 for 循环"""
        return iter(self.deck_list.items())

    def to_dict(self):
        """输出卡牌信息"""
        return {card_type: [card.to_dict() for card in card_list] for card_type, card_list in self.deck_list.items()}

# 玩家个人事件管理
class PlayerEventManager:
    def __init__(self):
        self.player_event_list: List[PlayerEvent] = []

    def add_event(self, player_event: PlayerEvent):
        """添加玩家事件"""
        self.player_event_list.append(player_event)

    def remove_event(self, player_event: PlayerEvent):
        """移除玩家事件"""
        self.player_event_list.remove(player_event)

    def get_event(self, event_index) -> PlayerEvent:
        """获取玩家事件，如果不存在返回 None"""
        return self.player_event_list[event_index]

    def clear(self):
        """清空所有事件"""
        self.player_event_list.clear()

    def to_dict(self):
        """输出玩家事件信息"""
        return [player_event.to_dict() for player_event in self.player_event_list]