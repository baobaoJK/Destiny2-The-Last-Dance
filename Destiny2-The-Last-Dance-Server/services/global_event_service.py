import copy
import random

from entitys.game.player import Player, PlayerEventManager
from entitys.game.room import Room
from entitys.message import Message
from entitys.sql.global_event import GlobalEvent
from services.room_service import RoomService
from services.special_event.special_event_service import SpecialEventService
from utils import debug, shuffle_list
from utils.tools.lottery import lottery_by_count


class GlobalEventService:

    # 生成全局事件
    @staticmethod
    def generate_global_event(room: Room):
        # 获取全局事件
        global_event_list = room.game_config.global_event_list

        generate_count = random.randint(1, 2)
        for _ in range(generate_count):
            # 设置全局事件
            global_event = lottery_by_count(global_event_list)
            global_event.count -= 1
            debug(f'生成全局事件：{global_event.event_name}')
            room.global_event_list.add_event(global_event)

    # 接受全局事件
    def accept_global_event(self, room: Room, event_index: int):

        # 获取事件
        global_event = room.global_event_list.get_event(event_index)
        global_event.event_status = 'active'

        message_list = self.run_global_event(room, global_event)

        message = Message().warning('globalEvent.message.warningText01')
        message.event_type = 'globalEvent'
        message.message_data = {
            'globalEventName': f'globalEventList.{global_event.item_name}.name'
        }
        message_list.append(message)

        return message_list

    # 全局事件执行
    def run_global_event(self, room: Room, global_event: GlobalEvent):
        message_list = []

        global_event_name = global_event.event_name

        special_event_service = SpecialEventService()

        player_list = shuffle_list(room.player_list.all_players())

        # 见者有份
        if global_event_name == 'Shared-Gold':
            for player in player_list:
                player.player_money += 3
                message = Message().success('special.message.sharedGoldText01')
                message.to = player.sid
                message_list.append(message)

        # 金融危机
        if global_event_name == 'Financial-Crisis':
            for player in player_list:
                player.player_money = player.player_money // 2
                message = Message().success('special.message.financialCrisisText01')
                message.to = player.sid
                message_list.append(message)

        # 五谷丰登
        if global_event_name == 'Bumper-Harvest':
            message_list.append(special_event_service.special_by_bumper_harvest(room))

        # 各自为营
        if global_event_name == 'Split-Up':
            message = Message().warning('special.message.splitUpText01')
            message.message_data = {
                'playerId1': player_list[0].role_id,
                'playerId2': player_list[1].role_id,
                'playerId3': player_list[2].role_id,
                'playerId4': player_list[3].role_id,
                'playerId5': player_list[4].role_id,
                'playerId6': player_list[5].role_id,
            }
            message_list.append(message)

        # 斗地主
        if global_event_name == 'Dou-Di-Zhu':
            message = Message().warning('special.message.douDiZhuText01')
            message.message_data = {
                'playerId1': player_list[0].role_id,
                'playerId2': player_list[1].role_id,
                'playerId3': player_list[2].role_id,
            }
            message_list.append(message)

        # 一二三木头人
        if global_event_name == 'Wood-Man':
            message = Message().warning('special.message.woodManText01')
            message.message_data = {
                'playerId': player_list[0].role_id
            }
            message_list.append(message)

        # 移型换位
        if global_event_name == 'Transposition':
            player = None
            for player_item in room.player_list.all_players():
                if player_item.is_captain:
                    player = player_item

            message_list.append(special_event_service.special_by_transposition(room, player))

        # 掀桌
        if global_event_name == 'Flip-The-Table':
            message = Message().warning('special.message.flipTheTableText01')
            message.event_type = 'kickPlayer'
            message.to = 'room'
            message_list.append(message)

            room_service = RoomService()
            room_service.room_list.delete_room(room)

        # 左平行，右...
        if global_event_name == 'Left-Parallel-Right':
            message = Message().warning('special.message.leftParallelRightText01')
            message.message_data = {
                'playerId1': player_list[0].role_id,
                'playerId2': player_list[1].role_id,
                'playerId3': player_list[2].role_id,
                'playerId4': player_list[3].role_id,
                'playerId5': player_list[4].role_id,
                'playerId6': player_list[5].role_id,
            }
            message_list.append(message)

        # 生化母体
        if global_event_name == 'Biochemical-Matrix':
            message_list.append(special_event_service.special_by_matrix(room))

        # 我的我的我的
        if global_event_name == 'Mine-Mine-Mine':
            message = Message().warning('special.message.mineMineMineText01')
            message.message_data = {
                'playerId': player_list[0].role_id
            }
            message_list.append(message)

        # 命定混沌
        # if global_event_name == 'Deterministic-Chaos':
        #     room.random_seats = True
        #     message = Message().warning("globalEvent.message.deterministicChaos")
        #     message_list.append(message)

        # 蜂巢思维
        if global_event_name == 'Hive-Mind':
            message = Message().warning('special.message.hiveMindText01')

            captain_player = [player_item for player_item in room.player_list.all_players() if player_item.is_captain][0]

            for player_item in room.player_list.all_players():
                if player_item != captain_player:
                    captain_player_event_list = PlayerEventManager()
                    for event in captain_player.player_event_list.player_event_list:
                        captain_player_event_list.add_event(copy.deepcopy(event))
                    player_item.player_event_list = captain_player_event_list

            message_list.append(message)

        # 我们，我不明白
        if global_event_name == 'We-I-Dont-Understand':
            message_list.append(special_event_service.special_by_we(room))

        return message_list

    # 完成全局事件
    @classmethod
    def finish_global_event(cls, room: Room, event_index: int):
        # 获取事件，设置事件状态
        global_event = room.global_event_list.get_event(event_index)
        room.global_event_list.remove_event(global_event)

        message = Message().success("globalEvent.message.successText01")
        message.event_type = 'globalEvent'
        message.message_data = {
            'globalEventName': f'globalEventList.{global_event.item_name}.name'
        }
        return message