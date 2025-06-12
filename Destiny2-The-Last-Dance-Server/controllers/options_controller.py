from flask_socketio import emit

from decorators.update_room_info import handle_update_room_info
from entitys.game.player import Player
from entitys.game.room import Room
from services.options_service import OptionsService
from services.room_service import RoomService
from utils import socketio, info, debug
from validators import validate_request

options_service = OptionsService()
room_service = RoomService()

# 获取地图
@socketio.on('getMapList')
@validate_request()
def handle_get_map_list(data, room: Room):
    info("获取地图列表")
    debug(data)

    message = options_service.get_map_list(room)
    emit('getMapList', message.to_dict())

# 选择地图
@socketio.on('setMap')
@validate_request()
@handle_update_room_info()
def handel_select_map(data, room: Room):
    info("设置地图")
    debug(data)

    map_id = data['mapId']

    message = options_service.select_map(room, map_id)

    emit('message', message.to_dict(), to=room.room_id)

# 抵达遭遇战插旗点
@socketio.on('mapDoor')
@validate_request()
@handle_update_room_info()
def handel_map_door(data, room: Room):
    info("抵达遭遇战插旗点")
    debug(data)

    message_list = options_service.map_door(room)

    for message in message_list:
        emit('message', message.to_dict(), to=room.room_id)

# 遭遇战通关
@socketio.on('mapNext')
@validate_request()
@handle_update_room_info()
def handel_map_next(data, room: Room):
    info("遭遇战通关")
    debug(data)

    message_list = options_service.map_next(room)

    for message in message_list:
        if message.to is not None:
            emit('message', message.to_dict(), to=message.to)
        else:
            emit('message', message.to_dict())

# 获取隐藏箱
@socketio.on('getChest')
@validate_request(require_player=True)
@handle_update_room_info()
def handel_get_chest(data, room: Room, player: Player):
    info("获取隐藏箱")
    debug(data)

    message = options_service.get_chest(room, player)

    emit('message', message.to_dict())

# 设置玩家抽卡和货币数量
@socketio.on('playerSetting')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_player_setting(data, room: Room, player: Player):
    info("设置玩家抽卡和货币数量")
    debug(data)

    setting_type = data['settingType']
    setting_count = data['settingCount']

    message = options_service.player_setting(room, player, setting_type, setting_count)

    emit('message', message.to_dict())

# 无瑕通关
@socketio.on('flawless')
@validate_request()
@handle_update_room_info()
def handle_flawless(data, room: Room):
    info("无瑕通关")
    debug(data)

    message = options_service.flawless(room)
    emit('message', message.to_dict(), to=room.room_id)

# 净化
@socketio.on('purify')
@validate_request()
@handle_update_room_info()
def handle_purify(data, room: Room):
    info("净化")
    debug(data)

    message_list = options_service.purify(room)

    for message in message_list:
        if message.to is not None:
            emit('message', message.to_dict(), to=message.to)
        else:
            emit('message', message.to_dict(), to=room.room_id)
