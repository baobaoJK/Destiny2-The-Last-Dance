import re

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from entitys.sql.card import Card
from entitys.sql.global_event import GlobalEvent
from entitys.sql.player_event import PlayerEvent
from entitys.sql.shop.exotic_armor import ExoticArmor
from entitys.sql.shop.exotic_weapon import ExoticWeapon


# def to_camel_case(name: str) -> str:
#     parts = name.split('-')
#     return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

def to_lower_camel_case(input_str):
    """
    将输入字符串去除空格、短横线和特殊字符后转换为小驼峰形式

    参数:
        input_str (str): 要处理的字符串

    返回:
        str: 小驼峰形式的字符串
    """
    if not input_str:
        return ""

    # 1. 去除所有非字母数字字符（保留字母和数字）
    cleaned_str = re.sub(r'[^a-zA-Z0-9]', ' ', input_str)

    # 2. 分割为单词列表
    words = cleaned_str.split()

    if not words:
        return ""

    # 3. 转换为小驼峰形式
    # 第一个单词全小写，后续单词首字母大写
    camel_case = words[0].lower()
    for word in words[1:]:
        camel_case += word.capitalize()

    return camel_case

def update_card_names():
    engine = create_engine(f'sqlite:///D:\Project\Web\Destiny2\Destiny2-The-Last-Dance\Destiny2-The-Last-Dance-Server\database/raid.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    items = session.query(ExoticArmor).all()
    for item in items:
        original_name = item.description
        new_name = to_lower_camel_case(original_name)
        if new_name != original_name:
            print(f"更新: {original_name} -> {new_name}")
            item.item_name = new_name
    session.commit()
    session.close()

if __name__ == "__main__":
    update_card_names()