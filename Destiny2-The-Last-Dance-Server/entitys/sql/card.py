from enum import Enum

from sqlalchemy import Column, Integer, String, Double
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# 十三幺
thirteen_list = [
    'Osteo-Striga',
    'All-Out',
    'Darkness-Servant-1',
    'Darkness-Servant-2',
    'Light-Bringer-1',
    'Light-Bringer-2',
    'Light-Bringer-3',
    'Paladin',
    'Armory',
    'Reicher-Playboy',
    'Assassin',
    'Protect-Target',
    'Weaken'
]

class CardType(Enum):
    MicroGain = 'MicroGain'
    StrongGain = 'StrongGain'
    Opportunity = 'Opportunity'
    MicroDiscomfort = 'MicroDiscomfort'
    StrongDiscomfort = 'StrongDiscomfort'
    Unacceptable = 'Unacceptable'
    Technology = 'Technology'
    Support = 'Support'

# 卡组列表
class DeckType(Enum):
    Safe = 'Safe'
    Danger = 'Danger'
    Gambit = 'Gambit'
    Luck = 'Luck'
    Devote = 'Devote'

class Card(Base):
    __tablename__ = 'card_list'

    card_id = Column(String, primary_key=True)
    card_type: CardType = Column(String)
    card_label = Column(String)
    card_level = Column(Integer)
    item_name = Column(String)
    card_name = Column(String)
    card_cn_name = Column(String)
    card_description = Column(String)
    card_cn_description = Column(String)
    card_special = Column(String)
    weight = Column(Double)
    count = Column(Integer)
    all_count = Column(Integer)
    idea = Column(String)
    role_id = 0

    def to_dict(self):
        return {
            'cardId': self.card_id,
            'cardType': self.card_type,
            'cardLabel': self.card_label,
            'cardLevel': self.card_level,
            'itemName': self.item_name,
            'cardName': self.card_name,
            'cardCnName': self.card_cn_name,
            'cardDescription': self.card_description,
            'cardCnDescription': self.card_cn_description,
            'cardSpecial': self.card_special,
            'weight': self.weight,
            'count': self.count,
            'allCount': self.all_count,
            'idea': self.idea,
            'roleId': self.role_id
        }

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.card_id == other.card_id
        return False

    def __hash__(self):
        return hash(self.card_id)

    def __getitem__(self, item):
        return getattr(self, item)