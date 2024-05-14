from datetime import datetime

from sqlalchemy import select, between, and_, or_, delete, update, String, Integer, exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import count


from src.models import SmokingPlace, SmokingPlaceAddress, User, Reservation
from src.schemas import UserDTO, SmokingPlaceDTO, ReservationDTO, SmokingPlaceAddressDTO, SmokingPlaceWithoutAddressDTO
from .db_conn import async_session_factory
from ..exceptions import UniqueError, DatabaseError


class UserQs:
    @staticmethod
    async def add_user(username: str, password: str, name: str, email: str):
        try:
            async with async_session_factory() as session:
                stmt = User(username=username, password=password, name=name, email=email)
                session.add(stmt)
                await session.commit()
                user_dto = UserDTO.model_validate(stmt, from_attributes=True)
        except IntegrityError as e:
            raise UniqueError(e.orig.args[0])
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return user_dto

    @staticmethod
    async def get_user_password(username: str):
        try:
            async with async_session_factory() as session:
                query = select(User.password).where(User.username == username)
                result = await session.execute(query)
                password = result.scalars().first()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return password

    @staticmethod
    async def get_user_role(username: str):
        try:
            async with async_session_factory() as session:
                query = select(User.role).where(User.username == username)
                result = await session.execute(query)
                role = result.scalars().one()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return role

    @staticmethod
    async def get_user_role_by_id(user_id: int):
        try:
            async with async_session_factory() as session:
                query = select(User.role).where(User.id == user_id)
                result = await session.execute(query)
                role = result.scalars().first()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return role

    @staticmethod
    async def get_user_id(username: str):
        try:
            async with async_session_factory() as session:
                query = select(User.id).where(User.username == username)
                result = await session.execute(query)
                user_id = result.scalars().first()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return user_id

    @staticmethod
    async def get_all_users():
        try:
            async with async_session_factory() as session:
                query = select(User)
                result = await session.execute(query)
                users = result.scalars().all()
                users_dto = [UserDTO.model_validate(user, from_attributes=True) for user in users]
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return users_dto

    @staticmethod
    async def get_user(user_id: int):
        try:
            async with async_session_factory() as session:
                query = select(User).where(User.id == user_id)
                result = await session.execute(query)
                user = result.scalars().first()
                user_dto = UserDTO.model_validate(user, from_attributes=True) if user else []
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return user_dto

    @staticmethod
    async def update_user_role(user_id: int, user_role: str):
        try:
            async with async_session_factory() as session:
                query = update(User).where(User.id == user_id).values(role=user_role).returning(User)
                result = await session.execute(query)
                user = result.scalars().first()
                user_dto = UserDTO.model_validate(user, from_attributes=True) if user else []
                await session.commit()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return user_dto

    @staticmethod
    async def delete_user(user_id: int):
        try:
            async with async_session_factory() as session:
                query = delete(User).where(User.id == user_id)
                await session.execute(query)
                await session.flush()

                query = delete(Reservation).where(Reservation.user == user_id)
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)
            raise DatabaseError()

    @staticmethod
    async def check_id(user_id: int):
        try:
            async with async_session_factory() as session:
                query = select(exists().where(User.id == user_id))
                result = await session.execute(query)
                check = result.scalars().first()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return check


