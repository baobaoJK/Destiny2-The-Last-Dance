import random

from entitys.game.player import Player
from entitys.game.room import Room
from entitys.game.shop import ShopConfig, ShopRefreshType
from entitys.message import Message
from entitys.sql.card import CardType
from entitys.sql.shop.shop import ShopItem
from services.card.card_service import CardService
from utils import debug
from utils.tools.lottery import lottery

card_service = CardService()


class ShopService:

    # 刷新商店
    @classmethod
    def refresh_shop(cls, room: Room):
        message_list = []
        shop_config: ShopConfig = room.shop_config

        refresh_mod = ShopRefreshType.FREE if shop_config.refresh_count >= 1 else ShopRefreshType.PAY

        # 判断刷新类型
        if refresh_mod is ShopRefreshType.PAY:
            need_money = shop_config.refresh_money // 6
            for player in room.player_list.all_players():
                if player.player_money < need_money:
                    message = Message().error("shop.message.errorText01")
                    message_list.append(message)
                    return message_list

            for player in room.player_list.all_players():
                player.player_money -= need_money

            shop_config.refresh_money += 6

            message = Message().warning("shop.message.warningText01")
            message.message_data = {
                'needMoney': need_money,
            }
            message_list.append(message)
        else:
            shop_config.refresh_count -= 1

        # 重置商店列表
        shop_config.item_list = []
        shop_config.weapon_list = []
        shop_config.exotic_list = []

        # 物品列表
        for _ in range(9):
            item_list = [item for item in shop_config.shop_item_list if item.type_name == 'water']
            item = lottery(item_list)
            item.count = 1
            shop_config.item_list.append(item)

        card_item = (next(item for item in shop_config.shop_item_list if item.type_name == 'drawCount'), None)
        card_item[0].count = random.randint(3, 6)
        shop_config.item_list.append(card_item[0])

        # 武器列表
        for _ in range(10):
            weapon_list = [weapon for weapon in shop_config.shop_item_list if weapon.type_name == 'weapon']
            weapon = lottery(weapon_list)
            weapon.count = 1
            shop_config.weapon_list.append(weapon)

        # 异域装备列表（武器）
        while len(shop_config.exotic_list) < 4:
            exotic_weapon = lottery(shop_config.exotic_weapon_list)
            if not (exotic_weapon in shop_config.exotic_list):
                exotic_weapon.count = 2
                shop_config.exotic_list.append(exotic_weapon)

        # 异域装备列表（护甲）
        while len(shop_config.exotic_list) < 10:
            exotic_armor = lottery(shop_config.exotic_armor_list)

            # 根据玩家角色抽取
            players = room.player_list.all_players()
            player = random.choice(players)
            player_role = 0
            if player is not None:
                player_role = player.role
                player_role = str(player_role).capitalize()

            if not exotic_armor in shop_config.exotic_list and player is None:
                exotic_armor.count = 2
                shop_config.exotic_list.append(exotic_armor)
            elif not exotic_armor in shop_config.exotic_list and exotic_armor.role == player_role:
                exotic_armor.count = 2
                shop_config.exotic_list.append(exotic_armor)

        message = Message().success("shop.message.successText01")
        message_list.append(message)
        return message_list

        # 购买物品
    def buy_item(self, room: Room, player: Player, type_list: str, item_index: int):
        message_list = []
        shop_config: ShopConfig = room.shop_config

        item: ShopItem | None = None
        if type_list == 'itemList':
            item = shop_config.item_list[item_index]
        elif type_list == 'weaponList':
            item = shop_config.weapon_list[item_index]
        elif type_list == 'exoticList':
            item = shop_config.exotic_list[item_index]

        sell = item.sell

        # 零元购
        if player.zero_buy > 0:
            player.zero_buy -= 1
            sell = 0
            message = Message.warning("shop.message.warningText04")
            message.message_data = {
                'playerName': player.player_name,
            }
            message_list.append(message)
        # 纨绔子弟
        if player.player_attributes['profiteer'] and player.zero_buy <= 0:
            sell += 1
        # 促销
        if player.player_attributes['promotions'] and player.zero_buy <= 0:
            sell = sell / 2

        # 货币检测
        if player.player_money < sell and player.zero_buy <= 0 and not player.player_attributes['market']:
            message = Message().error("shop.message.errorText02")
            message.to = player.sid
            message_list.append(message)
            return message_list

        # 未来市场
        if player.player_attributes['market'] and item.type_name == 'water':
            message = Message().error("shop.message.errorText05")
            message.to = player.sid
            message_list.append(message)
            return message_list

        if item.type_name == 'water':
            message_list.append(self.buy_water(room, player, item, item_index, sell))
        elif item.type_name == 'drawCount':
            message_list.append(self.buy_draw_count(room, player, item_index, sell))
        elif item.type_name == 'weapon':
            message_list += self.buy_weapon(room, player, item, item_index, sell)
        elif item.type_name == 'weapons' or item.type_name == 'armor':
            message_list += self.buy_exotic_item(room, player, item, item_index, sell)

        message = Message().warning("shop.message.warningText02")
        message.event_type = 'shopItem'
        message.message_data = {
            'playerName': player.player_name,
            'itemName': f'item.{item.item_name}.name',
        }
        message_list.append(message)
        return message_list

    # 购买圣水
    @classmethod
    def buy_water(cls, room: Room, player: Player, item: ShopItem, item_index: int, sell: int):
        shop_config = room.shop_config

        del shop_config.item_list[item_index]
        player.backpack.append(item)
        player.player_money -= sell

        message = Message().success("shop.message.successText02")
        message.to = player.sid
        return message

    # 购买抽卡次数
    @classmethod
    def buy_draw_count(cls, room: Room, player: Player, item_index: int, sell: int):
        shop_config: ShopConfig = room.shop_config

        shop_config.item_list[item_index].count -= 1
        if shop_config.item_list[item_index].count == 0:
            del shop_config.item_list[item_index]

        player.draw_count += 1
        player.player_money -= sell

        message = Message().success("shop.message.successText03")
        message.to = player.sid
        return message

    # 购买武器
    @classmethod
    def buy_weapon(cls, room: Room, player: Player, item: ShopItem, item_index: int, sell: int):
        message_list = []
        shop_config: ShopConfig = room.shop_config

        del shop_config.weapon_list[item_index]

        player.backpack.append(item)
        player.player_money -= sell

        # 恶魔契约
        if player.devilspact != 0:
            player.devilspact -= 1
            player.draw_count += 1
            message = Message().success("shop.message.successText05")
            message.to = player.sid
            message_list.append(message)

        message = Message().success("shop.message.successText04")
        message.event_type = 'shopItem'
        message.message_data = {
            'itemName': f'item.{item.item_name}.name'
        }
        message.to = player.sid
        message_list.append(message)
        return message_list

    # 购买异域装备
    @classmethod
    def buy_exotic_item(cls, room: Room, player: Player, item: ShopItem, item_index: int, sell: int):
        message_list = []
        shop_config: ShopConfig = room.shop_config

        shop_config.exotic_list[item_index].count-= 1
        if shop_config.exotic_list[item_index].count == 0:
            del shop_config.exotic_list[item_index]

        player.backpack.append(item)
        player.player_money -= sell

        # 恶魔契约
        if player.devilspact != 0:
            player.devilspact -= 1
            player.draw_count += 1
            message = Message().success("shop.message.successText05")
            message.to = player.sid
            message_list.append(message)

        message = Message().success("shop.message.successText04")
        message.event_type = 'shopItem'
        message.message_data = {
            'itemName': f'item.{item.item_name}.name'
        }
        message.to = player.sid
        message_list.append(message)
        return message_list

    # 开启商店
    @classmethod
    def open_shop(cls, room: Room, player: Player):

        # 判断玩家货币是否充足
        if player.player_money < 12:
            message = Message().error("shop.message.errorText06")
            return message

        player.player_money -= 12

        card_item = card_service.find_card_by_name_in_player_deck_list(player, 'Stillwater-Prison')

        card_service.delete_card(room, player, card_item)

        message = Message().success("shop.message.successText06")
        return message

    # 使用圣水
    @classmethod
    def use_item(cls, player: Player, backpack_index):
        item: ShopItem = player.backpack[backpack_index]

        if item.type_name != 'water':
            return Message().error("shop.message.errorText03")

        deck_list = []

        # 十三幺判断
        if item.item_name == 'water1' and not player.player_attributes['thirteen']:
            deck_list = player.deck_list.get_card_type_list(CardType.MicroDiscomfort.name)
        elif item.item_name == 'water2' and not player.player_attributes['thirteen']:
            deck_list = player.deck_list.get_card_type_list(CardType.StrongDiscomfort.name)
        elif item.item_name == 'water3' and not player.player_attributes['thirteen']:
            deck_list = player.deck_list.get_card_type_list(CardType.Unacceptable.name)
        elif item.item_name == 'water7':
            deck_list = player.deck_list.get_card_type_list(CardType.Technology.name)

        if len(deck_list) <= 0:
            return Message().error("shop.message.errorText04")

        message = Message().warning("shop.message.warningText03")
        message.data = {
            'deckList': [card.to_dict() for card in deck_list]
        }
        return message

    # 删除卡牌
    @classmethod
    def delete_card_item(cls, room: Room, player: Player, card_type: CardType, card_index: int, backpack_index: int):
        message_list = []

        card = player.deck_list.get_card_type_list(card_type)[card_index]

        message_list += card_service.delete_card(room, player, card)

        del player.backpack[backpack_index]

        return message_list