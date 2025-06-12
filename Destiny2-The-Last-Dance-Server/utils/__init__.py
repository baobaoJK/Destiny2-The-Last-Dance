import random

from utils.service.socketio_instance import *
from .debug import *
from utils.service.sql_connect import *

PLAYER_NUMBERS = [1, 2, 3, 4, 5, 6]

# 打乱
def shuffle_list(data_list):
    random.shuffle(data_list)
    return data_list
