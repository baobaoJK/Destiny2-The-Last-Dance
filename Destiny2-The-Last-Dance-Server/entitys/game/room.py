from enum import Enum

from entitys.game.game_config import GameConfig
from entitys.game.player import PlayerManager
from entitys.game.shop import ShopConfig
from entitys.sql.card import CardType
from entitys.sql.global_event import GlobalEvent
from entitys.sql.raid_map import RaidMap

# 房间状态枚举
class RoomStatus(Enum):
    WAITING = "WAITING"
    PLAYING = "PLAYING"

# 房间阶段枚举
class RoomStage(Enum):
    NEXT = "NEXT"
    DOOR = "DOOR"

class Room:
    MAX_USERS_PER_ROOM = 6  # 设置房间的最大人数

    def __init__(self, room_id, room_owner):
        self.room_id: str = room_id
        self.room_owner: str = room_owner
        self.room_stage: RoomStage = RoomStage.NEXT
        self.room_status: RoomStatus = RoomStatus.WAITING
        self.draw_card_player: str | None = None
        self.random_seats: bool = False
        self.player_list: PlayerManager = PlayerManager()
        self.global_event_list: GlobalEventManager = GlobalEventManager()
        self.raid_config: RaidMap | None = None
        self.shop_config: ShopConfig = ShopConfig()
        self.game_config: GameConfig = GameConfig()

    def to_dict(self):
        return {
            'roomId': self.room_id,
            'roomOwner': self.room_owner,
            'roomStage': self.room_stage.value,
            'roomStatus': self.room_status.value,
            'drawCardPlayer': self.draw_card_player,
            'randomSeats': self.random_seats,
            'playerList': self.player_list.to_dict(),
            'globalEventList': self.global_event_list.to_dict(),
            'raidConfig': self.raid_config.to_dict() if self.raid_config is not None else None ,
            'shopConfig': self.shop_config.to_dict(),
            'cardCountList': self.card_count_list
        }

    # 房间信息
    def to_room_info(self):
        return {
            'roomId': self.room_id,
            'roomOwner': self.room_owner,
            'playerCount': len(self.player_list.players),
        }

    # 玩家信息
    @property
    def players_info(self):
        info_list = {}

        for player_name, player_config in self.player_list.items():
            info_list[player_name] = {
                "playerMoney": player_config['playerConfig'].player_money,
                "drawCount": player_config['playerConfig'].draw_count
            }

        return info_list

    # 获取房间配置
    def get_game_config(self):
        return self.game_config

    # 获取玩家数量
    def get_players(self):
        return len(self.player_list.players)

    # 获取玩家座位
    def get_player_seat(self):
        player_list = []
        for i in range(1, 7):
            player_item = self.player_list.get_player_by_id(i)

            if player_item is not None:
                item = {
                    'roleId': player_item.role_id,
                    'playerName': player_item.player_name,
                    'role': player_item.role
                }
                player_list.append(item)
            else:
                player_list.append(None)

        return player_list

    # 设置突袭信息
    def set_raid_config(self, data):
        self.raid_config = data

    # 获取突袭信息
    def get_raid_config(self):
        return self.raid_config

    # 卡牌数量
    @property
    def card_count_list(self):
        card_count_list = {
            card_type.value: len([card.to_dict() for card in self.game_config.card_list
                              if card.card_type == card_type.value
                              and card.count > 0])
            for card_type in CardType
        }

        return card_count_list

# 房间管理类
class RoomManager:
    def __init__(self):
        self.rooms: dict[str, Room] = {}

    def create_room(self, room_id: str, owner: str) -> bool:
        if room_id in self.rooms:
            return False
        self.rooms[room_id] = Room(room_id, owner)
        return True

    def delete_room(self, room_id: str) -> bool:
        return self.rooms.pop(room_id, None) is not None

    def get_room(self, room_id: str) -> Room | None:
        return self.rooms.get(room_id)

    def room_exists(self, room_id: str) -> bool:
        return room_id in self.rooms

    def all_rooms(self) -> list[Room]:
        return list(self.rooms.values())

    def clear(self):
        self.rooms.clear()

# 全局事件管理类
class GlobalEventManager:

    def __init__(self):
        self.global_event_list: list[GlobalEvent] = []

    def add_event(self, global_event: GlobalEvent):
        """添加全局事件"""
        self.global_event_list.append(global_event)

    def remove_event(self, global_event: GlobalEvent):
        """移除全局事件"""
        self.global_event_list.remove(global_event)

    def get_event(self, event_index) -> GlobalEvent:
        """获取全局事件，如果不存在返回 None"""
        return self.global_event_list[event_index]

    def clear(self):
        """清空全局事件列表"""
        self.global_event_list.clear()

    def to_dict(self):
        """输出玩家事件信息"""
        return [global_event.to_dict() for global_event in self.global_event_list]