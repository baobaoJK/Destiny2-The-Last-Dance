import random
import string

from entitys.sql.card import DeckType
from utils import info, debug, error, warn

from flask_socketio import join_room, leave_room, emit

from entitys.message import Message
from entitys.game.player import Player
from entitys.game.room import RoomManager, RoomStatus, Room


# 生成 4 位由字母大小写和数字随机组合
def random_room_name():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=4))


class RoomService:
    # 房间列表
    room_list = RoomManager()

    # 检查房间号是否位空
    @staticmethod
    def check_room_id(room_id):
        if room_id is None:
            message = Message().error(message='room.message.errorText01')
            emit('message', message.to_dict())
            raise Exception('房间号不能为空')

    # 检查玩家名称是否位空
    @staticmethod
    def check_player_name(player_name):
        if player_name is None:
            message = Message().error(message='room.message.errorText02')
            emit('message', message.to_dict())
            raise Exception('玩家名称不能为空')

    # 检查玩家信息是否为空
    @staticmethod
    def check_player_info(role, role_id, player_name):
        if role is None or role_id is None or player_name is None:
            message = Message().error(message='room.message.errorText03')
            emit('message', message.to_dict())
            raise Exception('玩家信息不能为空')

    # 检查房间是否存在
    def check_room_in_room_list(self, room_id):
        if self.room_list.room_exists(room_id) is False:
            message = Message().error(message='room.message.errorText04')
            message.event_type = 'idNone'
            warn('房间不存在')
            emit('message', message.to_dict())
            raise Exception('房间不存在')

    # 检查玩家是否在房间中
    def check_player_in_room(self, room_id, player_name):
        room = self.room_list.get_room(room_id)
        if room.player_list.players.get(player_name) is None:
            message = Message().error(message='room.message.errorText05')
            emit('message', message.to_dict())
            raise Exception('玩家不在房间中')

    # 检查卡组列表是否正确
    @staticmethod
    def check_deck_type(deck_type):
        if not deck_type in DeckType:
            message = Message().error(message='room.message.errorText10')
            emit('message', message.to_dict())
            raise Exception('卡组列表不正确')

    # 获取所有房间信息
    def update_room_list_info(self):
        # print('获取房间信息')
        room_list = [room.to_room_info() for room in self.room_list.all_rooms()]
        message = Message()
        message.event_type = 'roomList'

        message.data = {'roomList': room_list}
        emit('message', message.to_dict(), broadcast=True)
        debug(f"房间列表 {room_list}")

    # 更新房间信息
    def update_room_info(self, room_id):
        """
        更新房间信息
        :param room_id: 房间 ID
        :return:
        """
        room = self.room_list.get_room(room_id)
        debug(f"房间 {room.to_dict()}")
        message = Message()
        message.data = {'roomInfo': room.to_dict()}
        message.event_type = 'roomInfo'
        emit('message', message.to_dict(), to=room.room_id)

    # 创建房间
    def create_room(self, player_name):
        # 检测该名玩家是否有房间
        for room in self.room_list.all_rooms():
            if room.room_owner == player_name:
                message = Message().warning(message='room.message.warningText06')
                return message

        # 检测房间数量是否大于 2
        if len(self.room_list.all_rooms()) == 2:
            message = Message().error(message='room.message.errorText12')
            return message

        # 随机生成 4 位房间名
        room_id = random_room_name()

        self.room_list.create_room(room_id, player_name)

        info(f"玩家 {player_name} 创建房间 {room_id}")
        message = Message().success(message='room.message.successText01')
        message.data = {'roomId': room_id}

        return message

    # 加入房间
    def join_room(self, room_id, player_data, request):
        # 创建一个玩家对象
        player = Player(player_data)

        # 获取房间
        room = self.room_list.get_room(room_id)

        # 判断玩家是不是队长
        if room.room_owner == player.player_name:
            player.is_captain = True

        message = Message()

        # 判断玩家是否在房间中
        if room.player_list.get_player(player.player_name) is not None:
            join_room(room.room_id)
            room.player_list.get_player(player.player_name).sid= request.sid
            message.event_type = 'joinRoom'
            message.data = {'roomInfo': room.to_dict()}
            return message

        # 判断加入该房间前人数是否为 Max
        if len(room.player_list.players) < 6:
            # 加入房间
            join_room(room.room_id)

            # 添加玩家
            player.sid = request.sid
            room.player_list.add_player(player.player_name, player)

            info(f"玩家 {player.player_name} 加入 {room_id} 房间成功 sid 是 {request.sid}")
            message.message = 'room.message.successText02'
            message.event_type = 'joinRoom'
            message.data = {'roomInfo': room.to_dict()}
            message.message_data = {'playerName': player.player_name}

            return message
        else:
            error("房间已满无法加入")
            return message.error(message = 'room.message.errorText06')

    # 离开房间
    def leave_destiny_room(self, room_id, player_name):
        # 获取房间
        room = self.room_list.get_room(room_id)

        try:
            # 退出房间
            leave_room(room.room_id)
        except Exception as e:
            warn(f"玩家 {player_name} 退出房间失败 {e}")
            message = Message().warning(message='room.message.warningText01')
            return message

        # 删除玩家
        # if room.room_status == RoomStatus.WAITING:
        room.player_list.remove_player(player_name)

        if len(room.player_list.players) == 0:
            self.room_list.delete_room(room_id)
            info(f"房间 {room_id} 因为没人而被销毁了")
            message = Message().warning(message='room.message.warningText01')
            message.event_type = 'destroyRoom'
            return message
        elif player_name == room.room_owner:
            # 如果是房主退出房间
            # 重新选择房主
            room.room_owner = random.choice(list(room.player_list.players.keys()))
            room.player_list.players[room.room_owner].is_captain = True
            info(f"房间 {room_id} 房主已更换为 {room.room_owner}")
            message = Message().warning(message='room.message.warningText02')
            message.message_data = {'playerName': room.room_owner}
        else:
            info(f"玩家 {player_name} 离开 {room_id} 房间")
            message = Message().warning(message='room.message.warningText03')
            message.message_data = {'playerName': player_name}

        return message

    # 点击座位
    def click_seat(self, room, seat_index, player_name):

        # 判断座位上是否有人
        for player in room.player_list.players.values():
            if player.role_id == seat_index:
                message = Message().error(message='room.message.errorText07')
                return message

        info(f"玩家 {player_name} 选择 {seat_index} 号位置")
        message = Message(message='room.message.infoText01')
        message.message_data = {'playerName': player_name, 'seatIndex': seat_index}

        player = room.player_list.get_player(player_name)
        player.role_id = seat_index
        return message

    # 开始游戏
    def start_game(self, room_id):
        # 获取房间
        room = self.room_list.get_room(room_id)

        if len(room.player_list.players) >= 1 and room.room_status is RoomStatus.WAITING:
            # 切换房间状态
            room.room_status = RoomStatus.PLAYING
            message = Message().success(message='room.message.successText03')
            message.event_type = 'startGame'
        elif room.room_status is RoomStatus.PLAYING:
            message = Message().error(message='room.message.errorText08')
        else:
            message = Message().error(message='room.message.errorText09')

        return message

    # 减除玩家
    def remove_player(self, room_id, player_name):
        # 获取房间
        room = self.room_list.get_room(room_id)
        # 获取玩家
        player = room.player_list.get_player(player_name)
        sid = player.sid
        # 删除玩家
        leave_room(room, sid=sid)
        room.player_list.remove_player(player_name)

        message = Message().warning(message='room.message.warningText04')
        message.message_data = {'playerName': player_name}
        return message

    # 获取当前玩家手上的卡牌
    @classmethod
    def get_player_deck_list(cls, room: Room, player: Player):
        all_deck_list = []

        for card_type, card_list in player.deck_list.items():
            all_deck_list += card_list

        message = Message()
        message.event_type = 'getPlayerDeckList'
        message.data = {
            'playerDeckList': [card.to_dict() for card in all_deck_list],
            'playerName': player.player_name
        }
        return message
