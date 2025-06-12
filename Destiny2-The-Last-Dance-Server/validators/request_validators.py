from functools import wraps

from services.room_service import RoomService
from utils import error

room_service = RoomService()

# 使用统一校验器，无需重复写代码
def validate_request(require_player=False):
    def decorator(func):
        @wraps(func)
        def wrapper(data, *args, **kwargs):
            room_id = data.get('roomId')
            player_name = data.get('playerName') if require_player else None

            try:
                room_service.check_room_id(room_id)
                room_service.check_room_in_room_list(room_id)
                if require_player:
                    room_service.check_player_name(player_name)
                    room_service.check_player_in_room(room_id, player_name)
            except ValueError as e:
                error(e)
                return

            room = room_service.room_list.get_room(room_id)
            player = room.player_list.get_player(player_name) if require_player else None

            # 将 room / player 透传下去
            if not require_player:
                return func(data, room, *args, **kwargs)
            else:
                return func(data, room, player, *args, **kwargs)

        return wrapper
    return decorator