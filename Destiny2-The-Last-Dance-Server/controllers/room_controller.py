import time

from flask import request
from flask_socketio import emit, disconnect

from decorators.update_room_info import handle_update_room_info
from entitys.game.player import Player
from entitys.game.room import Room
from entitys.message import Message
from services.room_service import RoomService
from utils import socketio, debug, PLAYER_NUMBERS, error, info
from utils.load_config import load_config
from validators import validate_request

room_service = RoomService()

def delayed_disconnect(sid):
    import time
    time.sleep(0.1)  # 短暂延迟
    disconnect(sid=sid)  # 断开指定客户端

# 连接触发
@socketio.on('connect')
def handle_connect(data):
    info("用户连接")
    debug(data)

    token = data.get('token', None)
    version = data.get('version', None)
    config = load_config()
    # if token is None or version is None or config['server']['version'] != version:
    #     disconnect()

    current_connections = len(socketio.server.manager.rooms['/'])
    debug(f"Socket 连接数量: {current_connections}")
    room_service.update_room_list_info()


# 退出连接
@socketio.on('disconnect')
def handle_disconnect():
    pass

# 创建房间
@socketio.on('createRoom')
def handle_create_room(data):
    info("创建房间")
    debug(data)

    role = data['playerInfo']['role']
    player_name = data['playerInfo']['playerName']

    try:
        room_service.check_player_info(role, 0, player_name)
    except ValueError:
        error(ValueError)
        return

    message = room_service.create_room(player_name)

    emit('message', message.to_dict())

    # 传递信息
    data = {
        'roomId': message.data['roomId'],
        'playerInfo': {
            'role': role,
            'playerName': player_name
        }
    }

    handle_join_room(data)
    room_service.update_room_list_info()

# 加入房间
@socketio.on('joinRoom')
def handle_join_room(data):
    info("加入房间")
    debug(data)

    room_id = data['roomId']
    player = data['playerInfo']

    try:
        room_service.check_room_id(room_id)
        room_service.check_player_info(player['role'], 0, player['playerName'])
        room_service.check_room_in_room_list(room_id)
    except ValueError:
        error(ValueError)
        return

    message = room_service.join_room(room_id, player, request)

    if message.status == Message.SUCCESS:
        room = room_service.room_list.get_room(room_id)

        emit('message', message.to_dict(), to=room.room_id)

        # 分发信息
        raid_map = room.raid_config
        if raid_map is not None and raid_map.raid_name is not None:
            message = Message().warning('room.message.warningText05')
            message.event_type = 'raidMap'
            message.message_data = {
                'raidName': raid_map.raid_name
            }
            emit('message', message.to_dict())
    else:
            emit('message', message.to_dict())

    room_service.update_room_list_info()


# 离开房间
@socketio.on('leaveRoom')
@validate_request(require_player=True)
def handle_leave_room(data, room: Room, player: Player):
    info("离开房间")
    debug(data)

    message = room_service.leave_destiny_room(room.room_id, player.player_name)

    emit('message', message.to_dict(), to=room.room_id)
    if message.event_type != 'destroyRoom':
        room_service.update_room_info(room.room_id)
    room_service.update_room_list_info()

# 坐下
@socketio.on('clickSeat')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_click_seat(data, room: Room, player: Player):
    info("坐下")
    debug(data)

    # 座位号
    seat_index = data['seatIndex']

    if seat_index not in PLAYER_NUMBERS:
        message = Message().error(message='room.message.errorText10')
        emit('message', message.to_dict())
        return

    message = room_service.click_seat(room, seat_index, player.player_name)
    if message.message_type is Message.ERROR:
        emit('message', message.to_dict())
    else:
        emit('message', message.to_dict(), to=room.room_id)

# 开始游戏
@socketio.on('startGame')
@validate_request()
@handle_update_room_info()
def handle_start_game(data, room: Room):
    info("开始游戏")
    debug(data)

    # 开始游戏信息
    message = room_service.start_game(room.room_id)
    # 广播消息
    emit('message', message.to_dict(), to=room.room_id)

# 减除玩家
@socketio.on('kickPlayer')
@validate_request(require_player=True)
@handle_update_room_info(update_room_list=True)
def handel_kick_player(data, room: Room, player: Player):
    info("减除玩家")
    debug(data)

    sid = room.player_list.get_player(player.player_name).sid
    message = Message().error(message='error.message.errorText11')
    message.event_type = 'kickPlayer'
    emit('message', message.to_dict(), to=sid)

    message = room_service.remove_player(room.room_id, player.player_name)

    emit('message', message.to_dict(), to=room.room_id)

# 获取当前玩家手上的手牌
@socketio.on('getPlayerDeckList')
@validate_request(require_player=True)
def handle_get_player_deck_list(data, room: Room, player: Player):
    debug(f"获取 {player.player_name} 手上的手牌")
    info(data)

    message = room_service.get_player_deck_list(room, player)

    emit('message', message.to_dict())
