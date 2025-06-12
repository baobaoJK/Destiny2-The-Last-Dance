import functools

from entitys.game.room import Room


def handle_update_room_info(update_room_info=True, update_room_list=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from services.room_service import RoomService
            room_service = RoomService()

            # 尝试从参数中提取 room
            room = None
            for arg in args:
                if isinstance(arg, Room):
                    room = arg
                    break

            try:
                return func(*args, **kwargs)
            finally:
                if update_room_info:
                    room_service.update_room_info(room.room_id)

                if update_room_list:
                    room_service.update_room_list_info()

        return wrapper
    return decorator
