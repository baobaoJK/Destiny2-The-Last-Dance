from flask_socketio import emit

from decorators.update_room_info import handle_update_room_info
from entitys.game.player import Player
from entitys.game.room import Room
from services.card.card_service import CardService
from services.room_service import RoomService
from utils import socketio, error, debug, info
from validators import validate_request

room_service = RoomService()
card_service = CardService()

# 抽取随机卡牌
@socketio.on('getRandomCard')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_get_random_card(data, room: Room, player: Player):
    info("抽取随机卡牌")
    debug(data)

    card_type = data['cardType']
    message_list = card_service.get_random_card(room, player, card_type)

    for message in message_list:
        if message.to is not None:
            emit('message', message.to_dict(), to=message.to)
        else:
            emit('message', message.to_dict())

# 卡牌选取
@socketio.on('getCardList')
@validate_request()
@handle_update_room_info()
def handle_get_card_list(data, room: Room):
    info("卡牌选取")
    debug(data)
    message = CardService.get_card_list(room)

    emit('getCardList', message.to_dict())

# 卡牌添加
@socketio.on('saveCard')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_save_card(data, room: Room, player: Player):
    info("卡牌添加")
    debug(data)

    card_dict = data['card']
    card = card_service.convert_card_dict(card_dict)

    message_list = card_service.save_card(room, player, card)

    for message in message_list:
        if message.to is not None:
            emit('message', message.to_dict(), to=message.to)
        else:
            emit('message', message.to_dict())

# 删除卡牌
@socketio.on('deleteCard')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_delete_card(data, room: Room, player: Player):
    info("删除卡牌")
    debug(data)

    card_dict = data['card']
    card = card_service.convert_card_dict(card_dict)

    message_list = card_service.delete_card(room, player, card)

    for message in message_list:
        if message.to is not None:
            emit('message', message.to_dict(), to=message.to)
        else:
            emit('message', message.to_dict())

# 卡牌转换
@socketio.on('transformCard')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_transform_card(data, room: Room, player: Player):
    info("卡牌转换")
    debug(data)

    card_dict = data['card']
    card = card_service.convert_card_dict(card_dict)

    message_list = card_service.transform_card(room, player, card)

    for message in message_list:
        emit('message', message.to_dict())