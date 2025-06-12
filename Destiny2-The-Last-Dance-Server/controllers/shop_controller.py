from flask_socketio import emit

from decorators.update_room_info import handle_update_room_info
from entitys.game.player import Player
from entitys.game.room import Room
from services.room_service import RoomService
from services.shop_service import ShopService
from utils import info, debug
from utils.service.socketio_instance import socketio
from validators import validate_request

shop_service = ShopService()
room_service = RoomService()

# 刷新商店
@socketio.on('refreshShop')
@validate_request()
@handle_update_room_info()
def handle_refresh_shop(data, room: Room):
    info(f"刷新商店")
    debug(data)

    message_list = shop_service.refresh_shop(room)

    for message in message_list:
        emit('message', message.to_dict(), to=room.room_id)

# 购买物品
@socketio.on('buyItem')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_buy_item(data, room: Room, player: Player):
    info(f"购买物品")
    debug(data)

    type_list = data['typeList']
    item_index = data['itemIndex']

    message_list = shop_service.buy_item(room, player, type_list, item_index)

    for message in message_list:
        if message.to is None:
            emit('message', message.to_dict(), to=room.room_id)
        else:
            emit('message', message.to_dict(), to=message.to)

# 开启商店
@socketio.on('openShop')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_open_shop(data, room: Room, player: Player):
    info(f"开启商店")
    debug(data)

    message = shop_service.open_shop(room, player)

    emit('message', message.to_dict())

# 使用圣水
@socketio.on('useItem')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_use_item(data, room: Room, player: Player):
    info(f"使用圣水")
    debug(data)

    backpack_index = data['backpackIndex']

    message = shop_service.use_item(player, backpack_index)

    if message.data is not None:
        emit('showWaterDeckList', message.to_dict())
        emit('message', message.to_dict())
    else:
        emit('message', message.to_dict())

# 删除卡牌
@socketio.on('deleteCardItem')
@validate_request(require_player=True)
@handle_update_room_info()
def handle_delete_card_item(data, room: Room, player: Player):
    info("删除卡牌")
    debug(data)

    card_type = data['cardType']
    card_index = data['cardIndex']
    backpack_index = data['backpackIndex']

    message_list = shop_service.delete_card_item(room, player, card_type, card_index, backpack_index)

    for message in message_list:
        if message.to is None:
            emit('message', message.to_dict(), to=message.to)
            emit('hideWaterDeckList', {}, to=message.to)
        else:
            emit('message', message.to_dict(), to=message.to)
            emit('hideWaterDeckList', {})
