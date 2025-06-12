from flask_socketio import emit

from decorators.update_room_info import handle_update_room_info
from entitys.game.room import Room
from entitys.message import Message
from services.global_event_service import GlobalEventService
from services.room_service import RoomService
from utils import error, debug, info
from utils.service.socketio_instance import socketio
from validators import validate_request

global_event_service = GlobalEventService()
room_service = RoomService()

# 接受全局事件
@socketio.on('acceptGlobalEvent')
@validate_request()
@handle_update_room_info()
def handle_accept_global_event(data, room: Room):
    info("接受全局事件")
    debug(data)

    event_index = data['eventIndex']

    message_list = global_event_service.accept_global_event(room, event_index)

    for message in message_list:
        emit('message', message.to_dict(), to=room.room_id)

    global_event = room.global_event_list.get_event(event_index)
    if global_event.event_name == 'Doro-Virus':
        emit('doro', Message().info('show').to_dict(), to=room.room_id)

# 完成全局事件
@socketio.on('finishGlobalEvent')
@validate_request()
@handle_update_room_info()
def handle_finish_global_event(data, room: Room):
    info("完成全局事件")
    debug(data)

    event_index = data['eventIndex']

    global_event = room.global_event_list.get_event(event_index)
    if global_event.event_name == 'Doro-Virus':
        emit('doro', Message().info('close').to_dict(), to=room.room_id)

    message = global_event_service.finish_global_event(room, event_index)

    emit('message', message.to_dict(), to=room.room_id)