from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RaidMap(Base):
    __tablename__ = 'raid_list'

    raid_id = Column(String, primary_key=True)
    raid_name = Column(String)
    raid_check = Column(Integer)
    raid_level = Column(Integer)
    raid_level_point = 0
    raid_chest = Column(Integer)
    weight = Column(Integer)
    count = Column(Integer)

    def to_dict(self):
        return {
            'raidId': self.raid_id,
            'raidName': self.raid_name,
            'raidCheck': self.raid_check,
            'raidLevel': self.raid_level,
            'raidLevelPoint': self.raid_level_point,
            'raidChest': self.raid_chest,
            'weight': self.weight,
            'count': self.count
        }