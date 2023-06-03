from xmlrpc.client import DateTime

import enum
from sqlalchemy import Boolean, MetaData, Column, ForeignKey, Integer, String, Date, DateTime, Float, Enum, UniqueConstraint, Table
from sqlalchemy.orm import relationship

from src.database import Base
from sqlalchemy.dialects.postgresql import ENUM


teams_in_competitions = Table("teams_in_competitions",Base.metadata,
                                 Column("id", Integer, primary_key=True),
                                 Column("team_id", Integer, ForeignKey("teams.id")),
                                 Column("competition_id",Integer, ForeignKey("competitions.id")))

class CategoryEnum(str, enum.Enum):
    Senior = 'Senior'
    Junior = 'Junior'

class SportEnum(str, enum.Enum):
    Football = 'Football'
    Basketball = 'Basketball'
    Volleyball = 'Volleyball'
    Futsal = 'Futsal'

categories_list = (category.value for category in CategoryEnum)
sports_list = (sport.value for sport in SportEnum)

class Team(Base):
    __tablename__ = 'teams' #This is table name

    id = Column(Integer, primary_key=True)
    name = Column(String(30),unique=True, nullable=False, index=True)
    country = Column(String(30),nullable=False)
    description = Column(String(100))

class Competition(Base):

    __tablename__ = 'competitions'  # This is table name
    __table_args__ = (UniqueConstraint('name', 'category', 'sport'),)

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    category = Column(ENUM(*categories_list, name="categories_list"),nullable=False)
    sport = Column(ENUM(*sports_list, name="sports_list"),nullable=False)
    teams = relationship("Team",secondary=teams_in_competitions,backref="competitions")

class Match(Base):
    __tablename__ = 'matches' #This is table name
    __table_args__ = (UniqueConstraint('local_id', 'visitor_id', 'competition_id', 'date'),)

    id = Column(Integer, primary_key=True)
    date = Column(DateTime,nullable=False)
    price = Column(Float, nullable=False)
    total_available_tickets = Column(Integer, nullable=False)

    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    competition = relationship("Competition",backref="matches")
    local_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    visitor_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    local = relationship("Team", foreign_keys=local_id)
    visitor = relationship("Team", foreign_keys=visitor_id)

class Account(Base):
    __tablename__ = 'accounts'

    username = Column(String(30), primary_key=True, unique=True, nullable=False)
    password = Column(String(), nullable=False)
    # 0 not admin/ 1 is admin
    is_admin = Column(Integer, nullable=False)
    available_money = Column(Float, nullable=False)
    orders = relationship('Order', backref='orders', lazy=True)

    def __init__(self, username, available_money=200, is_admin=0):
        self.username = username
        self.available_money = available_money
        self.is_admin = is_admin


class Order(Base):
    __tablename__ = 'orders'
    __table_args__ = (UniqueConstraint('id'),)

    id = Column(Integer, primary_key=True)
    username = Column(String(30), ForeignKey('accounts.username'), nullable=False)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    tickets_bought = Column(Integer, nullable=False)

    def __init__(self, match_id, tickets_bought):
        self.match_id = match_id
        self.tickets_bought = tickets_bought
