from enum import Enum


class SpecialEventType(Enum):
    # Type
    CARD_LIST = 'cardList'
    PLAYER_LIST = 'playerList'
    OPTIONS_LIST = 'optionsList'

class SpecialConfig:
    def __init__(self):
        self.title = ''
        self.description = ''
        self.event_name = ''
        self.event_type = ''
        self.send = ''
        self.to = ''
        self.players = []
        self.now_player = 0
        self.deck_list = []
        self.player_list = []
        self.options_list = []
        self.value = None

    def to_dict(self):
        return {
                'title': self.title,
                'description': self.description,
                'eventName': self.event_name,
                'eventType': self.event_type,
                'send': self.send,
                'to': self.to,
                'players': self.players,
                'nowPlayer': self.now_player,
                'deckList': [card if isinstance(card, dict) else card.to_dict() for card in self.deck_list],
                'playerList': self.player_list,
                'optionsList': self.options_list,
                'value': self.value
            }