class SmokingPlaceQs:
    @staticmethod
    async def add_smoking_place(number: int, address_id: int):
        try:
            async with async_session_factory() as session:
                stmt = SmokingPlace(number=number, sp_address=address_id)
                session.add(stmt)
                await session.commit()
        except IntegrityError as e:
            raise UniqueError(e.orig.args[0])
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return stmt.id

    @staticmethod
    async def put_smoking_place(sp_id: int, number: int, address_id: int):
        try:
            async with async_session_factory() as session:
                stmt = SmokingPlace(id=sp_id, number=number, sp_address=address_id)
                session.add(stmt)
                smoking_place_dto = SmokingPlaceWithoutAddressDTO.model_validate(stmt, from_attributes=True)
                await session.commit()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return smoking_place_dto

    @staticmethod
    async def get_all_smoking_places():
        try:
            async with async_session_factory() as session:
                query = (select(SmokingPlace.id,
                                SmokingPlace.number,
                                SmokingPlaceAddress.city,
                                SmokingPlaceAddress.street)
                         .select_from(SmokingPlace)
                         .join(SmokingPlace.address))
                result = await session.execute(query)
                smoking_places = result.all()
                smoking_places_dto = [SmokingPlaceDTO.model_validate(smoking_place, from_attributes=True)
                                      for smoking_place in smoking_places]
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return smoking_places_dto

    @staticmethod
    async def get_smoking_place(sp_id: int):
        try:
            async with async_session_factory() as session:
                query = (select(SmokingPlace.id,
                                SmokingPlace.number,
                                SmokingPlaceAddress.city,
                                SmokingPlaceAddress.street)
                         .select_from(SmokingPlace)
                         .where(SmokingPlace.id == sp_id)
                         .join(SmokingPlace.address))
                result = await session.execute(query)
                smoking_place = result.first()
                smoking_place_dto = SmokingPlaceDTO.model_validate(smoking_place,
                                                                   from_attributes=True) if smoking_place else []
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return smoking_place_dto

    @staticmethod
    async def get_smoking_place_id(number: int, city: str, street: str):
        try:
            async with async_session_factory() as session:
                query = (select(SmokingPlace.id)
                         .join(SmokingPlace.address)
                         .where(and_(SmokingPlace.number == number,
                                     SmokingPlaceAddress.city == city,
                                     SmokingPlaceAddress.street == street)))
                result = await session.execute(query)
                sp_id = result.first()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return sp_id

    @staticmethod
    async def delete_smoking_place(sp_id: int):
        try:
            async with async_session_factory() as session:
                query = delete(SmokingPlace).where(SmokingPlace.id == sp_id)
                await session.execute(query)
                await session.flush()

                query = delete(Reservation).where(Reservation.smoking_place == sp_id)
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)
            raise DatabaseError()

    @staticmethod
    async def get_sp_amount(address_id: int):
        try:
            async with async_session_factory() as session:
                query = (select(count(SmokingPlace.id).label('amount').cast(Integer))
                         .where(SmokingPlace.sp_address == address_id))
                result = await session.execute(query)
                amount = result.scalars().first()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return amount

    @staticmethod
    async def get_smoking_places_on_address(address_id: int):
        try:
            async with async_session_factory() as session:
                query = (select(SmokingPlace.id,
                                SmokingPlace.number)
                         .where(SmokingPlace.sp_address == address_id))
                result = await session.execute(query)
                smoking_places = result.all()
                smoking_places_dto = [SmokingPlaceWithoutAddressDTO.model_validate(smoking_place, from_attributes=True)
                                      for smoking_place in smoking_places]
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return smoking_places_dto

    @staticmethod
    async def get_smoking_place_on_address(sp_id: int, address_id: int):
        try:
            async with (async_session_factory() as session):
                query = (select(SmokingPlace.id,
                                SmokingPlace.number)
                         .where(and_(SmokingPlace.id == sp_id, SmokingPlace.sp_address == address_id)))
                result = await session.execute(query)
                smoking_place = result.first()
                if smoking_place:
                    smoking_place_dto = SmokingPlaceWithoutAddressDTO.model_validate(smoking_place,
                                                                                     from_attributes=True)
                else:
                    smoking_place_dto = []
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return smoking_place_dto

    @staticmethod
    async def update_smoking_place(number: int, sp_id: int):
        try:
            async with async_session_factory() as session:
                query = (update(SmokingPlace)
                         .where(SmokingPlace.id == sp_id)
                         .values(number=number)
                         .returning(SmokingPlace))
                result = await session.execute(query)
                smoking_place = result.scalars().first()
                smoking_place_dto = SmokingPlaceWithoutAddressDTO.model_validate(smoking_place, from_attributes=True)
                await session.commit()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return smoking_place_dto

    @staticmethod
    async def check_id(sp_id: int):
        try:
            async with async_session_factory() as session:
                query = select(exists().where(SmokingPlace.id == sp_id))
                result = await session.execute(query)
                check = result.scalars().first()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return check


