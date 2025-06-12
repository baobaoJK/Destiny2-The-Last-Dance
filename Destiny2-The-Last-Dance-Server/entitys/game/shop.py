from enum import Enum

from entitys.sql.shop.exotic_armor import ExoticArmor
from entitys.sql.shop.exotic_weapon import ExoticWeapon
from entitys.sql.shop.shop import ShopItem
from utils.service.sql_connect import get_session

# 商店刷新类型
class ShopRefreshType(Enum):
    FREE = 'FREE'
    PAY = 'PAY'

class ShopConfig:
    def __init__(self):
        self.shop_item_list = self.set_shop_item_list()
        self.exotic_weapon_list = self.set_exotic_weapon_list()
        self.exotic_armor_list = self.set_exotic_armor_list()
        self.item_list: list[ShopItem] = []
        self.weapon_list = []
        self.exotic_list = []
        self.refresh_money = 6
        self.refresh_count = 0

    # 设置商店物品
    @classmethod
    def set_shop_item_list(cls):
        session = get_session()
        sql_shop_item_list = session.query(ShopItem).all()
        return sql_shop_item_list

    # 设置商店异域武器列表
    @classmethod
    def set_exotic_weapon_list(cls):
        session = get_session()
        sql_exotic_weapon_list = session.query(ExoticWeapon).all()
        return sql_exotic_weapon_list

    # 设置商店异域护甲列表
    @classmethod
    def set_exotic_armor_list(cls):
        session = get_session()
        sql_exotic_armor_list = session.query(ExoticArmor).all()
        return sql_exotic_armor_list

    def to_dict(self) -> dict :
        return {
            'itemList': [item.to_dict() for item in self.item_list],
            'weaponList': [weapon.to_dict() for weapon in self.weapon_list],
            'exoticList': [exotic.to_dict() for exotic in self.exotic_list],
            'refreshMoney': self.refresh_money,
            'refreshCount': self.refresh_count
        }