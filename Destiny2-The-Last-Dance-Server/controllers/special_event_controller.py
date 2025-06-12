from flask_socketio import emit

from decorators.update_room_info import handle_update_room_info
from entitys.game.room import Room
from services.special_event.special_card_service import SpecialCardService
from services.options_service import card_service
from services.room_service import RoomService
from services.special_event.special_event_service import SpecialEventService
from utils import info, debug
from utils.service.socketio_instance import socketio
from validators import validate_request

special_event_service = SpecialEventService()
special_card_service = SpecialCardService()
room_service = RoomService()

# 卡牌特殊事件
@socketio.on('runSpecialByCard')
@validate_request()
@handle_update_room_info()
def handle_run_special_by_card(data, room: Room):
    info("卡牌特殊事件")
    debug(data)

    special_config_dict = data['specialConfig']
    card_dict = data['card']

    special_config = special_card_service.convert_config_dict(special_config_dict)
    card = card_service.convert_card_dict(card_dict)

    player = room.player_list.get_player_by_id(special_config.send)

    message_list = special_card_service.run_special_by_card(room, player, special_config, card)

    for message in message_list:
        if message.to is None:
            emit('message', message.to_dict())
        else:
            if message.to == 'room':
                emit('message', message.to_dict(), to=room.room_id)
            else:
                emit('message', message.to_dict(), to=message.to)

# 执行特殊事件
@socketio.on('runSpecialByEvent')
@validate_request()
@handle_update_room_info()
def handle_run_special_by_event(data, room: Room):
    info("执行特殊事件")
    debug(data)

    special_config_dict = data['specialConfig']
    special_data = data['specialData']
    special_config = special_card_service.convert_config_dict(special_config_dict)

    special_config.to = special_data['to']
    special_config.send = special_data['send']
    special_config.value = special_data['value']

    player = room.player_list.get_player_by_id(special_config.send)

    message_list = special_event_service.run_special_by_event(room, player, special_config)

    for message in message_list:
        if message.to is None:
            emit('message', message.to_dict())
        else:
            if message.to == 'room':
                emit('message', message.to_dict(), to=room.room_id)
            else:
                emit('message', message.to_dict(), to=message.to)
