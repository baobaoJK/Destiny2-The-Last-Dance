from flask_socketio import emit

from decorators.update_room_info import handle_update_room_info
from entitys.game.player import Player
from entitys.game.room import Room
from entitys.message import Message
from services.card.card_service import CardService
from services.room_service import RoomService
from utils import socketio, error, info, debug
from validators import validate_request

card_service = CardService()
room_service = RoomService()

# 显示抽卡列表
@socketio.on('showDeckList')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_show_deck_list(data, room: Room, player: Player):
    info("显示抽卡列表")
    debug(data)

    deck_type = data['deckType']

    message = card_service.show_deck_list(room, player, deck_type)

    if message.data is not None:
        emit('showDeckList', {'data': message.data})
        # 当前 {playerName} 正在抽卡
        room_message = Message().info('card.message.infoText01')
        room_message.message_data = {
            'playerName': player.player_name
        }
        emit('message', room_message.to_dict(), to=room.room_id)

    emit('message', message.to_dict())

# 关闭抽卡列表
@socketio.on('closeDeckList')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_close_deck_list(data, room: Room, player: Player):
    info("关闭抽卡列表")
    debug(data)

    message = card_service.close_deck_list(room, player)

    emit('message', message.to_dict(), to=room.room_id)

# 点击卡牌
@socketio.on('clickCard')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_click_card(data, room: Room, player: Player):
    info("点击卡牌")
    debug(data)

    card_dict = data['card']
    card = card_service.convert_card_dict(card_dict)

    message_list = card_service.click_card(room, player, card)

    for message in message_list:
        if message.to is None:
            emit('message', message.to_dict())
        else:
            emit('message', message.to_dict(), to=message.to)

        if message.data is not None:
            emit('clickCard', message.to_dict())