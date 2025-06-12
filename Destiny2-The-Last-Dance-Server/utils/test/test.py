import json
import re

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from entitys.sql.card import Card
from entitys.sql.global_event import GlobalEvent
from entitys.sql.player_event import PlayerEvent
from entitys.sql.shop.exotic_armor import ExoticArmor
from entitys.sql.shop.exotic_weapon import ExoticWeapon
from entitys.sql.shop.shop import ShopItem
from utils import get_session


# 转换 card_name（大驼峰 + -） 为 camelCase
def to_camel_case(s: str) -> str:
    parts = s.split('-')
    if not parts:
        return s[0].lower() + s[1:] if len(s) > 1 else s.lower()
    return parts[0][0].lower() + parts[0][1:] + ''.join(p.capitalize() for p in parts[1:])

def export_card_list_to_json_zhcn(file_path: str):
    engine = create_engine(f'sqlite:///D:\Project\Web\Destiny2\Destiny2-The-Last-Dance\Destiny2-The-Last-Dance-Server\database/raid.db')
    session = sessionmaker(bind=engine)

    result = {}

    # CardList
    item_list = session().query(Card).all()
    card_list = {}
    for item in item_list:
        card_list[item.item_name] = {
            "name": item.card_cn_name,
            "sub": item.card_name,
            "description": item.card_cn_description or ""
        }
    result['cardList'] = card_list

    # PlayerEventList
    item_list = session().query(PlayerEvent).all()
    player_event_list = {}
    for item in item_list:
        player_event_list[item.item_name] = {
            "name": item.event_cn_name,
            "sub": item.event_name,
            "description": item.event_cn_description or ""
        }
    result['playerEventList'] = player_event_list

    # GlobalEventList
    item_list = session().query(GlobalEvent).all()
    global_event_list = {}
    for item in item_list:
        global_event_list[item.item_name] = {
            "name": item.event_cn_name,
            "sub": item.event_name,
            "description": item.event_cn_description or ""
        }
    result['globalEventList'] = global_event_list

    # ShopItem
    item_list = session().query(ShopItem).all()
    shop_item_list = {}
    for item in item_list:
        shop_item_list[item.item_name] = {
            "name": item.cn_name,
            "rarity": item.rarity,
            "description": item.cn_description
        }

    # ExoticWeapon
    item_list = session().query(ExoticWeapon).all()
    for item in item_list:
        shop_item_list[item.item_name] = {
            "name": item.cn_name,
            "rarity": item.rarity,
            "description": item.cn_description
        }

    # ExoticArmor
    item_list = session().query(ExoticArmor).all()
    for item in item_list:
        shop_item_list[item.item_name] = {
            "name": item.cn_name,
            "rarity": item.rarity,
            "description": item.cn_description
        }

    result['item'] = shop_item_list


    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 已成功导出 {len(result)} 条卡牌信息到 {file_path}")

def export_card_list_to_json_en(file_path: str):
    engine = create_engine(f'sqlite:///D:\Project\Web\Destiny2\Destiny2-The-Last-Dance\Destiny2-The-Last-Dance-Server\database/raid.db')
    session = sessionmaker(bind=engine)

    result = {}

    # CardList
    item_list = session().query(Card).all()
    card_list = {}
    for item in item_list:
        card_list[item.item_name] = {
            "name": item.card_name,
            "sub": item.card_name,
            "description": item.card_description or ""
        }
    result['cardList'] = card_list

    # PlayerEventList
    item_list = session().query(PlayerEvent).all()
    player_event_list = {}
    for item in item_list:
        player_event_list[item.item_name] = {
            "name": item.event_name,
            "sub": item.event_name,
            "description": item.event_description or ""
        }
    result['playerEventList'] = player_event_list

    # GlobalEventList
    item_list = session().query(GlobalEvent).all()
    global_event_list = {}
    for item in item_list:
        global_event_list[item.item_name] = {
            "name": item.event_name,
            "sub": item.event_name,
            "description": item.event_description or ""
        }
    result['globalEventList'] = global_event_list

    # ShopItem
    item_list = session().query(ShopItem).all()
    shop_item_list = {}
    for item in item_list:
        shop_item_list[item.item_name] = {
            "name": item.item_name,
            "rarity": item.rarity,
            "description": item.description
        }

    # ExoticWeapon
    item_list = session().query(ExoticWeapon).all()
    for item in item_list:
        shop_item_list[item.item_name] = {
            "name": item.item_name,
            "rarity": item.rarity,
            "description": item.description
        }

    # ExoticArmor
    item_list = session().query(ExoticArmor).all()
    for item in item_list:
        shop_item_list[item.item_name] = {
            "name": item.item_name,
            "rarity": item.rarity,
            "description": item.description
        }

    result['item'] = shop_item_list


    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 已成功导出 {len(result)} 条卡牌信息到 {file_path}")

if __name__ == "__main__":
    export_card_list_to_json_zhcn("zh_item.json")
    export_card_list_to_json_en("en_item.json")
