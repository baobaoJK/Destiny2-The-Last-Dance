from sqlalchemy import Column, Integer, String, Double
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PlayerEvent(Base):
    __tablename__ = 'player_event_list'

    event_id = Column(String, primary_key=True)
    event_type = Column(String)
    item_name = Column(String)
    event_name = Column(String)
    event_cn_name = Column(String)
    event_description = Column(String)
    event_cn_description = Column(String)
    event_status = Column(String)
    weight = Column(Double)
    count = Column(Integer)
    idea = Column(String)

    def to_dict(self):
        return {
            'eventId': self.event_id,
            'eventType': self.event_type,
            'itemName': self.item_name,
            'eventName': self.event_name,
            'eventCnName': self.event_cn_name,
            'eventDescription': self.event_description,
            'eventCnDescription': self.event_cn_description,
            'eventStatus': self.event_status,
            'weight': self.weight,
            'count': self.count,
            'idea': self.idea,
        }

    def __eq__(self, other):
        if isinstance(other, PlayerEvent):
            return self.event_id == other.event_id
        return False

    def __hash__(self):
        return hash(self.event_id)

    def __getitem__(self, item):
        return getattr(self, item)