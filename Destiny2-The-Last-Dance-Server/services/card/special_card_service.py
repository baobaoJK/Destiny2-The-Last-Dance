import math
import random

from entitys.game.player import Player
from entitys.game.room import Room
from entitys.message import Message
from entitys.sql.card import Card, thirteen_list, CardType
from utils import debug


class SpecialCardService:
    @classmethod
    def special_card(cls, room: Room, player: Player, card: Card):
        from services.card.card_service import CardService
        from services.special_event.special_card_service import SpecialCardService
        card_service = CardService()
        special_card_service = SpecialCardService()

        card_name = card.card_name

        players_id = random.choices([target_player.role_id for target_player in room.player_list.all_players()
                                     if target_player is not None and player.role_id != target_player.role_id])

        # players_id = [1]
        message_list = []
        # -------------------------------------------
        # 特殊效果
        # -------------------------------------------
        # 不吃这套
        if player.player_attributes['noDeal']:
            if (card.card_type == CardType.MicroDiscomfort.name
                or card.card_type == CardType.StrongDiscomfort.name
                or card.card_type == CardType.Unacceptable.name):

                no_deal_card = player.deck_list.get_card_by_name(CardType.Technology.name, 'I-Wont-Eat-This')
                message_list += card_service.delete_card(room, player, card)
                message_list += card_service.delete_card(room, player, no_deal_card)
                message = Message().warning('special.message.noDealText01')
                message.event_type = 'specialCard'
                message.message_data = {
                    'specialCardName': f'cardList.{no_deal_card.item_name}.name'
                }
                message_list.append(message)
        # 不是哥们
        if player.player_attributes['noBuddy']:
            if (card.card_type == CardType.MicroGain.name
                or card.card_type == CardType.StrongGain.name
                or card.card_type == CardType.Opportunity.name):

                no_buddy_card = player.deck_list.get_card_by_name(CardType.Technology.name, 'No-Buddy')
                message_list += card_service.delete_card(room, player, card)
                message_list += card_service.delete_card(room, player, no_buddy_card)
                message = Message().warning('special.message.noBuddyText01')
                message.event_type = 'specialCard'
                message.message_data = {
                    'specialCardName': f'cardList.{no_buddy_card.item_name}.name'
                }
                message_list.append(message)

        # 卡牌抵消
        if player.player_attributes['counteract']:
            card_1 = player.deck_list.get_card_by_name(CardType.Opportunity.name, 'The-Medallion')
            card_2 = player.deck_list.get_card_by_name(CardType.Unacceptable.name, 'Imperial-Ban')

            message_list += card_service.delete_card(room, player, card_1)
            message_list += card_service.delete_card(room, player, card_2)

            message = Message().warning('special.message.counteractText01')
            message_list.append(message)

        # -------------------------------------------
        # 欧皇增益
        # -------------------------------------------
        # 这不是很简单吗
        if card_name == 'Easy':
            count = room.raid_config.raid_level_point

            for _ in range(count):
                card_type = random.choice([CardType.MicroGain.name,
                                           CardType.StrongGain.name,
                                           CardType.Opportunity.name])
                message_list += card_service.get_random_card(room, player, card_type)

                message = Message().warning("special.message.easyText01")
                message.message_data = {
                    'count': count
                }
                message_list.append(message)
        # -------------------------------------------
        # 反人类
        # -------------------------------------------
        # 重重难关
        if card_name == 'Many-Difficulties' and not player.player_attributes['compensate']:
            count = room.raid_config.raid_level_point

            for _ in range(count):
                card_type = random.choice([CardType.MicroDiscomfort.name,
                                           CardType.StrongDiscomfort.name,
                                           CardType.Unacceptable.name])
                message_list += card_service.get_random_card(room, player, card_type)

            message = Message().warning("special.message.manyDifficultiesText01")
            message.message_data = {
                'count': count
            }
            message_list.append(message)

        # 舍己为人
        if card_name == 'Altruism' and not player.player_attributes['compensate']:
            deck_list = set()

            for target_player in room.player_list.all_players():
                if target_player.player_attributes['thirteen'] or player.role_id == target_player.role_id:
                    continue

                for card_type, card_list in target_player.deck_list.items():
                    if (card_type == CardType.MicroDiscomfort.name
                        or card_type == CardType.StrongDiscomfort.name
                        or card_type == CardType.Unacceptable.name):

                        cards_to_remove = card_list[:]

                        for card in cards_to_remove:
                            deck_list.add(card)

                            message_list += card_service.delete_card(room, target_player, card)

                message = Message().warning("special.message.altruismText01")
                message.message_data = {
                    'playerName': player.player_name
                }
                message.to = target_player.sid
                message_list.append(message)
            for card in deck_list:
                message_list += card_service.save_card(room, player, card)

            message = Message().warning("special.message.altruismText02")
            message.to = player.sid
            message_list.append(message)

        # 堕落之血
        if card_name == 'Corrupted-Blood':
            message_list.append(Message().warning("special.message.corruptedBloodText01"))

        # -------------------------------------------
        # 重度不适
        # -------------------------------------------
        # 杂鱼
        if card_name == 'Lost-Wallet':
            player.deck_list.remove_card(card)
            player.player_money = 0
            message_list.append(Message().warning("special.message.lostWalletText01"))

        # -------------------------------------------
        # 特殊卡牌
        # -------------------------------------------

        # 收过路费
        if card_name == 'Capitalism':
            player.deck_list.remove_card(card)
            player_1_role_id = player.role_id + 2 - 6 if player.role_id + 2 > 6 else player.role_id + 2
            player_2_role_id = player.role_id - 2 + 6 if player.role_id - 2 < 1 else player.role_id - 2

            player_1 = room.player_list.get_player_by_id(player_1_role_id)
            player_2 = room.player_list.get_player_by_id(player_2_role_id)

            player_1_money = math.ceil(player_1.player_money / 2)
            player_2_money = math.ceil(player_2.player_money / 2)

            player_1.player_money = player_1.player_money - player_1_money
            player_2.player_money = player_2.player_money - player_2_money

            player.player_money += (player_1_money + player_2_money)

            message = Message().warning('special.message.capitalismText01')
            message.message_data = {
                'player1Id':  player_1_role_id,
                'player2Id': player_2_role_id
            }
            message_list.append(message)

            message = Message().warning('special.message.capitalismText02')
            message.message_data = {
                'playerId': player.role_id,
                'playerMoney': player_1_money
            }
            message.to = player_1.sid
            message_list.append(message)

            message = Message().warning('special.message.capitalismText02')
            message.message_data = {
                'playerId': player.role_id,
                'playerMoney': player_2_money
            }
            message.to = player_2.sid
            message_list.append(message)

        # 生财有道
        if card_name == 'Make-Wealth':
            player.deck_list.remove_card(card)
            player.player_money += 6
            message_list.append(Message().warning("special.message.makeWealthText01"))

        # 起手换牌
        if card_name == 'Change-Card':
            player.deck_list.remove_card(card)

            draw_count = 0
            for card_type, card_list in player.deck_list.items():
                cards_to_remove = card_list[:]

                for card in cards_to_remove:
                    draw_count += 1
                    message_list += card_service.delete_card(room, player, card)

            player.draw_count += draw_count

            message = Message().warning("special.message.changeCardText01")
            message.message_data = {
                'count': draw_count
            }
            message_list.append(message)

        # 恶魔契约
        if card_name == 'Devils-Pact':
            player.deck_list.remove_card(card)
            player.devilspact = 2
            message = Message().warning('special.message.devilsPactText01')
            message_list.append(message)

        # 上贡
        if card_name == 'Tribute':
            player.deck_list.remove_card(card)
            player.special_config.send = player.role_id
            player.special_config.to = players_id[0]
            message_list.append(special_card_service.special_by_tribute(room, player))

        # 决斗
        if card_name == 'Duel':
            player.deck_list.remove_card(card)
            message = Message().warning('special.message.duelText01')
            message.message_data = {
                'playerId': player.role_id
            }
            message_list.append(message)

        # 等价交换
        if card_name == 'Equivalent-Exchange':
            player.deck_list.remove_card(card)
            change_player = room.player_list.get_player_by_id(players_id[0])

            message = Message().warning('special.message.equivalentExchangeText01')
            message.message_data = {
                'playerId': players_id[0]
            }
            message_list.append(message)

            message = Message().warning('special.message.equivalentExchangeText02')
            message.message_data = {
                'playerId': player.role_id
            }
            message.to = change_player.sid
            message_list.append(message)

            if change_player is not None:
                player_deck_list = []
                change_player_deck_list = []

                # 删除卡牌
                for card_type, card_list in player.deck_list.items():
                    for card in card_list:
                        player_deck_list.append(card)
                        message_list += card_service.delete_card(room, player, card)

                for card_type, card_list in change_player.deck_list.items():
                    for card in card_list:
                        change_player_deck_list.append(card)
                        message_list += card_service.delete_card(room, change_player, card)

                # 添加卡牌
                for card in player_deck_list:
                    message_list += card_service.save_card(room, change_player, card)

                for card in change_player_deck_list:
                    message_list += card_service.save_card(room, player, card)

        # 有福同享
        if card_name == 'Blessed-To-Share':
            player.deck_list.remove_card(card)
            and_player = room.player_list.get_player_by_id(players_id[0])

            if and_player is not None:
                player.blessing = players_id[0]
                and_player.blessing = player.role_id

                and_player_micro_gain_deck_list = and_player.deck_list.get_card_type_list(CardType.MicroGain.name)
                for card in and_player_micro_gain_deck_list:
                    player.deck_list.add_card(card)

                and_player_strong_gain_deck_list = and_player.deck_list.get_card_type_list(CardType.StrongGain.name)
                for card in and_player_strong_gain_deck_list:
                    player.deck_list.add_card(card)

                and_player_opportunity_deck_list = and_player.deck_list.get_card_type_list(CardType.Opportunity.name)
                for card in and_player_opportunity_deck_list:
                    player.deck_list.add_card(card)

                and_player.deck_list.set_card_type_list(CardType.MicroGain, player.deck_list.get_card_type_list(CardType.MicroGain.name))
                and_player.deck_list.set_card_type_list(CardType.StrongGain, player.deck_list.get_card_type_list(CardType.StrongGain.name))
                and_player.deck_list.set_card_type_list(CardType.Opportunity, player.deck_list.get_card_type_list(CardType.Opportunity.name))

                message = Message().warning('special.message.blessedToShareText01')
                message.message_data = {
                    'playerName': and_player.player_name
                }
                message_list.append(message)

                and_player_message = Message().warning('special.message.blessedToShareText02')
                and_player_message.message_data = {
                    'playerName': player.player_name
                }
                and_player_message.to = and_player.sid
                message_list.append(and_player_message)

        # 有难同当
        if card_name == 'Share-The-Difficulties':
            player.deck_list.remove_card(card)
            and_player = room.player_list.get_player_by_id(players_id[0])

            if and_player is not None:
                player.disaster = players_id[0]
                and_player.disaster = player.role_id

                and_player_micro_micro_discomfort_deck_list = and_player.deck_list.get_card_type_list(CardType.MicroDiscomfort.name)
                for card in and_player_micro_micro_discomfort_deck_list:
                    player.deck_list.add_card(card)

                and_player_strong_discomfort_deck_list = and_player.deck_list.get_card_type_list(CardType.StrongDiscomfort.name)
                for card in and_player_strong_discomfort_deck_list:
                    player.deck_list.add_card(card)

                and_player_unacceptable_deck_list = and_player.deck_list.get_card_type_list(CardType.Unacceptable.name)
                for card in and_player_unacceptable_deck_list:
                    player.deck_list.add_card(card)

                and_player.deck_list.set_card_type_list(CardType.MicroDiscomfort, player.deck_list.get_card_type_list(CardType.MicroDiscomfort.name))
                and_player.deck_list.set_card_type_list(CardType.StrongDiscomfort, player.deck_list.get_card_type_list(CardType.StrongDiscomfort.name))
                and_player.deck_list.set_card_type_list(CardType.Unacceptable, player.deck_list.get_card_type_list(CardType.Unacceptable.name))

                message = Message().warning('special.message.shareTheDifficultiesText01')
                message.message_data = {
                    'playerName': and_player.player_name
                }
                message_list.append(message)

                and_player_message = Message().warning('special.message.shareTheDifficultiesText02')
                and_player_message.message_data = {
                    'playerName': player.player_name
                }
                and_player_message.to = and_player.sid
                message_list.append(and_player_message)

        # 鱿鱼游戏
        if card_name == 'Squid-Game':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 赌徒
        if card_name == 'Gambler':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 十三幺
        if card_name == 'Thirteen-Orphans':
            player.deck_list.clear()

            for thirteen_card_name in thirteen_list:
                card_item = next((card for card in room.game_config.card_list if card.card_name == thirteen_card_name), None)
                player.deck_list.add_card(card_item)

            player.deck_list.add_card(card)
            message_list.append(Message().warning('special.message.thirteenOrphans'))

        # 欧皇附体
        if card_name == 'Lucky-Man':
            player.deck_list.remove_card(card)
            message_list.append(Message().warning('special.message.luckyManText01'))

        # 倒霉蛋
        if card_name == 'Unlucky-Man':
            player.deck_list.remove_card(card)
            message_list += card_service.get_random_card(room, player, CardType.StrongDiscomfort.name)
            message = Message().warning('special.message.unluckyManText01')
            message_list.append(message)

        # 天选者
        if card_name == 'The-Chosen-One':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 暴君
        if card_name == 'Tyrant':
            player.deck_list.remove_card(card)
            player.special_config.send = player.role_id
            message_list.append(special_card_service.special_by_tyrant(room, player))

        # 天使
        if card_name == 'Angel':
            player.deck_list.remove_card(card)
            message_list.append(Message().warning('special.message.angelText01'))

        # 恶魔
        if card_name == 'Devil':
            player.deck_list.remove_card(card)
            message_list.append(Message().warning('special.message.devilText01'))

        # 未来市场
        if card_name == "Future's-Market":
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 强买强卖
        if card_name == 'Hard-Sells':
            player.deck_list.remove_card(card)
            message_list.append(Message().warning('special.message.hardSellsText01'))

        # 低帧率模式
        if card_name == 'Low-FPS':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 你在逗我吗?
        if card_name == 'Are-You-Kidding-Me':
            player.deck_list.remove_card(card)

            list_number = [0, 0, 0, 0, 0, 0]

            for card_type, card_list in player.deck_list.items():
                cards_to_remove = card_list[:]
                for card_item in cards_to_remove:
                    if card_item.card_type == CardType.MicroGain.name:
                        list_number[0] += 1
                    elif card_item.card_type == CardType.StrongGain.name:
                        list_number[1] += 1
                    elif card_item.card_type == CardType.Opportunity.name:
                        list_number[2] += 1
                    elif card_item.card_type == CardType.MicroDiscomfort.name:
                        list_number[3] += 1
                    elif card_item.card_type == CardType.StrongDiscomfort.name:
                        list_number[4] += 1
                    elif card_item.card_type == CardType.Unacceptable.name:
                        list_number[5] += 1

                    message_list += card_service.delete_card(room, player, card_item)

            for index, i in enumerate(list_number):
                card_type_list = [
                    CardType.MicroDiscomfort.name,
                    CardType.StrongDiscomfort.name,
                    CardType.Unacceptable.name,
                    CardType.MicroGain.name,
                    CardType.StrongGain.name,
                    CardType.Opportunity.name
                ]
                for _ in range(list_number[index]):
                    message_list += card_service.get_random_card(room, player, card_type_list[index])
                    index += 1

            message = Message().warning('special.message.areYouKiddingMeText01')
            message.message_data = {
                'cardListNumber1': list_number[0],
                'cardListNumber2': list_number[1],
                'cardListNumber3': list_number[2],
                'cardListNumber4': list_number[3],
                'cardListNumber5': list_number[4],
                'cardListNumber6': list_number[5]
            }
            message_list.append(message)

        # 力量的代价
        if card_name == 'The-Price-of-Power':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 苦肉计
        if card_name == 'The-Self-Torture-Scheme':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 这不是个人恩怨
        if card_name == 'This-isnt-a-Personal':
            player.deck_list.remove_card(card)
            message_list.append(special_card_service.special_by_personal(room, player))

        # 不，你不能
        if card_name == 'You-Cant':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 忘了就是开了？
        if card_name == 'Forget':
            player.deck_list.remove_card(card)
            player.draw_count += 1
            message_list += card_service.get_random_card(room, player, CardType.MicroGain.name)
            message_list.append(Message().warning('special.message.forgetText01'))

        # 光能庇护
        if card_name == 'Light-Blessing':
            player.deck_list.remove_card(card)
            for _, card_list in player.deck_list.items():
                cards_to_remove = card_list[:]
                for card_item in cards_to_remove:
                    card_type = card_item.card_type
                    if (card_type == CardType.MicroDiscomfort.name
                        or card_type == CardType.StrongDiscomfort.name
                        or card_type == CardType.Unacceptable.name):
                        message_list += card_service.delete_card(room, player, card_item)
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 观星
        if card_name == 'Stargazing':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 全局 BP
        if card_name == 'Global-BP':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 卡牌回收计划
        if card_name == 'Card-Recycling-Program':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 海马的特殊规则
        if card_name == 'Special-Rules-For-Seahorses':
            player.deck_list.remove_card(card)
            message_list.append(Message().warning('special.message.specialRulesForSeahorsesText01'))

        # 谢谢，不吃这套
        if card_name == 'I-Wont-Eat-This':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 不是，哥们
        if card_name == 'No-Buddy':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 人为财死
        if card_name == 'People-Die-For-Money':
            player.deck_list.remove_card(card)
            player.special_config.send = player.role_id
            message_list.append(special_card_service.special_by_money(room, player))

        # 拉姆蕾萨尔·华伦泰
        if card_name == 'Ramresar-Valentine':
            message_list.append(Message().warning(f'cardList.{card.item_name}.description'))

        # 感觉不如
        if card_name == 'Feeling-Not-As-Good-As':
            player.deck_list.remove_card(card)

            card_count = 0
            for _, card_list in player.deck_list.items():
                cards_to_remove = card_list[:]
                for card_item in cards_to_remove:
                    card_type = card_item.card_type
                    if (card_type == CardType.MicroGain.name
                        or card_type == CardType.StrongGain.name
                        or card_type == CardType.Opportunity.name):
                        card_count += 1
                        message_list += card_service.delete_card(room, player, card_item)

            for _ in range(card_count):
                random_type = random.choice(list(CardType))
                message_list += card_service.get_random_card(room, player, random_type.name)

            message = Message().warning('special.message.feelingNotAsGoodAsText01')
            message.message_data = {
                'cardCount': card_count
            }
            message_list.append(message)

        # 上帝宽恕你
        if card_name == 'God-Forgive-You':
            player.deck_list.remove_card(card)
            card_count = 0

            for card_type, card_list in player.deck_list.items():
                if (card_type == CardType.MicroDiscomfort.name
                    or card_type == CardType.StrongDiscomfort.name
                    or card_type == CardType.Opportunity.name):
                    cards_to_remove = card_list[:]
                    for card_item in cards_to_remove:
                        card_count += 1
                        message_list += card_service.delete_card(room, player, card_item)

            final_count = card_count // 2
            for _ in range(final_count):
                random_type = [
                    CardType.MicroGain.name,
                    CardType.StrongGain.name,
                    CardType.Opportunity.name
                ]
                message_list += card_service.get_random_card(room, player, random.choice(random_type))

            message = Message().warning('special.message.godForgiveYouText01')
            message.message_data = {
                'cardCount': card_count,
                'finalCount': final_count
            }
            message_list.append(message)

        # 忧愁加冕
        if card_name == 'Crowning-Of-Sorrow':
            message_list.append(Message().warning('special.message.crowningOfSorrowText01'))

        # 商店促销
        if card_name == 'Store-Promotions':
            message_list.append(Message().warning('special.message.storePromotionsText01'))

        # 等级提升
        if card_name == 'Level-Up':
            message_list += cls.special_by_level_up(room, player)

        # 分发消息
        return message_list

    # 等级提升
    @classmethod
    def special_by_level_up(cls, room: Room, player: Player):
        from services.card.card_service import CardService

        card_service = CardService()

        message_list = []

        # 判断卡牌升级列表
        card_type_list = [
            CardType.MicroGain.name,
            CardType.StrongGain.name,
            CardType.MicroDiscomfort.name,
            CardType.StrongDiscomfort.name
        ]

        # 判断玩家列表
        for card_type, card_list in player.deck_list.items():
            if card_type in card_type_list:
                # 获取列表长度
                card_list_len = len(card_list)
                # 如果大于等于3执行
                if card_list_len >= 3:
                    # 循环 列表长度 // 3
                    for _ in range(card_list_len // 3):
                        cards_to_remove = card_list[:]
                        for _ in range(3):
                            message_list += card_service.delete_card(room, player, cards_to_remove.pop())
                        if card_type == CardType.MicroGain.name:
                            message_list += card_service.get_random_card(room, player, CardType.StrongGain.name)
                            message_list.append(Message().warning('special.message.levelUpText01'))
                        if card_type == CardType.StrongGain.name:
                            message_list += card_service.get_random_card(room, player, CardType.Opportunity.name)
                            message_list.append(Message().warning('special.message.levelUpText02'))
                        if card_type == CardType.MicroDiscomfort.name:
                            message_list += card_service.get_random_card(room, player, CardType.StrongDiscomfort.name)
                            message_list.append(Message().warning('special.message.levelUpText03'))
                        if card_type == CardType.StrongDiscomfort.name:
                            message_list += card_service.get_random_card(room, player, CardType.Unacceptable.name)
                            message_list.append(Message().warning('special.message.levelUpText04'))

        return message_list
