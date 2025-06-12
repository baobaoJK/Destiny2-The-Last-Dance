from typing import List

from entitys.sql.global_event import GlobalEvent
from entitys.sql.raid_map import RaidMap
from entitys.sql.player_event import PlayerEvent
from entitys.sql.card import Card
from utils import get_session


class GameConfig:

    def __init__(self):
        self.raid_list: List[RaidMap] = self.set_raid_list()
        self.card_list: List[Card] = self.set_card_list()
        self.player_event_list: List[PlayerEvent] = self.set_player_event_list()
        self.global_event_list: List[GlobalEvent] = self.set_global_event_list()

    # 设置突袭地图列表
    @classmethod
    def set_raid_list(cls) -> List[RaidMap]:
        session = get_session()
        sql_raid_list = session.query(RaidMap).all()
        return sql_raid_list

    # 设置卡牌列表
    @classmethod
    def set_card_list(cls) -> List[Card]:
        session = get_session()
        sql_card_list = session.query(Card).all()
        return sql_card_list

    # 设置玩家个人事件列表
    @classmethod
    def set_player_event_list(cls) -> List[PlayerEvent]:
        session = get_session()
        sql_player_event_list = session.query(PlayerEvent).all()
        return sql_player_event_list

    # 设置全局事件列表
    @classmethod
    def set_global_event_list(cls) -> List[GlobalEvent]:
        session = get_session()
        sql_global_event_list = session.query(GlobalEvent).all()
        return sql_global_event_list