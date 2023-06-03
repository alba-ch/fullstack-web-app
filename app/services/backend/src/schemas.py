# import enum
from src.models import CategoryEnum, SportEnum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TeamBase(BaseModel):
    name: str
    country: str
    description: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class Team(TeamBase):
    id: int

    class Config:
        orm_mode = True


class CompetitionBase(BaseModel):
    name: str
    category: CategoryEnum
    sport:  SportEnum


class CompetitionCreate(CompetitionBase):
    pass


class Competition(CompetitionBase):
    id: int
    teams: list[Team] = []

    class Config:
        orm_mode = True


class MatchBase(BaseModel):
    date: datetime
    price: float
    total_available_tickets: int
    local: Team
    visitor: Team
    competition: Competition


class MatchCreate(MatchBase):
    date : str


class Match(MatchBase):
    id: int

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    #username: str
    match_id: int
    tickets_bought: int

    class Config:
        orm_mode = True

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    username: str

    class Config:
        orm_mode = True

class AccountBase(BaseModel):
    username: str

class AccountCreate(AccountBase):
    username: str = Field(..., description="username")
    password: str = Field(..., min_length=8, max_length=24 ,description="user password")

class Account(AccountBase):
    orders: list[Order] = []
    is_admin: int
    available_money: float

    class Config:
        orm_mode = True

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None

class SystemAccount(Account):
    password: str
