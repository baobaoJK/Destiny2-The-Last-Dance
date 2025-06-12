import time

from flask_socketio import emit

from decorators.update_room_info import handle_update_room_info
from entitys.game.room import Room
from entitys.message import Message
from services.raid_map_service import RaidMapService
from services.room_service import RoomService
from utils import socketio, debug, info
from validators import validate_request

raid_map_service = RaidMapService()
room_service = RoomService()

# 抽取地图
@socketio.on('rollMap')
@validate_request()
@handle_update_room_info()
def handle_roll_map(data, room: Room):
    info(f"抽取地图")
    debug(data)

    roll_time = data.get('rollTime')

    message = Message().warning(message='map.message.warningText01')
    emit('message', message.to_dict(), to=room.room_id)

    message = raid_map_service.roll_map(room.room_id)
    emit('rollMap', message.to_dict(), to=room.room_id)

    if roll_time is not None:
        time.sleep(roll_time)

        message = raid_map_service.change_map(room.room_id)
        emit('message', message.to_dict(), to=room.room_id)