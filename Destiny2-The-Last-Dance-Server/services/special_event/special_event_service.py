import random
import threading

from entitys.game.player import Player, PlayerStatus
from entitys.game.room import Room
from entitys.game.special_conig import SpecialConfig, SpecialEventType
from entitys.message import Message
from entitys.sql.card import CardType
from utils import debug, shuffle_list


class SpecialEventService:
    # 特殊事件处理
    @classmethod
    def run_special_by_event(cls, room: Room, player: Player, special_config: SpecialConfig):
        from services.card.card_service import CardService
        from services.special_event.special_card_service import SpecialCardService

        message_list = []

        card_service = CardService()

        event_name = special_config.event_name

        # 这不是个人恩怨
        if event_name == 'Personal':
            target_player = room.player_list.get_player_by_id(special_config.to)

            target_player_deck_list = []
            if not target_player.player_attributes['thirteen']:
                for card_type, card_list in target_player.deck_list.items():
                    for card in card_list:
                        target_player_deck_list.append(card)

            player_deck_list = []
            if not player.player_attributes['thirteen']:
                for card_type, card_list in player.deck_list.items():
                    for card in card_list:
                        player_deck_list.append(card)

            gain_deck_list = []
            discomfort_deck_list = []

            if special_config.value:
                source_deck = target_player_deck_list  # 从目标玩家移除增益卡
                target_deck = player_deck_list  # 从当前玩家移除不适卡
                gain_recipient = player  # 增益卡接收者是当前玩家
                discomfort_recipient = target_player  # 不适卡接收者是目标玩家
            else:
                source_deck = player_deck_list  # 从当前玩家移除增益卡
                target_deck = target_player_deck_list  # 从目标玩家移除不适卡
                gain_recipient = target_player  # 增益卡接收者是目标玩家
                discomfort_recipient = player  # 不适卡接收者是当前玩家

            # 增益卡类型
            gain_types = {
                CardType.MicroGain.name,
                CardType.StrongGain.name,
                CardType.Opportunity.name
            }

            # 不适卡类型
            discomfort_types = {
                CardType.MicroDiscomfort.name,
                CardType.StrongDiscomfort.name,
                CardType.Unacceptable.name
            }

            # 从 source_deck 移除增益卡
            for card in source_deck[:]:  # 遍历副本，避免修改原列表时的问题
                if card.card_type in gain_types:
                    message_list += card_service.delete_card(room, discomfort_recipient, card)
                    gain_deck_list.append(card)

            # 从 target_deck 移除不适卡
            for card in target_deck[:]:
                if card.card_type in discomfort_types:
                    message_list += card_service.delete_card(room, gain_recipient, card)
                    discomfort_deck_list.append(card)

            # 如果玩家没有 'thirteen' 属性，则应用交换
            if not gain_recipient.player_attributes.get('thirteen'):
                for card in gain_deck_list:
                    message_list += card_service.save_card(room, gain_recipient, card)

            if not discomfort_recipient.player_attributes.get('thirteen'):
                for card in discomfort_deck_list:
                    message_list += card_service.save_card(room, discomfort_recipient, card)

            message = Message().warning('special.message.thisIsntAPersonalText02')
            message.to = player.sid
            message_list.append(message)

            message = Message().warning('special.message.thisIsntAPersonalText02')
            message.to = target_player.sid
            message_list.append(message)

        # 赢下所有或一无所有
        if event_name == 'Win-or-Loss':
            value = special_config.value

            if value == 20:
                for _ in range(3):
                    message_list += card_service.get_random_card(room, player, CardType.StrongGain.name)

                message_list.append(Message().warning('special.message.winOrLossText01'))
            elif value == 1:
                for _ in range(3):
                    message_list += card_service.get_random_card(room, player, CardType.StrongDiscomfort.name)

                message_list.append(Message().warning('special.message.winOrLossText02'))
            else:
                message_list.append(Message().warning('special.message.winOrLossText03'))

        # 幸运数字
        if event_name == 'Lucky-Number':
            value = special_config.value

            if value == 7:
                random_card_type = [
                    CardType.MicroGain.name,
                    CardType.StrongGain.name,
                    CardType.Opportunity.name
                ]
                message_list += card_service.get_random_card(room, player, random.choice(random_card_type))
                message_list.append(Message().warning('special.message.luckyNumberText02'))
            elif value == 2:
                random_card_type = [
                    CardType.MicroDiscomfort.name,
                    CardType.StrongDiscomfort.name,
                    CardType.Unacceptable.name
                ]
                message_list += card_service.get_random_card(room, player, random.choice(random_card_type))
                message_list.append(Message().warning('special.message.luckyNumberText03'))
            else:
                message_list.append(Message().warning('special.message.luckyNumberText04'))

        # 内鬼
        if event_name == 'Spy':
            value = special_config.value

            if value:
                random_type = [
                    CardType.MicroGain.name,
                    CardType.StrongGain.name,
                    CardType.Opportunity.name
                ]
                message_list += card_service.get_random_card(room, player, random.choice(random_type))
                message_list.append(Message().warning('special.message.spyText01'))
            else:
                random_type = [
                    CardType.MicroDiscomfort.name,
                    CardType.StrongDiscomfort.name,
                    CardType.Unacceptable.name
                ]
                message_list += card_service.get_random_card(room, player, random.choice(random_type))
                message_list.append(Message().warning('special.message.spyText02'))

        # 噶点放心飞，出事自己背
        if event_name == 'By-Self':
            value = special_config.value

            if value > 0:
                for _ in range(value):
                    random_card_type = [
                        CardType.MicroDiscomfort.name,
                        CardType.StrongDiscomfort.name,
                        CardType.Unacceptable.name
                    ]
                    message_list += card_service.get_random_card(room, player, random.choice(random_card_type))

                message = Message().warning('special.message.bySelfText05')
                message.message_data = {
                    'count': value
                }
                message_list.append(message)
            else:
                random_card_type = [
                    CardType.MicroGain.name,
                    CardType.StrongGain.name,
                    CardType.Opportunity.name
                ]
                message_list += card_service.get_random_card(room, player, random.choice(random_card_type))
                message_list.append(Message().warning('special.message.bySelfText06'))

        # Alex-Mercer
        if event_name == 'Alex-Mercer':
            value = special_config.value
            to = special_config.to

            if value:
                to_player = room.player_list.get_player_by_id(to)

                player.player_money += to_player.player_money
                to_player.player_money = 0
                player.draw_count += to_player.draw_count
                to_player.draw_count = 0

                if not to_player.player_attributes['thirteen']:
                    for card_type, card_list in to_player.deck_list.items():
                        card_to_remove = card_list[:]

                        for card in card_to_remove:
                            message_list += card_service.delete_card(room, to_player, card)
                            message_list += card_service.save_card(room, player, card)
                else:
                    card = to_player.deck_list.get_card_by_name('Thirteen-Orphans')
                    if card is not None:
                        message_list += card_service.delete_card(room, to_player, card)

                back_to_remove = to_player.backpack[:]

                for item in back_to_remove:
                    player.backpack.append(item)
                    to_player.backpack.remove(item)

                message = Message().warning('special.message.alexMercerText03')
                message.to = player.sid
                message_list.append(message)

                message = Message().warning('special.message.alexMercerText04')
                message.to = to_player.sid
                message_list.append(message)
            else:
                message_list.append(Message().warning('nothing'))

        # 你知道的，这是交易
        if event_name == 'This-Is-The-Deal':
            value = special_config.value
            to_player = room.player_list.get_player_by_id(special_config.to)

            temp_deck_list = []

            if value:
                source_player = player
                target_player = to_player
            else:
                source_player = to_player
                target_player = player

            if not source_player.player_attributes['thirteen']:
                for card_type, card_list in source_player.deck_list.items():
                    for card in card_list:
                        temp_deck_list.append(card)

            if len(temp_deck_list) <= 0:
                message = Message().warning('special.message.thisIsTheDealText03')
                message.to = source_player.sid
                message_list.append(message)

                message = Message().warning('special.message.thisIsTheDealText04')
                message.to = target_player.sid
                message_list.append(message)
            else:
                if not target_player.player_attributes['thirteen']:
                    temp_deck_list = shuffle_list(temp_deck_list)
                    message_list += card_service.save_card(room, target_player, temp_deck_list[0])
                    message_list += card_service.delete_card(room, source_player, temp_deck_list[0])

                    message = Message().warning('special.message.thisIsTheDealText05')
                    message.to = source_player.sid
                    message_list.append(message)

                    message = Message().warning('special.message.thisIsTheDealText06')
                    message.to = target_player.sid
                    message_list.append(message)
                else:
                    message = Message().warning('special.message.thisIsTheDealText07')
                    message.to = to=source_player.sid
                    message_list.append(message)

        # 以存护之名
        if event_name == 'In-The-Name-of-Preservation':
            value = special_config.value
            to_player = room.player_list.get_player_by_id(special_config.to)

            if value:
                for target_player in [player, to_player]:
                    if not target_player.player_attributes['thirteen']:
                        message_list += card_service.get_random_card(room, target_player, CardType.StrongGain.name)
                        message = Message().warning('special.message.inTheNameOfPreservationText02')
                        message.to = target_player.sid
                        message_list.append(message)
                    else:
                        message = Message().warning('special.message.inTheNameOfPreservationText03')
                        message.to = target_player.sid
                        message_list.append(message)
            else:
                player_deck_list = []

                if not player.player_attributes['thirteen']:
                    for card_type, card_list in player.deck_list.items():
                        for card in card_list:
                            if(card.card_type == CardType.MicroGain.name
                                or card.card_type == CardType.StrongGain.name
                                or card.card_type == CardType.Opportunity.name):
                                player_deck_list.append(card)
                else:
                    player_card = player.deck_list.get_card('Thirteen-Orphans')
                    player_deck_list.append(player_card)

                if len(player_deck_list) != 0:
                    random_card = random.choice(player_deck_list)
                    message_list += card_service.delete_card(room, player, random_card)
                    message_list.append(Message().warning('special.message.inTheNameOfPreservationText05'))
                else:
                    message_list.append(Message().warning('special.message.inTheNameOfPreservationText04'))

        # 移型换位
        if event_name == 'Transposition':
            send_player = room.player_list.get_player_by_id(special_config.send)
            to_player = room.player_list.get_player_by_id(special_config.to)

            send_player_deck_list = []
            if not send_player.player_attributes['thirteen']:
                for card_type, card_list in send_player.deck_list.items():
                    card_to_remove = card_list[:]
                    for card in card_to_remove:
                        send_player_deck_list.append(card)
                        message_list += card_service.delete_card(room, send_player, card)
            else:
                thirteen_card = send_player.deck_list.get_card('Thirteen-Orphans')
                send_player_deck_list.append(thirteen_card)
                message_list += card_service.delete_card(room, send_player, thirteen_card)

            to_player_deck_list = []
            if not to_player.player_attributes['thirteen']:
                for card_type, card_list in to_player.deck_list.items():
                    card_to_remove = card_list[:]
                    for card in card_to_remove:
                        to_player_deck_list.append(card)
                        message_list += card_service.delete_card(room, to_player, card)
            else:
                thirteen_card = to_player.deck_list.get_card('Thirteen-Orphans')
                to_player_deck_list.append(thirteen_card)
                message_list += card_service.delete_card(room, to_player, thirteen_card)

            for card_item in send_player_deck_list:
                message_list += card_service.save_card(room, to_player, card_item)

            for card_item in to_player_deck_list:
                message_list += card_service.save_card(room, send_player, card_item)

            message = Message().warning("special.message.transpositionText01")
            message.to = send_player.sid
            message_list.append(message)

            message = Message().warning("special.message.transpositionText01")
            message.to = to_player.sid
            message_list.append(message)

        # 我们，我不明白
        if event_name == 'We':
            value = special_config.value

            if value == 0:
                for player_item in room.player_list.all_players():
                    player_item.player_money += 6
                    player_item.draw_count += 2

                message = Message().warning('special.message.weText03')
                message.to = 'room'
                message_list.append(message)
            elif value == 1:
                for player_item in room.player_list.all_players():
                    random_money = random.randint(1, 6)
                    player_item.player_money += random_money

                    message = Message().warning('special.message.weText04')
                    message.message_data = {
                        'playerMoney': random_money
                    }
                    message.to = player_item.sid
                    message_list.append(message)
            elif value == -1:
                for player_item in room.player_list.all_players():
                    if not player_item.player_attributes['thirteen']:
                        random_card_type = [
                            CardType.MicroDiscomfort.name,
                            CardType.StrongDiscomfort.name,
                            CardType.Unacceptable.name
                        ]
                        message_list += card_service.get_random_card(room, player_item, random.choice(random_card_type))

                        message = Message().warning('special.message.weText05')
                        message.to = player_item.sid
                        message_list.append(message)
                    else:
                        message = Message().warning('special.message.weText06')
                        message.to = player_item.sid
                        message_list.append(message)

        # 风险转换
        if event_name == 'Risk-Transformation':
            to_player = room.player_list.get_player_by_id(special_config.to)

            # 将玩家自己的增益卡牌给对方
            player_deck_list = []
            for card_type, card_list in player.deck_list.items():
                card_to_remove = card_list[:]
                for card in card_to_remove:
                    if (card.card_type == CardType.MicroGain.name
                        or card.card_type == CardType.StrongGain.name
                        or card.card_type == CardType.Opportunity.name):

                        player_deck_list.append(card)
                        message_list += card_service.delete_card(room, player, card)

            for card_item in player_deck_list:
                message_list += card_service.save_card(room, to_player, card_item)

            # 将对方的减益卡牌转为给自己
            to_player_deck_list = []
            for card_type, card_list in to_player.deck_list.items():
                card_to_remove = card_list[:]
                for card in card_to_remove:
                    if (card.card_type == CardType.MicroDiscomfort.name
                        or card.card_type == CardType.StrongDiscomfort.name
                        or card.card_type == CardType.Unacceptable.name):
                        to_player_deck_list.append(card)
                        message_list += card_service.delete_card(room, to_player, card)

            for card_item in to_player_deck_list:
                message_list += card_service.save_card(room, player, card_item)

        player.player_status = PlayerStatus.Idle
        threading.Thread(target=SpecialCardService.delayed_execution, args=(player,)).start()

        return message_list

    # 内鬼
    @classmethod
    def special_by_spy(cls, player: Player):
        options_list = [
            {
                'text': 'success',
                'value': True
            },
            {
                'text': 'failure',
                'value': False
            }
        ]

        player.player_status = PlayerStatus.Spy

        special_config = SpecialConfig()
        special_config.title = 'playerEventList.spy.name'
        special_config.description = 'playerEventList.spy.description'
        special_config.event_name = player.player_status.name
        special_config.event_type = SpecialEventType.OPTIONS_LIST.value
        special_config.send = player.role_id
        special_config.options_list = options_list

        player.special_config = special_config

    # 顺手牵羊
    @classmethod
    def special_by_take_others(cls, room: Room, player: Player):
        target_player_list = []
        for target_player in room.player_list.all_players():
            if target_player != player and target_player.deck_list.get_card_count() != 0:
                target_player_list.append(target_player)

        if len(target_player_list) != 0:
            target_player = random.choice(target_player_list)

            all_deck_list = []

            for card_type, card_list in target_player.deck_list.items():
                for card in card_list:
                    card.role_id = target_player.role_id
                    all_deck_list.append(card)

            all_deck_list = shuffle_list(all_deck_list)

            player.player_status = PlayerStatus.TakeOthers

            special_config = SpecialConfig()
            special_config.title = 'playerEventList.takeOthers.name'
            special_config.description = 'special.message.takeOthersText02'
            special_config.event_name = player.player_status.value
            special_config.event_type = SpecialEventType.CARD_LIST.value
            special_config.send = player.role_id
            special_config.to = target_player.role_id
            special_config.deck_list = all_deck_list

            player.special_config = special_config

            return Message().warning('special.message.takeOthersText03')

        else:
            return Message().warning('special.message.takeOthersText01')

    # 赢下所有或一无所有
    @classmethod
    def special_by_win_or_loss(cls, player: Player):
        options_list = [
            {
                "text": 20,
                "value": 20,
            },
            {
                "text": 1,
                "value": 1,
            },
            {
                "text": "nothing",
                "value": 0
            }
        ]

        player.player_status = PlayerStatus.WinOrLoss

        special_config = SpecialConfig()
        special_config.title = 'playerEventList.winOrLoss.name'
        special_config.description = 'playerEventList.winOrLoss.description'
        special_config.event_name = player.player_status.value
        special_config.event_type = SpecialEventType.OPTIONS_LIST.value
        special_config.send = player.role_id
        special_config.options_list = options_list

        player.special_config = special_config

        return Message().warning('playerEventList.winOrLoss.description')

    # 幸运数字
    @classmethod
    def special_by_lucky_number(cls, player: Player):
        options_list = [
            {
                "text": "7/14/17",
                "value": 7,
            },
            {
                "text": "special.message.luckyNumberText01",
                "value": 2,
            },
            {
                "text": "nothing",
                "value": 0
            }
        ]

        player.player_status = PlayerStatus.LuckyNumber

        special_config = SpecialConfig()
        special_config.title = 'playerEventList.luckyNumber.name'
        special_config.description = 'playerEventList.luckyNumber.description'
        special_config.event_name = player.player_status.value
        special_config.event_type = SpecialEventType.OPTIONS_LIST.value
        special_config.send = player.role_id
        special_config.options_list = options_list

        player.special_config = special_config

        return Message().warning('playerEventList.luckyNumber.description')

    # 噶点放心飞，出事自己背
    @classmethod
    def special_by_self(cls, player: Player):
        options_list = [
            {
                "text": "special.message.bySelfText01",
                "value": 1,
            },
            {
                "text": "special.message.bySelfText02",
                "value": 2,
            },
            {
                "text": "special.message.bySelfText03",
                "value": 3
            },
            {
                "text": "special.message.bySelfText04",
                "value": 0
            }
        ]

        player.player_status = PlayerStatus.BySelf

        special_config = SpecialConfig()
        special_config.title = 'playerEventList.bySelf.name'
        special_config.description = 'playerEventList.bySelf.description'
        special_config.event_name = player.player_status.value
        special_config.event_type = SpecialEventType.OPTIONS_LIST.value
        special_config.send = player.role_id
        special_config.options_list = options_list

        player.special_config = special_config

        return Message().warning('playerEventList.bySelf.description')

    # Alex Mercer
    @classmethod
    def special_by_alex_mercer(cls, room: Room, player: Player):

        player_list = room.get_player_seat()

        options_list = [
            {
                "text": "special.message.alexMercerText01",
                "value": True,
            },
            {
                "text": "special.message.alexMercerText02",
                "value": False
            }
        ]

        player.player_status = PlayerStatus.AlexMercer

        special_config = SpecialConfig()
        special_config.title = 'playerEventList.alexMercer.name'
        special_config.description = 'playerEventList.alexMercer.description'
        special_config.event_name = player.player_status.value
        special_config.event_type = SpecialEventType.PLAYER_LIST.value
        special_config.send = player.role_id
        special_config.options_list = options_list
        special_config.player_list = player_list

        player.special_config = special_config

        return Message().warning('playerEventList.alexMercer.description')

    # 你知道的，这是交易
    @classmethod
    def special_by_you_know(cls, room: Room, player: Player):

        player_list = room.get_player_seat()

        options_list = [
            {
                "text": "special.message.thisIsTheDealText01",
                "value": True,
            },
            {
                "text": "special.message.thisIsTheDealText02",
                "value": False
            }
        ]

        player.player_status = PlayerStatus.ThisIsTheDeal

        special_config = SpecialConfig()
        special_config.title = 'playerEventList.thisIsTheDeal.name'
        special_config.description = 'playerEventList.thisIsTheDeal.description'
        special_config.event_name = player.player_status.value
        special_config.event_type = SpecialEventType.PLAYER_LIST.value
        special_config.send = player.role_id
        special_config.options_list = options_list
        special_config.player_list = player_list

        player.special_config = special_config

        return Message().warning('playerEventList.thisIsTheDeal.description')

    # 以存护之名
    @classmethod
    def special_by_preservation(cls, room: Room, player: Player):
        player_list = room.get_player_seat()

        options_list = [
            {
                "text": "success",
                "value": True
            },
            {
                "text": "failure",
                "value": False
            }
        ]

        player.player_status = PlayerStatus.Preservation

        special_config = SpecialConfig()
        special_config.title = 'playerEventList.inTheNameOfPreservation.name'
        special_config.description = 'special.message.inTheNameOfPreservationText01'
        special_config.event_name = player.player_status.value
        special_config.event_type = SpecialEventType.PLAYER_LIST.value
        special_config.send = player.role_id
        special_config.options_list = options_list
        special_config.player_list = player_list

        player.special_config = special_config

        return Message().warning('playerEventList.inTheNameOfPreservation.description')

    # 五谷丰登
    @classmethod
    def special_by_bumper_harvest(cls, room: Room):

        players = [player.role_id for player in room.player_list.all_players() if player is not None]
        players = shuffle_list(players)

        all_deck_list = []
        for _ in range(len(players)):
            random_card = random.choice(room.game_config.card_list)
            all_deck_list.append(random_card)

        all_deck_list = shuffle_list(all_deck_list)

        special_config = SpecialConfig()
        special_config.title = 'globalEventList.bumperHarvest.name'
        special_config.description = 'globalEventList.bumperHarvest.description'
        special_config.event_name = 'Bumper-Harvest'
        special_config.event_type = SpecialEventType.CARD_LIST.value
        special_config.now_player = 0
        special_config.players = players
        special_config.deck_list = all_deck_list

        for player in room.player_list.all_players():
            player.player_status = PlayerStatus.BumperHarvest
            player.special_config = special_config

        message = Message().warning('special.message.bumperHarvestText01')
        message.message_data = {
            'playerId1': players[0],
            'playerId2': players[1],
            'playerId3': players[2],
            'playerId4': players[3],
            'playerId5': players[4],
            'playerId6': players[5],
        }
        message.to = 'room'

        return message

    # 移型换位
    @classmethod
    def special_by_transposition(cls, room: Room, player: Player):
        player_list = room.get_player_seat()
        options_list = [
            {
                "text": "confirm",
                "value": True
            }
        ]

        player.player_status = PlayerStatus.Transposition

        special_config = SpecialConfig()
        special_config.title = 'globalEventList.transposition.name'
        special_config.description = 'globalEventList.transposition.description'
        special_config.event_name = player.player_status.value
        special_config.event_type = SpecialEventType.PLAYER_LIST.value
        special_config.send = player.role_id
        special_config.options_list = options_list
        special_config.player_list = player_list

        player.special_config = special_config

        return Message().warning('globalEventList.transposition.description')

    # 生化母体
    @classmethod
    def special_by_matrix(cls, room: Room):

        players = [player.role_id for player in room.player_list.all_players() if player is not None]
        players = shuffle_list(players)

        all_deck_list = []
        while len(all_deck_list) != len(players):
            random_card_type = [
                CardType.MicroDiscomfort.name,
                CardType.StrongDiscomfort.name,
                CardType.Unacceptable.name
            ]
            random_card = random.choice(room.game_config.card_list)
            if random_card.card_type in random_card_type:
                all_deck_list.append(random_card)

        all_deck_list = shuffle_list(all_deck_list)

        special_config = SpecialConfig()
        special_config.title = 'globalEventList.biochemicalMatrix.name'
        special_config.description = 'globalEventList.biochemicalMatrix.description'
        special_config.event_name = 'Biochemical-Matrix'
        special_config.event_type = SpecialEventType.CARD_LIST.value
        special_config.now_player = 0
        special_config.players = players
        special_config.deck_list = all_deck_list

        for player in room.player_list.all_players():
            player.player_status = PlayerStatus.BiochemicalMatrix
            player.special_config = special_config

        message = Message().warning('special.message.biochemicalMatrixText01')
        message.message_data = {
            'playerId1': players[0],
            'playerId2': players[0],
            'playerId3': players[0],
            'playerId4': players[1],
            'playerId5': players[1],
            'playerId6': players[1],
        }
        message.to = 'room'
        return message

    # 我们，我不明白
    @classmethod
    def special_by_we(cls, room: Room):
        options_list = [
            {
                "text": "flawless",
                "value": 0
            },
            {
                "text": "special.message.weText01",
                "value": 1
            },
            {
                "text": "special.message.weText02",
                "value": -1
            }
        ]

        player = [player_item for player_item in room.player_list.all_players() if player_item.is_captain][0]

        player.player_status = PlayerStatus.We

        special_config = SpecialConfig()
        special_config.title = 'globalEventList.weIDontUnderstand.name'
        special_config.description = 'globalEventList.weIDontUnderstand.description'
        special_config.event_name = player.player_status.value
        special_config.event_type = SpecialEventType.OPTIONS_LIST.value
        special_config.send = player.role_id
        special_config.options_list = options_list

        player.special_config = special_config

        return Message().warning('globalEventList.weIDontUnderstand.description')

    # 风险转换
    @classmethod
    def special_by_risk_transformation(cls, room: Room, player: Player):
        player_list = room.get_player_seat()

        options_list = [
            {
                "text": "confirm",
                "value": True
            }
        ]

        player.player_status = PlayerStatus.RiskTransformation

        special_config = SpecialConfig()
        special_config.title = 'playerEventList.riskTransformation.name'
        special_config.description = 'playerEventList.riskTransformation.description'
        special_config.event_name = player.player_status.value
        special_config.event_type = SpecialEventType.PLAYER_LIST.value
        special_config.send = player.role_id
        special_config.options_list = options_list
        special_config.player_list = player_list

        player.special_config = special_config

        return Message().warning('playerEventList.riskTransformation.description')