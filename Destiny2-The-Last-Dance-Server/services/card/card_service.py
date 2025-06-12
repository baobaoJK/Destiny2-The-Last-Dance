from entitys.game.player import PlayerStatus
from entitys.sql.card import CardType, Card, thirteen_list
from services.card.draw_cards_service import DrawCardsService
from services.card.special_card_service import SpecialCardService
from services.room_service import RoomService
from utils import error, shuffle_list, debug
from utils.tools.lottery import lottery_by_count
from entitys.message import Message
from entitys.game.player import Player
from entitys.game.room import Room
from entitys.sql.card import DeckType

room_service = RoomService()

draw_cards_service = DrawCardsService()

class CardService:

    # 名称转换
    @staticmethod
    def camel_to_snake(name):
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    def convert_card_dict(self, frontend_card_dict: dict) -> Card:
        # 将驼峰命名转换为下划线命名
        backend_dict = {self.camel_to_snake(k): v for k, v in frontend_card_dict.items()}
        return Card(**backend_dict)

    # 搜索卡牌
    @classmethod
    def find_card_by_name_in_player_deck_list(cls, player: Player, card_name: str):
        for card_type, card_list in player.deck_list.items():
            for card in card_list:
                if card.card_name == card_name:
                    return card
        return None

    # 检查卡牌列表是否存在该卡牌
    # 不存在返回 False
    # 存在返回 True
    @classmethod
    def check_deck_list(cls, deck_list, card: Card):
        if len(deck_list) == 0:
            return False
        card_item = next((item for item in deck_list if item.card_id == card.card_id), None)
        return card_item is not None

    # 抽取随机卡牌
    def get_random_card(self, room: Room, player: Player, card_type: CardType):
        card_list = [card for card in room.game_config.card_list if card.card_type == card_type]

        card = lottery_by_count(card_list)
        if card is not None:
            return self.save_card(room, player, card)

        message_list = [Message().warning('card.message.warningText09')]
        return message_list

    # 获取卡牌列表
    @classmethod
    def get_card_list(cls, room: Room):
        game_card_list = room.game_config.card_list
        card_list = {
            card_type.value: [card.to_dict() for card in game_card_list if card.card_type == card_type.value]
            for card_type in CardType
        }
        message = Message()
        message.data = {
            'cardList': card_list
        }

        return message

    # 显示卡组列表
    def show_deck_list(self, room: Room, player: Player, deck_type: DeckType):

        # 判断有没有人在抽卡
        if room.draw_card_player is not None:
            message = Message().error("card.message.errorText02")
            message.message_data = {
                'playerName': room.draw_card_player
            }
            return message

        # 判断玩家是否有抽卡次数
        if player.draw_count <= 0:
            player.player_status = PlayerStatus.Idle
            player.draw_card_type = None
            room.draw_card_player = None

            return Message().error("card.message.errorText03")


        deck_list_name = None
        deck_list = None

        # 判断卡组类型
        if DeckType(deck_type) is DeckType.Safe:
            deck_list_name = 'deckListName.safe'
            deck_list = draw_cards_service.build_safe_deck_list(room, player)
        elif DeckType(deck_type) is DeckType.Danger:
            deck_list_name = 'deckListName.danger'
            deck_list = draw_cards_service.build_danger_deck_list(room, player)
        elif DeckType(deck_type) is DeckType.Gambit:
            deck_list_name = 'deckListName.gambit'
            deck_list = draw_cards_service.build_gambit_deck_list(room, player)
        elif DeckType(deck_type) is DeckType.Luck:
            deck_list_name = 'deckListName.luck'
            deck_list = draw_cards_service.build_luck_deck_list(room, player)
        elif DeckType(deck_type) is DeckType.Devote:
            deck_list_name = 'deckListName.devote'
            deck_list = draw_cards_service.build_devote_deck_list(room, player)

        # 判断卡组列表是否充足
        if deck_list is None or len(deck_list) != 12:
            error("卡组列表不充足无法抽取")
            return Message().error("card.message.errorText04")

        # 修改玩家状态
        player.player_status = PlayerStatus.Draw
        player.draw_card_type = deck_type
        room.draw_card_player = player.player_name

        deck_list = shuffle_list(deck_list)

        message = Message().success("card.message.successText03")
        message.data = {
            'deckListName': deck_list_name,
            'deckList': [card.to_dict() for card in deck_list]
        }

        return message

    # 关闭卡组列表
    @classmethod
    def close_deck_list(cls, room: Room, player: Player):
        room.draw_card_player = None
        player.player_status = PlayerStatus.Idle
        player.draw_card_type = None

        message = Message.warning('card.message.warningText01')
        message.message_data = {
            'playerName': player.player_name
        }
        return message

    # 点击卡牌
    def click_card(self, room: Room, player: Player, card: Card):
        message_list = []

        # 判断玩家是否有抽卡次数
        if player.draw_count <= 0:
            player.player_status = PlayerStatus.Idle
            player.draw_card_type = None
            room.draw_card_player = None
            message_list.append(Message().error("card.message.errorText03"))
            return message_list

        player.draw_count -= 1

        # 不，你不能
        if player.player_attributes['isRandom']:
            random_list = [card for card in room.game_config.card_list if
                           not (draw_cards_service.check_card_in_player_deck_list(player, card))]
            random_card = lottery_by_count(random_list)

            message_list += self.save_card(room, player, random_card)
            message = Message().warning("card.message.warningText02")
            message.data = {
                'card': card.to_dict()
            }
            message_list.append(message)
        else:
            message_list = self.save_card(room, player, card)
            message = Message()
            message.data = {
                'card': card.to_dict()
            }
            message_list.append(message)

        return message_list

    # 添加卡牌至列表
    @classmethod
    def save_card(cls, room: Room, player: Player, card: Card):
        message_list = []
        special_card_service = SpecialCardService()
        # 获取卡牌类型
        card_type = card.card_type

        # 判断玩家是否有舍己为人
        if (card_type == CardType.MicroDiscomfort.name
                or card_type == CardType.StrongDiscomfort.name
                or card_type == CardType.Unacceptable.name):
            for target_player in room.player_list.all_players():
                if target_player.player_attributes['thirteen'] or player.role_id == target_player.role_id:
                    continue

                if target_player.player_attributes['selfless']:
                    player = target_player

                    message = Message().warning('card.message.warningText03')
                    message_list.append(message)

                    message = Message().warning('card.message.warningText04')
                    message.to = player.sid
                    message_list.append(message)

        # 检查卡牌列表是否存在该卡牌
        if not cls.check_deck_list(player.deck_list.get_card_type_list(card_type), card):
            player.deck_list.add_card(card)

            # 有福同享
            if player.blessing != 0:
                if (card_type == CardType.MicroGain.name
                    or card_type == CardType.StrongGain.name
                    or card_type == CardType.Opportunity.name):

                    and_player = room.player_list.get_player_by_id(player.blessing)

                    message = Message().warning("card.message.warningText05")
                    message.event_type = 'card'
                    message.message_data = {
                        'playerName': player.player_name,
                        'cardName': f'cardList.{card.item_name}.name'
                    }
                    message.to = and_player.sid
                    message_list.append(message)

            # 有难同当
            if player.disaster != 0:
                if (card_type == CardType.MicroDiscomfort.name
                    or card_type == CardType.StrongDiscomfort.name
                    or card_type == CardType.Unacceptable.name):

                    and_player = room.player_list.get_player_by_id(player.disaster)

                    message = Message().warning("card.message.warningText06")
                    message.event_type = 'card'
                    message.message_data = {
                        'playerName': player.player_name,
                        'cardName': f'cardList.{card.item_name}.name'
                    }
                    message.to = and_player.sid
                    message_list.append(message)

            message = Message().success("card.message.successText01")
            message.event_type = 'card'
            message.to = player.sid
            message.message_data = {
                'cardName': f'cardList.{card.item_name}.name'
            }
            message_list.append(message)

            # 等级提升
            if player.level_up:
                message_list += special_card_service.special_by_level_up(room, player)

            # 特殊卡牌事件执行
            special_message_list = special_card_service.special_card(room, player, card)
            if special_message_list is not None:
                for special_message in special_message_list:
                    message_list.append(special_message)

            # 更新卡牌数量
            card_item = next((item for item in room.game_config.card_list if item.card_name == card.card_name), None)

            if card_item is not None:
                card_item.count -= 1
        else:
            message = Message().error("card.message.errorText01")
            message.event_type = 'card'
            message.to = player.sid
            message.message_data = {
                'cardName': f'cardList.{card.item_name}.name'
            }
            message_list.append(message)

        # 判断卡牌名字
        if (card.card_name == 'Thirteen-Orphans'
            or card.card_name == 'Quit-Gambling'
            or card.card_name == 'Gambler'):
            player.player_status = PlayerStatus.Idle
            player.draw_card_type = None
            room.draw_card_player = None

        return message_list

    # 删除卡牌
    @classmethod
    def delete_card(cls, room: Room, player: Player, card: Card):
        message_list = []

        # 卡牌类型
        card_type = card.card_type

        # 苦肉计
        if (card.card_name != 'The-Self-Torture-Scheme' and player.player_attributes['torture']
                and (card_type == CardType.MicroGain.name
                    or card_type == CardType.StrongGain.name
                    or card_type == CardType.Opportunity.name)):
            player.draw_count += 2
            message_list.append(Message().warning('card.message.torture'))

        # 十三幺
        if card.card_name == 'Thirteen-Orphans':
            for card_name in thirteen_list:
                card_item = next((card for card in room.game_config.card_list if card.card_name == card_name), None)
                if card_item in player.deck_list.get_card_type_list(card_item.card_type):
                    player.deck_list.remove_card(card_item)

            message_list.append(Message().warning('card.message.thirteenOrphans'))

        # 卡牌回收计划
        if card.card_name != 'Card-Recycling-Program' and player.player_attributes['program']:
            temp_str = ''
            if card.card_type == CardType.MicroGain.name:
                player.player_money += 1
                temp_str = 'card.message.programText01'
            elif card.card_type == CardType.StrongGain.name:
                player.player_money += 3
                temp_str = 'card.message.programText02'
            elif card.card_type == CardType.Opportunity.name:
                player.player_money += 6
                temp_str = 'card.message.programText03'

            message_list.append(Message().warning(temp_str))

        # 有福同享
        if player.blessing != 0:
            if (card_type == CardType.MicroGain.name
                or card_type == CardType.StrongGain.name
                or card_type == CardType.Opportunity.name):

                and_player = room.player_list.get_player_by_id(player.blessing)
                message = Message().warning('card.message.warningText07')
                message.event_type = 'card'
                message.message_data = {
                    'playerName': player.player_name,
                    'cardName': f'cardList.{card.item_name}.name'
                }
                message.to = and_player.sid
                message_list.append(message)

        # 有难同当
        if player.disaster != 0:
            if (card_type == CardType.MicroDiscomfort.name
                or card_type == CardType.StrongDiscomfort.name
                or card_type == CardType.Unacceptable.name):

                and_player = room.player_list.get_player_by_id(player.disaster)
                message = Message().warning('card.message.warningText08')
                message.event_type = 'card'
                message.message_data = {
                    'playerName': player.player_name,
                    'cardName': f'cardList.{card.item_name}.name'
                }
                message.to = and_player.sid
                message_list.append(message)

        # 删除卡牌
        player.deck_list.remove_card(card)
        message = Message().success("card.message.successText02")
        message.event_type = 'card'
        message.to = player.sid
        message.message_data = {
            'cardName': f'cardList.{card.item_name}.name'
        }
        message_list.append(message)
        return message_list

    # 转换
    def transform_card(self, room: Room, player: Player, card: Card):
        message_list = self.delete_card(room, player, card)

        for card_type, card_list in player.deck_list.items():
            card_to_remove = card_list[:]
            for card_item in card_to_remove:
                if card_item.card_type == CardType.MicroDiscomfort.name:
                    message_list += self.delete_card(room, player, card_item)
                    message_list += self.get_random_card(room, player, CardType.MicroGain)
                if card_item.card_type == CardType.StrongDiscomfort.name:
                    message_list += self.delete_card(room, player, card_item)
                    message_list += self.get_random_card(room, player, CardType.StrongGain)
                if card_item.card_type == CardType.Unacceptable.name:
                    message_list += self.delete_card(room, player, card_item)
                    message_list += self.get_random_card(room, player, CardType.Opportunity)

        return message_list