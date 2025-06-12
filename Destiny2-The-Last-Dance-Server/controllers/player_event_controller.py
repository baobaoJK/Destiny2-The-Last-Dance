from flask_socketio import emit

from decorators.update_room_info import handle_update_room_info
from entitys.game.player import Player
from entitys.game.room import Room
from services.player_event_service import PlayerEventService
from services.room_service import RoomService
from utils import error, info, debug
from utils.service.socketio_instance import socketio
from validators import validate_request

player_event_service = PlayerEventService()
room_service = RoomService()

# 接受个人事件
@socketio.on('acceptPlayerEvent')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_accept_player_event(data, room: Room, player: Player):
    info("接受个人事件")
    debug(data)

    event_index = data['eventIndex']

    message_list = player_event_service.accept_player_event(room, player, event_index)

    for message in message_list:
        if message.to is not None:
            emit('message', message.to_dict(), to=message.to)
        else:
            emit('message', message.to_dict())

# 完成个人事件
@socketio.on('finishPlayerEvent')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_finish_player_event(data, room: Room, player: Player):
    info("完成个人事件")
    debug(data)

    event_index = data['eventIndex']

    message_list = player_event_service.finish_player_event(room, player, event_index)

    for message in message_list:
        if message.to is not None:
            emit('message', message.to_dict(), to=message.to)
        else:
            emit('message', message.to_dict())

# 放弃个人事件
@socketio.on('dropPlayerEvent')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_drop_player_event(data, room: Room, player: Player):
    info("放弃个人事件")
    debug(data)

    event_index = data['eventIndex']

    message = player_event_service.drop_player_event(player, event_index)

    emit('message', message.to_dict())
