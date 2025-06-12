import random
from random import choice

from entitys.message import Message
from entitys.game.player import Player
from entitys.game.room import Room
from entitys.sql.card import CardType
from entitys.sql.player_event import PlayerEvent
from services.card.card_service import CardService
from services.special_event.special_event_service import SpecialEventService
from utils.tools.lottery import lottery_by_count


# 玩家事件服务器类
class PlayerEventService:

    # 接受个人事件
    def accept_player_event(self, room: Room, player: Player, event_index: int):

        # 获取事件
        player_event = player.player_event_list.get_event(event_index)
        player_event.event_status = 'active'

        message_list = self.run_player_event(room, player, player_event)

        message = Message().success(message='playerEvent.message.successText01')
        message.event_type = 'playerEvent'
        message.to = player.sid
        message.message_data = {
            'playerEventName': f'playerEventList.{player_event.item_name}.name'
        }
        message_list.append(message)

        return message_list

    # 执行个人事件
    @classmethod
    def run_player_event(cls, room: Room, player: Player, player_event: PlayerEvent):
        message_list = []

        # 卡牌服务类
        card_service = CardService()
        special_event_service = SpecialEventService()

        player_event_name = player_event.event_name

        # 亚托克斯
        if player_event_name == 'Aatrox':
            for aatrox_card in room.game_config.card_list:
                if aatrox_card.card_name == 'Aatrox':
                    player.deck_list.add_card(aatrox_card)
                    message_list.append(Message().warning('special.message.aatroxText01'))
            # aatrox_card_dict = {
            #     'cardId': 'Aatrox',
            #     'cardType': CardType.StrongDiscomfort.name,
            #     'cardLabel': 'god',
            #     'cardLevel': 999,
            #     'itemName': 'aatrox',
            #     'cardName': 'Aatrox',
            #     'cardCnName': '亚托克斯',
            #     'cardDescription': '获得一把挽歌且绑定威能位无法更换，可被[贱卖][重铸]和2阶圣水解除，前二者失去挽歌，后者保留',
            #     'cardSpecial': 'god',
            #     'weight': 0,
            #     'count': 0,
            #     'allCount': 0,
            #     'idea': '来自亚托克斯'
            # }
            # aatrox_card = card_service.convert_card_dict(aatrox_card_dict)



        # 顺手牵羊
        if player_event_name == 'Take-Others':
            message_list.append(special_event_service.special_by_take_others(room, player))

        # 无中生有
        if player_event_name == 'Create-Nothing':
            player.draw_count += 2
            message_list.append(Message().warning('special.message.createNothingText01'))

        # 零元购
        if player_event_name == '0-Money-Buy':
            player.zero_buy = 3
            message_list.append(Message().warning('special.message.zeroMoneyBuyText01'))

        # 赢下所有或一无所有
        if player_event_name == 'Win-or-Loss':
            message_list.append(special_event_service.special_by_win_or_loss(player))

        # 幸运数字
        if player_event_name == 'Lucky-Number':
            message_list.append(special_event_service.special_by_lucky_number(player))

        # 开摆
        if player_event_name == 'Open1':
            player.give_up = True

        # 苦尽甘来
        if player_event_name == 'Sweet-After-Bitter':
            for _ in range(3):
                random_type = [
                    CardType.MicroDiscomfort.name,
                    CardType.StrongDiscomfort.name,
                    CardType.Unacceptable.name
                ]
                card_list = [card for card in room.game_config.card_list if card.card_type == random.choice(random_type)]
                card = lottery_by_count(card_list)
                if card is not None:
                    message_list += card_service.save_card(room, player, card)
                player.sab_list.append(card)

            message_list.append(Message().warning('special.message.sweetAfterBitterText01'))

        # 风险转化
        if player_event_name == 'Risk-Transformation':
            message_list.append(special_event_service.special_by_risk_transformation(room, player))

        return message_list

    # 完成个人事件
    @classmethod
    def finish_player_event(cls, room:Room, player: Player, event_index: int):
        message_list = []

        # 卡牌服务类
        card_service = CardService()
        special_event_service = SpecialEventService()

        # 获取事件，设置事件状态
        player_event = player.player_event_list.get_event(event_index)
        player_event_name = player_event.event_name

        # 内鬼
        if player_event_name == 'Spy':
            special_event_service.special_by_spy(player)

        # 饮鸩止渴
        if player_event_name == 'Drinking-Poison-to-Quench-Thirst':
            message_list += card_service.get_random_card(room, player, CardType.MicroDiscomfort.name)
            message_list += card_service.get_random_card(room, player, CardType.StrongDiscomfort.name)

        # 噶点放心飞，出事自己背
        if player_event_name == 'By-Self':
            message_list.append(special_event_service.special_by_self(player))

        # Alex Mercer
        if player_event_name == 'Alex-Mercer':
            message_list.append(special_event_service.special_by_alex_mercer(room, player))

        # 你知道的，这是交易
        if player_event_name == 'This-Is-The-Deal':
            message_list.append(special_event_service.special_by_you_know(room, player))

        # 以守护之名
        if player_event_name == 'In-The-Name-of-Preservation':
            message_list.append(special_event_service.special_by_preservation(room, player))

        # 苦尽甘来
        if player_event_name == 'Sweet-After-Bitter':
            for sab_card in player.sab_list:
                message_list += card_service.delete_card(room, player, sab_card)

            player.sab_list = []
            message_list.append(Message().success("special.message.sweetAfterBitterText02"))

            for _ in range(3):
                random_type = [
                    CardType.MicroGain.name,
                    CardType.StrongGain.name,
                    CardType.Opportunity.name
                ]

                message_list += card_service.get_random_card(room, player, random.choice(random_type))

        # 开摆
        if player_event_name == 'Open1':
            player.give_up = False
            player.player_money += 6
            player.draw_count += 2
            message_list.append(Message().success("special.message.open1Text01"))

        # 风险转化
        if player_event_name == 'Risk-Transformation':
            transform_count = 0

            for card_type, card_list in player.deck_list.items():
                for card in card_list:
                    if card.card_type == CardType.MicroDiscomfort.name:
                        transform_count += 1
                        message_list += card_service.delete_card(room, player, card)
                    if card.card_type == CardType.StrongDiscomfort.name:
                        transform_count += 2
                        message_list += card_service.delete_card(room, player, card)
                    if card.card_type == CardType.Unacceptable.name:
                        transform_count += 4
                        message_list += card_service.delete_card(room, player, card)

            if transform_count > 7:
                transform_count = 7

            for _ in range(transform_count):
                random_type = [
                    CardType.MicroGain.name,
                    CardType.StrongGain.name,
                    CardType.Opportunity.name
                ]
                message_list += card_service.get_random_card(room, player, random.choice(random_type))


        # 完成事件奖励
        random_event_type = ['water', 'drawCount', 'money']
        random_event = random.choice(random_event_type)

        if random_event == 'water':
            water_item_list = [item for item in room.shop_config.shop_item_list if item.kind == 'water']
            water_item = random.choice(water_item_list)
            player.backpack.append(water_item)
            message = Message().success('playerEvent.message.successText02')
            message.event_type = 'playerEvent'
            message.to = player.sid
            message.message_data = {
                'playerEventName': f'playerEventList.{player_event.item_name}.name',
                'water': water_item.item_name
            }
            message_list.append(message)
        elif random_event == 'drawCount':
            draw_count = random.randint(1, 2)
            player.draw_count += draw_count
            message = Message().success('playerEvent.message.successText03')
            message.event_type = 'playerEvent'
            message.to = player.sid
            message.message_data = {
                'playerEventName': f'playerEventList.{player_event.item_name}.name',
                'drawCount': draw_count
            }
            message_list.append(message)
        elif random_event == 'money':
            player_money = random.randint(1, 3)
            player.player_money += player_money
            message = Message().success('playerEvent.message.successText04')
            message.event_type = 'playerEvent'
            message.to = player.sid
            message.message_data = {
                'playerEventName': f'playerEventList.{player_event.item_name}.name',
                'playerMoney': player_money
            }
            message_list.append(message)

        player.player_event_list.remove_event(player_event)

        return message_list

    # 放弃个人事件
    @classmethod
    def drop_player_event(cls, player: Player, event_index: int):

        player_event = player.player_event_list.get_event(event_index)
        player.player_event_list.remove_event(player_event)

        delete_money = random.randint(3, 5)
        player.player_money -= delete_money

        message = Message().error(message='playerEvent.message.errorText01')
        message.event_type = 'playerEvent'
        message.message_data = {
            'playerEventName': f'playerEventList.{player_event.item_name}.name',
            'playerMoney': delete_money
        }

        return message

    # 生成个人事件
    @classmethod
    def generate_player_event(cls, room: Room):
        # 获取个人事件
        player_event_list = room.game_config.player_event_list

        # 设置玩家事件
        for player in room.player_list.all_players():
            player_event: PlayerEvent = lottery_by_count(player_event_list)
            player_event.count -= 1
            player.player_event_list.add_event(player_event)
