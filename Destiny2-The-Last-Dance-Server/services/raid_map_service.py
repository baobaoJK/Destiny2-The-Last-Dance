from typing import List

from entitys.message import Message
from entitys.game.room import RoomStage
from entitys.sql.raid_map import RaidMap
from services.room_service import RoomService
from utils import debug
from utils.tools.lottery import lottery_by_count


class RaidMapService:
    room_service = RoomService()

    # 抽取地图
    def roll_map(self, room_id):
        # 获取房间
        room = self.room_service.room_list.get_room(room_id)

        # 判断地图数量
        raid_list: List[RaidMap] = room.game_config.raid_list
        debug([raid.to_dict() for raid in raid_list])
        raid_maps_count = sum(item.count for item in raid_list)
        if raid_maps_count == 0:
            message = Message().error(message='map.message.errorText01')
            return message

        # 抽取地图
        lottery_count = 50
        map_list = []
        for i in range(lottery_count):
            if i == lottery_count - 7:
                map_obj: RaidMap = lottery_by_count(raid_list)
                map_obj.count -= 1
                map_list.append(map_obj)
                room.set_raid_config(map_obj)
            else:
                map_obj = lottery_by_count(raid_list)
                map_list.append(map_obj)
        message = Message()
        message.data = {'mapList': [raid_map.to_dict() for raid_map in map_list]}
        message.event_type = 'rollMap'
        return message

    # 更改地图事件
    def change_map(self, room_id):
        # 获取房间
        room = self.room_service.room_list.get_room(room_id)

        # 更改玩家隐藏箱数量
        for player in room.player_list.all_players():
            player.raid_chest = 0

        # 更新房间阶段
        room.room_stage = RoomStage.NEXT

        message = Message().warning(message="map.message.warningText02")
        message.event_type = 'raidMap'
        message.message_data = {'raidName': room.raid_config.raid_name}
        return message