class ReservationQs:
    @staticmethod
    async def get_status(sp_id: int):
        try:
            async with async_session_factory() as session:
                query = select(Reservation.end).where(
                    and_(Reservation.smoking_place == sp_id, between(
                        datetime.now(), Reservation.start, Reservation.end)))
                result = await session.execute(query)
                end_occupied = result.scalars().first()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return f'occupied until {end_occupied}' if end_occupied else 'free'

    @staticmethod
    async def get_all_reservations():
        try:
            async with async_session_factory() as session:
                query = (select(Reservation.id.label("reservation_id"),
                                User.username.label("username"),
                                SmokingPlace.number.label("sp_number"),
                                SmokingPlaceAddress.city.label("city"),
                                SmokingPlaceAddress.street.label("street"),
                                Reservation.start.label("start").cast(String),
                                Reservation.end.label("end").cast(String))
                         .select_from(Reservation)
                         .where(Reservation.end >= datetime.now())
                         .join(Reservation.user_ref)
                         .join(Reservation.sp_ref)
                         .join(SmokingPlace.address))
                result = await session.execute(query)
                reservations = result.all()
                reservations_dto = [ReservationDTO.model_validate(reservation, from_attributes=True)
                                    for reservation in reservations]
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return reservations_dto

    @staticmethod
    async def check_time(user_id: int, sp_id: int, start: datetime, end: datetime):
        try:
            async with async_session_factory() as session:
                query = select(Reservation.start, Reservation.end).where(
                    and_(
                        or_(
                            Reservation.user == user_id,
                            Reservation.smoking_place == sp_id),
                        or_(
                            between(
                                start, Reservation.start, Reservation.end),
                            between(
                                end, Reservation.start, Reservation.end)
                        )
                    )
                )
                result = await session.execute(query)
                reservation_time = result.scalars().first()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return reservation_time

    @staticmethod
    async def add_reservation(user_id: int, sp_id: int, start: datetime, end: datetime):
        try:
            async with async_session_factory() as session:
                stmt = Reservation(user=user_id, smoking_place=sp_id, start=start, end=end)
                session.add(stmt)
                await session.commit()
        except IntegrityError as e:
            raise UniqueError(e.orig.args[0])
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return stmt.id

    @staticmethod
    async def put_reservation(res_id: int, user_id: int, sp_id: int, start: datetime, end: datetime):
        try:
            async with async_session_factory() as session:
                stmt = Reservation(id=res_id, user=user_id, smoking_place=sp_id, start=start, end=end)
                session.add(stmt)
                await session.commit()
        except Exception as e:
            print(e)
            raise DatabaseError()

    @staticmethod
    async def get_user_reservations(user_id: int):
        try:
            async with async_session_factory() as session:
                query = (select(Reservation.id.label("reservation_id"),
                                User.username.label("username"),
                                SmokingPlace.number.label("sp_number"),
                                SmokingPlaceAddress.city.label("city"),
                                SmokingPlaceAddress.street.label("street"),
                                Reservation.start.label("start").cast(String),
                                Reservation.end.label("end").cast(String))
                         .select_from(Reservation)
                         .where(and_(Reservation.user == user_id,
                                     Reservation.end >= datetime.now()))
                         .join(Reservation.user_ref)
                         .join(Reservation.sp_ref)
                         .join(SmokingPlace.address))
                result = await session.execute(query)
                user_reservations = result.all()
                user_reservations_dto = [ReservationDTO.model_validate(user_reservation, from_attributes=True)
                                         for user_reservation in user_reservations]
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return user_reservations_dto

    @staticmethod
    async def get_user_reservation(user_id: int, res_id: int):
        try:
            async with async_session_factory() as session:
                query = (select(Reservation.id.label("reservation_id"),
                                User.username.label("username"),
                                SmokingPlace.number.label("sp_number"),
                                SmokingPlaceAddress.city.label("city"),
                                SmokingPlaceAddress.street.label("street"),
                                Reservation.start.label("start").cast(String),
                                Reservation.end.label("end").cast(String))
                         .select_from(Reservation)
                         .where(and_(Reservation.user == user_id, Reservation.id == res_id))
                         .join(Reservation.user_ref)
                         .join(Reservation.sp_ref)
                         .join(SmokingPlace.address))
                result = await session.execute(query)
                user_reservation = result.first()
                if user_reservation:
                    user_reservation_dto = ReservationDTO.model_validate(user_reservation, from_attributes=True)
                else:
                    user_reservation_dto = []
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return user_reservation_dto

    @staticmethod
    async def get_reservation_admin(res_id: int):
        try:
            async with async_session_factory() as session:
                query = (select(Reservation.id.label("reservation_id"),
                                User.username.label("username"),
                                SmokingPlace.number.label("sp_number"),
                                SmokingPlaceAddress.city.label("city"),
                                SmokingPlaceAddress.street.label("street"),
                                Reservation.start.label("start").cast(String),
                                Reservation.end.label("end").cast(String))
                         .select_from(Reservation)
                         .where(Reservation.id == res_id)
                         .join(Reservation.user_ref)
                         .join(Reservation.sp_ref)
                         .join(SmokingPlace.address))
                result = await session.execute(query)
                user_reservation = result.first()
                if user_reservation:
                    user_reservation_dto = ReservationDTO.model_validate(user_reservation, from_attributes=True)
                else:
                    user_reservation_dto = []
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return user_reservation_dto

    @staticmethod
    async def update_user_reservation(res_id: int, sp_id: int, start: datetime, end: datetime):
        try:
            async with async_session_factory() as session:
                query = (update(Reservation).where(Reservation.id == res_id)
                         .values(smoking_place=sp_id, start=start, end=end))
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)
            raise DatabaseError()

    @staticmethod
    async def delete_reservation(res_id: int, user_id: int):
        try:
            async with async_session_factory() as session:
                query = delete(Reservation).where(and_(Reservation.id == res_id, Reservation.user == user_id))
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)
            raise DatabaseError()

    @staticmethod
    async def delete_reservation_admin(res_id: int):
        try:
            async with async_session_factory() as session:
                query = delete(Reservation).where(Reservation.id == res_id)
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)
            raise DatabaseError()

    @staticmethod
    async def check_id(res_id: int):
        try:
            async with async_session_factory() as session:
                query = select(exists().where(Reservation.id == res_id))
                result = await session.execute(query)
                check = result.scalars().first()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return check


