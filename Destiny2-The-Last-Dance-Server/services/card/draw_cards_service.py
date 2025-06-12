from typing import List

from entitys.game.player import Player
from entitys.game.room import Room
from entitys.sql.card import CardType, Card
from utils import debug, shuffle_list
from utils.tools.lottery import lottery_by_count

class DrawCardsService:

    # 检测函数
    # -----------------------------------------------------------------------------
    # 检查 卡牌 是否在玩家卡牌列表中
    # 是 返回 True
    # 否 返回 False
    @staticmethod
    def check_card_in_player_deck_list(player: Player, item: Card) -> bool:
        for card_type, card_list in player.deck_list:
            for card in card_list:
                if item.card_name == card.card_name:
                    return True
        return False

    # 检测玩家能抽取的卡牌数量
    @staticmethod
    def check_drawable(player_counts: dict, requirements: dict[CardType, int]) -> bool:
        return all(player_counts[ct.name] >= count for ct, count in requirements.items())

    # ------------------------------------------------------------------------------

    # 构建函数
    # ------------------------------------------------------------------------------
    # 构建玩家卡牌列表
    def build_deck(self, room: Room, player: Player, card_level_plan: dict[CardType, list[int]]):
        deck = []
        for card_type, level_list in card_level_plan.items():
            cards = self.get_deck_list_tag_level_list(room, player, card_type, level_list)
            deck += cards
        return deck

    # 获取 稳妥起见 列表 6张微弱增益 1张强大增益 4张微弱不适 1张特殊卡牌
    def build_safe_deck_list(self, room: Room, player: Player):
        card_list = room.game_config.card_list
        # 获取玩家还能抽取的卡牌列表数量
        player_can_draw_count = self.get_player_can_draw_count(player, card_list)

        requirements = {
            CardType.MicroGain: 6,
            CardType.StrongGain: 1,
            CardType.MicroDiscomfort: 4,
            CardType.Technology: 1
        }

        if not self.check_drawable(player_can_draw_count, requirements):
            return []

        card_plan = {
            CardType.MicroGain: [2, 2, 2],
            CardType.StrongGain: [0, 0, 1],
            CardType.MicroDiscomfort: [1, 1, 2],
            CardType.Technology: [1, 0, 0]
        }

        safe_deck_list = self.build_deck(room, player, card_plan)

        return safe_deck_list

    # 获取 险中求胜 列表 4张微弱增益 3张强大增益 1张欧皇增益 1张微弱不适 2张重度不适 1张特殊卡牌
    def build_danger_deck_list(self, room: Room, player: Player):
        card_list = room.game_config.card_list

        # 获取玩家还能抽取的卡牌列表数量
        player_can_draw_count = self.get_player_can_draw_count(player, card_list)

        requirements = {
            CardType.MicroGain: 4,
            CardType.StrongGain: 3,
            CardType.MicroDiscomfort: 1,
            CardType.StrongDiscomfort: 2,
            CardType.Technology: 1
        }

        if not self.check_drawable(player_can_draw_count, requirements):
            return []


        card_plan = {
            CardType.MicroGain: [1, 1, 2],
            CardType.StrongGain: [1, 1, 1],
            CardType.MicroDiscomfort: shuffle_list([0, 0, 1]),
            CardType.StrongDiscomfort: shuffle_list([0, 1, 1]),
            CardType.Technology: [1, 0, 0]
        }

        danger_deck_list = self.build_deck(room, player, card_plan)


        self.try_draw_card_with_fallback(room, player, CardType.Opportunity, CardType.StrongGain, shuffle_list([0, 0, 1]), danger_deck_list)

        return danger_deck_list

    # 获取 对赌博弈 列表 5张强大增益 1张欧皇增益 5张重度不适 1张反人类
    def build_gambit_deck_list(self, room: Room, player: Player):
        card_list = room.game_config.card_list

        # 获取玩家还能抽取的卡牌列表数量
        player_can_draw_count = self.get_player_can_draw_count(player, card_list)

        requirements = {
            CardType.StrongGain: 5,
            CardType.StrongDiscomfort: 5
        }

        if not self.check_drawable(player_can_draw_count, requirements):
            return []

        card_plan = {
            CardType.StrongGain: shuffle_list([1, 2, 2]),
            CardType.StrongDiscomfort: shuffle_list([1, 2, 2])
        }

        gambit_deck_list = self.build_deck(room, player, card_plan)

        self.try_draw_card_with_fallback(room, player, CardType.Opportunity, CardType.StrongGain, shuffle_list([0, 0, 1]), gambit_deck_list)
        self.try_draw_card_with_fallback(room, player, CardType.Unacceptable, CardType.StrongDiscomfort, shuffle_list([0, 0, 1]), gambit_deck_list)

        return gambit_deck_list

    # 获取 时来运转 列表 1张强大增益 1张欧皇增益 1张重度不适 1张反人类 8张特殊卡牌
    def build_luck_deck_list(self, room: Room, player: Player):
        card_list = room.game_config.card_list

        # 获取玩家还能抽取的卡牌列表数量
        player_can_draw_count = self.get_player_can_draw_count(player, card_list)

        requirements = {
            CardType.StrongGain: 1,
            CardType.StrongDiscomfort: 1,
            CardType.Technology: 8
        }

        if not self.check_drawable(player_can_draw_count, requirements):
            return []

        card_plan = {
            CardType.StrongGain: shuffle_list([0, 0, 1]),
            CardType.StrongDiscomfort: shuffle_list([0, 0, 1]),
            CardType.Technology: [8, 0, 0]
        }

        luck_deck_list = self.build_deck(room, player, card_plan)

        self.try_draw_card_with_fallback(room, player, CardType.Opportunity, CardType.StrongGain, shuffle_list([0, 0, 1]), luck_deck_list)
        self.try_draw_card_with_fallback(room, player, CardType.Unacceptable, CardType.StrongDiscomfort, shuffle_list([0, 0, 1]), luck_deck_list)

        return luck_deck_list

    # 获取 身心奉献 列表 8张辅助卡牌 4张微弱不适
    def build_devote_deck_list(self, room: Room, player: Player):
        card_list = room.game_config.card_list

        # 获取玩家还嫩抽取的卡牌列表数量
        player_can_draw_count = self.get_player_can_draw_count(player, card_list)

        support_count = len([card for card in card_list if card.card_type == CardType.Support.name and card.count > 0])
        technology_count = 8 - support_count

        requirements = {
            CardType.Support: 1,
            CardType.MicroDiscomfort: 4,
            CardType.Technology: technology_count
        }

        if not self.check_drawable(player_can_draw_count, requirements):
            return []

        card_plan = {
            CardType.Support : [support_count, 0, 0],
            CardType.MicroDiscomfort: [1, 1, 2],
            CardType.Technology: [technology_count, 0, 0]
        }

        devote_deck_list = self.build_deck(room, player, card_plan)

        return devote_deck_list

    # ------------------------------------------------------------------------------

    # 尝试函数
    # ------------------------------------------------------------------------------
    # 尝试补卡
    def try_draw_card_with_fallback(
            self, room: Room, player: Player,
            target_type: CardType,
            fallback_type: CardType,
            level_plan: List[int],
            deck: List[Card],
            max_count=10
    ):
        for _ in range(max_count):
            count = self.get_player_can_draw_count(player, room.game_config.card_list)[target_type.name]
            card_type = target_type if count > 0 else fallback_type
            card_list = self.get_deck_list_tag_level_list(room, player, card_type, shuffle_list(level_plan))
            if card_list and not self.check_card_in_player_deck_list(player, card_list[0]):
                deck += card_list
                break

    # ------------------------------------------------------------------------------

    # 获取函数
    # ------------------------------------------------------------------------------

    # 输出玩家可以抽取的数量
    def get_player_can_draw_count(self, player: Player, card_list: List[Card]):
        player_can_draw_count = {
            card_type.value:
                len([card for card in card_list if card.card_type == card_type.name and card.count > 0
                     and not (self.check_card_in_player_deck_list(player, card))])
             for card_type in CardType
        }

        for card_type in CardType:
            debug(f"{card_type} - {player_can_draw_count[card_type.name]}")

        return player_can_draw_count

    # 获取当前卡牌列表的标签等级数量
    @staticmethod
    def get_deck_list_tag_level_count(deck_list: List[Card], tag_level: int):
        deck_list_count = [card for card in deck_list if card.card_level == tag_level and card.count > 0]
        return len(deck_list_count)

    # 融合原先逻辑与智能补位算法
    # 假设 lottery_by_count 是从卡池中按权重抽一张卡的方法
    # 入口函数：根据等级和目标抽卡数从卡池抽卡（支持等级补位）
    def get_deck_list_tag_level_list(self, room, player, card_type, tag_level):
        tag_level_deck_list = []  # 最终抽到的卡列表
        card_list = room.game_config.card_list
        # 获取当前类型的所有未在玩家卡组中的卡牌列表
        game_card_list = [card for card in card_list if card.card_type == card_type.name
                          and not self.check_card_in_player_deck_list(player, card)]

        # 将卡牌按等级分类
        level_cards = {1: [], 2: [], 3: []}
        for card in game_card_list:
            if card.card_level in level_cards:
                level_cards[card.card_level].append(card)

        # 记录每个等级当前拥有的卡数量
        t1, t2, t3 = len(level_cards[1]), len(level_cards[2]), len(level_cards[3])

        # 如果所有卡加起来不够，则返回空
        if t1 + t2 + t3 < sum(tag_level):
            return []

        # 补位优先级规则
        priority = {
            1: [2, 3],
            2: [3, 1],
            3: [2, 1],
        }

        used_ids = set()  # 防止抽到重复卡

        # 内部函数：尝试从指定等级和补位等级抽卡
        def draw_from_levels(target_level, count):
            drawn = []
            levels_to_try = [target_level] + priority[target_level]
            for lvl in levels_to_try:
                candidates = [c for c in level_cards[lvl] if id(c) not in used_ids and c.count > 0]
                while candidates and len(drawn) < count:
                    card = lottery_by_count(candidates)
                    if card not in drawn and not self.check_card_in_player_deck_list(player, card):
                        drawn.append(card)
                        used_ids.add(id(card))
                        candidates.remove(card)
            return drawn

        # 开始执行抽卡，按等级目标执行补位逻辑
        for level, target_count in zip([1, 2, 3], tag_level):
            tag_level_deck_list.extend(draw_from_levels(level, target_count))

        debug(tag_level_deck_list)

        # 最终检查数量是否足够，不足返回空（视情况可以改为容错）
        if len(tag_level_deck_list) < sum(tag_level):
            return []

        return tag_level_deck_list

    # ------------------------------------------------------------------------------