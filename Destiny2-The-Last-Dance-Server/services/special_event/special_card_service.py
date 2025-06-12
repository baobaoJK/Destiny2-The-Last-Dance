import threading
import time

from entitys.game.player import Player, PlayerStatus
from entitys.game.room import Room
from entitys.game.special_conig import SpecialConfig, SpecialEventType
from entitys.message import Message
from entitys.sql.card import Card, CardType


class SpecialCardService:

    # 名称转换
    @staticmethod
    def convert_config_dict(frontend_config_dict: dict) -> SpecialConfig:
        special_config = SpecialConfig()
        special_config.title = frontend_config_dict['title']
        special_config.description = frontend_config_dict['description']
        special_config.event_name = frontend_config_dict['eventName']
        special_config.event_type = frontend_config_dict['eventType']
        special_config.send = frontend_config_dict['send']
        special_config.to = frontend_config_dict['to']
        special_config.players = frontend_config_dict['players']
        special_config.now_player = frontend_config_dict['nowPlayer']
        special_config.deck_list = frontend_config_dict['deckList']
        special_config.player_list = frontend_config_dict['playerList']
        special_config.options_list = frontend_config_dict['optionsList']
        return special_config

    # 重置信息
    @staticmethod
    def delayed_execution(player: Player):
        time.sleep(2)
        if player is not None:
            player.player_status = PlayerStatus.Idle
            player.special_config = SpecialConfig()

    # 特殊卡牌事件处理
    def run_special_by_card(self, room: Room, player: Player, special_config: SpecialConfig, card: Card):
        from services.card.card_service import CardService

        message_list = []
        card_service = CardService()

        event_name = special_config.event_name

        # 上贡
        if event_name == 'Tribute':
            target_player = room.player_list.get_player_by_id(special_config.to)

            if target_player is not None:
                message_list += card_service.delete_card(room, player, card)
                message_list += card_service.save_card(room, target_player, card)

        # 暴君
        if event_name == 'Tyrant':
            target_player = room.player_list.get_player_by_id(special_config.to)

            if target_player is not None:
                message_list += card_service.delete_card(room, target_player, card)
                message_list += card_service.save_card(room, player, card)

        # 人为财死
        if event_name == 'Money':
            another_card_type = None

            if card.card_type == CardType.MicroGain.name:
                another_card_type = CardType.MicroDiscomfort.name
            elif card.card_type == CardType.StrongGain.name:
                another_card_type = CardType.StrongDiscomfort.name
            elif card.card_type == CardType.Opportunity.name:
                another_card_type = CardType.Unacceptable.name

            message_list += card_service.get_random_card(room, player, card.card_type)
            message_list += card_service.get_random_card(room, player, another_card_type)

        # 顺手牵羊
        if event_name == 'Take-Others':
            to_player = room.player_list.get_player_by_id(special_config.to)

            message_list += card_service.delete_card(room, to_player, card)

            message = Message().warning('special.message.takeOthersText04')
            message.message_data = {
                'playerId': player.role_id,
            }
            message.to = to_player.sid
            message_list.append(message)

            message_list += card_service.save_card(room, player, card)

            message = Message().warning('special.message.takeOthersText05')
            message.message_data = {
                'playerId': to_player.role_id,
            }
            message.to = player.sid
            message_list.append(message)

        # 五谷丰登 | 生化母体
        if event_name == 'Bumper-Harvest' or event_name == 'Biochemical-Matrix':
            players = special_config.players[:]
            now_player = special_config.now_player

            target_player = room.player_list.get_player_by_id(players[now_player])

            message_list += card_service.save_card(room, target_player, card)

            special_config.now_player += 1
            special_config.deck_list.remove(card.to_dict())

            if len(special_config.deck_list) <= 0:
                for player_item in room.player_list.all_players():
                    player_item.player_status = PlayerStatus.Idle
                    player_item.special_config = SpecialConfig()
            else:
                for player_item in room.player_list.all_players():
                    player_item.player_status = PlayerStatus.BumperHarvest
                    player_item.special_config = special_config

            if event_name == 'Bumper-Harvest':
                message = Message().warning('special.message.bumperHarvestText02')
            else:
                message = Message().warning('special.message.biochemicalMatrixText02')

            message.event_type = event_name
            message.message_data = {
                'playerId': target_player.role_id,
                'cardName': f'cardList.{card.item_name}.name'
            }
            message.to = 'room'
            message_list.append(message)

        if event_name != 'Bumper-Harvest' and event_name != 'Biochemical-Matrix':
            player.player_status = PlayerStatus.Idle
            threading.Thread(target=self.delayed_execution, args=(player,)).start()

        return message_list

    # 上贡
    @classmethod
    def special_by_tribute(cls, room: Room, player: Player):
        list_1 = player.deck_list.get_card_type_list(CardType.MicroGain.name)
        list_2 = player.deck_list.get_card_type_list(CardType.StrongGain.name)
        list_3 = player.deck_list.get_card_type_list(CardType.Opportunity.name)

        if len(list_1) == 0 and len(list_2) == 0 and len(list_3) == 0:
            return Message().warning('special.message.tributeText01')

        to = player.special_config.to

        tribute_list = list_1 + list_2 + list_3

        player.player_status = PlayerStatus.Tribute

        special_config = SpecialConfig()
        special_config.title = 'cardList.tribute.name'
        special_config.description = 'special.message.tributeText02'
        special_config.event_name = player.player_status.name
        special_config.event_type = SpecialEventType.CARD_LIST.value
        special_config.send = player.role_id
        special_config.to = to
        special_config.deck_list = tribute_list

        player.special_config = special_config
        player.draw_card_type = None
        room.draw_card_player = None

        message = Message().warning('special.message.tributeText02')
        return message

    # 暴君
    @classmethod
    def special_by_tyrant(cls, room: Room, player: Player):
        all_card_list = []
        card_count = 0
        for target_player in room.player_list.all_players():
            if target_player.role_id == player.role_id:
                continue

            for card_type, card_list in target_player.deck_list.items():
                for card in card_list:
                    gain_card_type = card.card_type

                    if (gain_card_type == CardType.MicroGain.name
                        or gain_card_type == CardType.StrongGain.name
                        or gain_card_type == CardType.Opportunity.name):
                        card.role_id = target_player.role_id
                        all_card_list.append(card)
                        card_count += 1

        if card_count == 0:
            return Message().warning('special.message.tyrantText01')

        to = player.special_config.to
        player.player_status = PlayerStatus.Tyrant

        special_config = SpecialConfig()
        special_config.title = 'cardList.tyrant.name'
        special_config.description = 'special.message.tyrantText02'
        special_config.event_name = player.player_status.name
        special_config.event_type = SpecialEventType.CARD_LIST.value
        special_config.send = player.role_id
        special_config.to = to
        special_config.deck_list = all_card_list

        player.special_config = special_config
        player.draw_card_type = None
        room.draw_card_player = None

        return Message().warning('special.message.tyrantText02')

    # 人为财死
    @classmethod
    def special_by_money(cls, room: Room, player: Player):
        deck_list = [
            {
                'cardType': CardType.MicroGain.name,
                'cardName': 'cardTypeList.MicroGain',
                'cardDescription': 'special.message.moneyText01'
            },
            {
                'cardType': CardType.StrongGain.name,
                'cardName': 'cardTypeList.StrongGain',
                'cardDescription': 'special.message.moneyText02'
            },
            {
                'cardType': CardType.Opportunity.name,
                'cardName': 'cardTypeList.Opportunity',
                'cardDescription': 'special.message.moneyText03'
            }
        ]

        player.player_status = PlayerStatus.Money

        special_config = SpecialConfig()
        special_config.title = 'cardList.peopleDieForMoney.name'
        special_config.description = 'cardList.peopleDieForMoney.description'
        special_config.event_name = player.player_status.name
        special_config.event_type = SpecialEventType.CARD_LIST.value
        special_config.send = player.role_id
        special_config.deck_list = deck_list

        player.special_config = special_config
        player.draw_card_type = None
        room.draw_card_player = None

        return Message().warning('cardList.peopleDieForMoney.description')

    # ---------------------------------------------------
    # 特殊卡牌 事件
    # ---------------------------------------------------

    # 这不是个人恩怨
    @classmethod
    def special_by_personal(cls, room: Room, player: Player):
        player_list = room.get_player_seat()

        options_list = [
            {
                "text": 'win',
                "value": True
            },
            {
                "text": "lose",
                "value": False
            }
        ]

        player.player_status = PlayerStatus.Personal

        special_config = SpecialConfig()
        special_config.title = 'cardList.thisIsntAPersonal.name'
        special_config.description = 'special.message.thisIsntAPersonalText01'
        special_config.event_name = player.player_status.name
        special_config.event_type = SpecialEventType.PLAYER_LIST.value
        special_config.send = player.role_id
        special_config.to = -1
        special_config.player_list = player_list
        special_config.options_list = options_list

        player.special_config = special_config
        player.draw_card_type = None
        room.draw_card_player = None

        return Message().warning('special.message.thisIsntAPersonalText01')
