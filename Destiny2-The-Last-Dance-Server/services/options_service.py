import random
from typing import List

from entitys.game.player import Player
from entitys.message import Message
from entitys.game.room import RoomStage, Room
from entitys.sql.card import CardType
from entitys.sql.raid_map import RaidMap
from services.card.card_service import CardService
from services.global_event_service import GlobalEventService
from services.player_event_service import PlayerEventService
from utils import debug

card_service = CardService()

class OptionsService:

    # 获取地图
    @classmethod
    def get_map_list(cls, room):
        message = Message()
        message.event_type = 'getMapList'
        message.data = {
            'mapList': [raid_map.to_dict() for raid_map in room.game_config.raid_list]
        }
        return message

    # 选择地图
    @classmethod
    def select_map(cls, room, map_id):
        # 搜索地图信息并返回
        raid_list: List[RaidMap] = room.game_config.raid_list

        raid = next((raid for raid in raid_list if raid.raid_id == map_id), None)
        if raid is not None:
            room.raid_config = raid

            # 更新玩家隐藏箱数量
            for player in room.player_list.all_players():
                player.raid_chest = 0

            room.room_stage = RoomStage.NEXT

            message = Message().success(message = 'options.message.successText01')
            message.message_data = {
                'raidName': raid.raid_name
            }
        else:
            message = Message().error(message = 'options.message.errorText01')
            message.message_data = {
                'mapId': map_id
            }
        return message

    # 抵达遭遇战插旗点
    @classmethod
    def map_door(cls, room: Room):
        # 设置状态
        room.room_stage = RoomStage.NEXT

        # 添加抽卡次数
        for player in room.player_list.all_players():
            player.draw_count += 2

        # 添加商店刷新次数
        if room.shop_config.refresh_count == 0:
            room.shop_config.refresh_count = 1

        # 生成个人事件
        player_event_service = PlayerEventService()
        player_event_service.generate_player_event(room)

        # 生成全局事件
        global_event_service = GlobalEventService()
        global_event_service.generate_global_event(room)

        message_list = []

        message = Message().success(message='options.message.successText02')

        message_list.append(message)

        # TODO 命定混沌事件
        # if room.random_seats:
        #     shuffled_numbers = random.sample(range(1, 7), 6)
        #     for player, number in zip(room.player_list.all_players(), shuffled_numbers):
        #         player.role_id = number
        #
        #     message = Message().warning(message='options.message.warningText02')
        #     message_list.append(message)

        return message_list

    # 遭遇战通关
    @classmethod
    def map_next(cls, room: Room):
        # 获取突袭信息
        raid_config: RaidMap = room.raid_config
        level_point = raid_config.raid_level
        level_point_now = raid_config.raid_level_point

        message_list = []

        # 判断当前关卡
        if level_point_now < level_point:
            level_point_now += 1
            raid_config.raid_level_point = level_point_now
            room.room_stage = RoomStage.DOOR

            if level_point_now == 1:
                return message_list

            # 玩家事件处理
            for player in room.player_list.all_players():
                player_money = random.randint(1, 3)
                player.player_money += player_money
                sid = player.sid

                # 免死金牌
                if not player.player_attributes['compensate']:
                    debuff_count = 0

                    # 负面补偿
                    md_count = len(player.deck_list.get_card_type_list(CardType.MicroDiscomfort.name))
                    sd_count = len(player.deck_list.get_card_type_list(CardType.StrongDiscomfort.name))
                    u_count = len(player.deck_list.get_card_type_list(CardType.Unacceptable.name))

                    debuff_count += md_count
                    debuff_count += sd_count * 2
                    debuff_count += u_count * 3

                    if debuff_count > 0:
                        player.player_money += debuff_count
                        message = Message().warning('options.message.warningText03')
                        message.message_data = {
                            'debuffCount': debuff_count
                        }
                        message.to = player.sid
                        message_list.append(message)

                # 这不是很简单吗
                if player.player_attributes['easy']:
                    count = raid_config.raid_level_point - 1

                    for _ in range(count):
                        card_type = random.choice([CardType.MicroGain.name,
                                                   CardType.StrongGain.name,
                                                   CardType.Opportunity.name])
                        message_list += card_service.get_random_card(room, player, card_type)

                    message = Message().warning("options.message.warningText04")
                    message.message_data = {
                        'count': count
                    }
                    message.to = player.sid
                    message_list.append(message)

                # 重重难关
                if player.player_attributes['difficult'] and not player.player_attributes['compensate']:
                    count = raid_config.raid_level_point - 1

                    for _ in range(count):
                        card_type = random.choice([CardType.MicroDiscomfort.name,
                                                   CardType.StrongDiscomfort.name,
                                                   CardType.Unacceptable.name])
                        message_list += card_service.get_random_card(room, player, card_type)

                    message = Message().warning("options.message.warningText05")
                    message.message_data = {
                        'count': count
                    }
                    message.to = player.sid
                    message_list.append(message)

                # 堕落之血
                if player.player_attributes['blood'] and not player.player_attributes['compensate']:
                    all_deck_list = []

                    for type_name, card_list in player.deck_list.items():
                        if (type_name == CardType.MicroDiscomfort.name
                            or type_name == CardType.StrongDiscomfort.name
                            or type_name == CardType.Unacceptable.name):
                            for card in card_list:
                                if card.card_name != 'Corrupted-Blood' and card.card_label != 'ai':
                                    all_deck_list.append(card)

                    if len(all_deck_list) > 0:
                        random_player = random.choice([p for p in room.player_list.all_players()
                                                       if p.player_name != player.player_name])

                        random_card = random.choice(all_deck_list)

                        message_list += card_service.save_card(room, random_player, random_card)

                        message = Message().warning("options.message.warningText06")
                        message.message_data = {
                            'cardName': f'cardList.{random_card.item_name}.name',
                            'playerName': random_player.player_name,
                        }
                        message.to = player.sid
                        message_list.append(message)

                        message = Message().warning("options.message.warningText07")
                        message.message_data = {
                            'cardName': f'cardList.{random_card.item_name}.name',
                            'playerName': player.player_name
                        }
                        message.to = random_player.sid
                        message_list.append(message)
                    else:
                        message = Message().warning("options.message.warningText08")
                        message.to = player.sid
                        message_list.append(message)

                message = Message().success(message='options.message.successText03')
                message.to = sid
                message.message_data = {
                    'playerMoney': player_money
                }
                message_list.append(message)
        else:
            message = Message().error(message='options.message.errorText02')
            message_list.append(message)

        return message_list

    # 获取隐藏箱
    @classmethod
    def get_chest(cls, room, player):
        # 获取突袭信息
        raid_config: RaidMap = room.raid_config
        chest_point = raid_config.raid_chest

        # 判断隐藏箱数量
        if player.raid_chest < chest_point:
            player_money = random.randint(1, 3)
            player.raid_chest += 1
            player.player_money += player_money

            message = Message().success(message='options.message.successText04')
            message.message_data = {
                'playerMoney': player_money
            }
        else:
            message = Message().error(message='options.message.errorText03')

        return message

    # 设置玩家抽卡和货币数量
    @classmethod
    def player_setting(cls, room, player, setting_type, setting_count):

        if setting_type == 'drawCard':
            player.draw_count = setting_count

        if setting_type == 'playerMoney':
            player.player_money = setting_count

        return Message()

    # 无瑕通关
    @classmethod
    def flawless(cls, room):
        for player in room.player_list.all_players():
            player.player_money += 6

        message = Message().success(message='options.message.successText05')
        return message

    # 净化
    @classmethod
    def purify(cls, room: Room):

        players = room.player_list.all_players()

        message_list = []
        player_list: list[Player] = []

        for player in players:

            player_deck_list_count = {
                CardType.MicroDiscomfort: len(player.deck_list.get_card_type_list(CardType.MicroDiscomfort.name)),
                CardType.StrongDiscomfort: len(player.deck_list.get_card_type_list(CardType.StrongDiscomfort.name)),
                CardType.Unacceptable: len(player.deck_list.get_card_type_list(CardType.Unacceptable.name))
            }

            debug(f"{player.player_name} - {player_deck_list_count}")

            if (player_deck_list_count[CardType.MicroDiscomfort] > 0
                    or player_deck_list_count[CardType.StrongDiscomfort] > 0
                    or player_deck_list_count[CardType.Unacceptable] > 0):
                player_list.append(player)

        if len(player_list) > 0:
            player_deck_list = []
            random_player = random.choice(player_list)

            for card_type, card_list in random_player.deck_list.items():
                if (card_type == CardType.MicroDiscomfort.name
                    or card_type == CardType.StrongDiscomfort.name
                    or card_type == CardType.Unacceptable.name):

                    for card in card_list:
                        player_deck_list.append(card)

            random_card = random.choice(player_deck_list)
            message_list = card_service.delete_card(room, random_player, random_card)

            message = Message().success("options.message.successText06")
            message.message_data = {
                'playerName': random_player.player_name,
            }
            message_list.append(message)
        else:
            message = Message().warning("options.message.warningText01")
            message_list.append(message)

        return message_list