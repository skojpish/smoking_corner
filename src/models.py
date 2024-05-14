from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    def __repr__(self):
        cols = []
        for col in self.__table__.columns.keys():
            cols.append(f'{col}={getattr(self, col)}')
        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    name: Mapped[str]
    email: Mapped[str]
    role: Mapped[str] = mapped_column(default='user')

    reservation_user: Mapped[List['Reservation']] = relationship(back_populates='user_ref')


class SmokingPlaceAddress(Base):
    __tablename__ = "smoking_place_address"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str]
    street: Mapped[str] = mapped_column(unique=True)

    smoking_place: Mapped[List['SmokingPlace']] = relationship(back_populates='address')


class SmokingPlace(Base):
    __tablename__ = "smoking_place"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int]
    sp_address: Mapped[int] = mapped_column(ForeignKey("smoking_place_address.id", ondelete='CASCADE'))

    address: Mapped['SmokingPlaceAddress'] = relationship(back_populates="smoking_place")
    reservation_sp: Mapped[List['Reservation']] = relationship(back_populates='sp_ref')


class Reservation(Base):
    __tablename__ = "reservation"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete='CASCADE'))
    smoking_place: Mapped[int] = mapped_column(ForeignKey("smoking_place.id", ondelete='CASCADE'))
    start: Mapped[datetime]
    end: Mapped[datetime]

    user_ref: Mapped['User'] = relationship(back_populates='reservation_user')
    sp_ref: Mapped['SmokingPlace'] = relationship(back_populates='reservation_sp')
