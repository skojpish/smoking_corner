from datetime import datetime

from pydantic import BaseModel, Field


class UserPostDTO(BaseModel):
    username: str
    password: str = Field(min_length=8)
    name: str
    email: str


class UserDTO(BaseModel):
    id: int
    username: str
    name: str
    email: str
    role: str


class SmokingPlaceAddressPostDTO(BaseModel):
    city: str
    street: str


class SmokingPlaceAddressDTO(BaseModel):
    id: int
    city: str
    street: str


class SmokingPlacePostDTO(BaseModel):
    number: int


class SmokingPlaceWithoutAddressDTO(BaseModel):
    id: int
    number: int


class SmokingPlaceDTO(SmokingPlaceWithoutAddressDTO):
    city: str
    street: str


class ReservationPostDTO(BaseModel):
    start: datetime
    end: datetime


class ReservationPutDTO(BaseModel):
    sp_number: int
    city: str
    street: str
    start: datetime
    end: datetime


class ReservationDTO(BaseModel):
    reservation_id: int
    username: str
    sp_number: int
    city: str
    street: str
    start: str
    end: str


class SetUserRoleDTO(BaseModel):
    role: str