class SmokingPlaceAddressQs:
    @staticmethod
    async def get_all_addresses():
        try:
            async with async_session_factory() as session:
                query = select(SmokingPlaceAddress.id.label('id'),
                               SmokingPlaceAddress.city.label('city'),
                               SmokingPlaceAddress.street.label('street'))
                result = await session.execute(query)
                addresses = result.all()
                addresses_dto = [SmokingPlaceAddressDTO.model_validate(address, from_attributes=True)
                                 for address in addresses]
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return addresses_dto

    @staticmethod
    async def get_address(address_id: int):
        try:
            async with async_session_factory() as session:
                query = (select(SmokingPlaceAddress.id.label('id'),
                                SmokingPlaceAddress.city.label('city'),
                                SmokingPlaceAddress.street.label('street'))
                         .where(SmokingPlaceAddress.id == address_id))
                result = await session.execute(query)
                address = result.first()
                address_dto = SmokingPlaceAddressDTO.model_validate(address, from_attributes=True) if address else []
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return address_dto

    @staticmethod
    async def add_address(city: str, street: str):
        try:
            async with async_session_factory() as session:
                stmt = SmokingPlaceAddress(city=city, street=street)
                session.add(stmt)
                await session.commit()
                address_dto = SmokingPlaceAddressDTO.model_validate(stmt, from_attributes=True)
        except IntegrityError as e:
            raise UniqueError(e.orig.args[0])
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return address_dto

    @staticmethod
    async def put_address(address_id: int, city: str, street: str):
        try:
            async with async_session_factory() as session:
                stmt = SmokingPlaceAddress(id=address_id, city=city, street=street)
                session.add(stmt)
                await session.commit()
                address_dto = SmokingPlaceAddressDTO.model_validate(stmt, from_attributes=True)
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return address_dto

    @staticmethod
    async def update_address(address_id: int, city: str, street: str):
        try:
            async with async_session_factory() as session:
                query = (update(SmokingPlaceAddress)
                         .where(SmokingPlaceAddress.id == address_id)
                         .values(city=city, street=street)
                         .returning(SmokingPlaceAddress))
                result = await session.execute(query)
                address = result.scalars().first()
                address_dto = SmokingPlaceAddressDTO.model_validate(address, from_attributes=True) if address else []
                await session.commit()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return address_dto

    @staticmethod
    async def delete_address(address_id: int):
        try:
            async with async_session_factory() as session:
                query = delete(SmokingPlaceAddress).where(SmokingPlaceAddress.id == address_id)
                await session.execute(query)
                await session.flush()

                query = delete(SmokingPlace).where(SmokingPlace.sp_address == address_id).returning(SmokingPlace.id)
                result = await session.execute(query)
                sp_ids = result.scalars().all()
                await session.flush()

                for sp_id in sp_ids:
                    query = delete(Reservation).where(Reservation.smoking_place == sp_id)
                    await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)
            raise DatabaseError()

    @staticmethod
    async def check_id(address_id: int):
        try:
            async with async_session_factory() as session:
                query = select(exists().where(SmokingPlaceAddress.id == address_id))
                result = await session.execute(query)
                check = result.scalars().first()
        except Exception as e:
            print(e)
            raise DatabaseError()
        else:
            return check
