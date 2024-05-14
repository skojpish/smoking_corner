from datetime import datetime, timedelta

from aiohttp import BasicAuth
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from aiohttp.web_routedef import RouteTableDef
from pydantic import ValidationError

from src.database.db_queries import SmokingPlaceQs, ReservationQs, UserQs
from src.decorators import validate_user_data, validate_json
from src.exceptions import UniqueError
from src.schemas import ReservationPostDTO, ReservationPutDTO

router = RouteTableDef()


@router.get('/smoking-places')
@validate_user_data
async def get_all_smoking_places(request: Request):
    smoking_places = await SmokingPlaceQs.get_all_smoking_places()

    if not smoking_places:
        return json_response(status=200, data={"message": "There are no smoking places yet"})

    response = {}

    for smoking_place in smoking_places:
        status = await ReservationQs.get_status(smoking_place.id)

        response[smoking_places.index(smoking_place)+1] = dict(smoking_place)
        response[smoking_places.index(smoking_place) + 1]['status'] = status

    return json_response(status=200, data=response)


@router.get(r"/smoking-places/{sp_id:\d+}")
@validate_user_data
async def get_smoking_place(request: Request):
    sp_id = request.match_info['sp_id']

    smoking_place = await SmokingPlaceQs.get_smoking_place(sp_id)

    if not smoking_place:
        return json_response(status=404, data={"error": f"Smoking place with id: {sp_id} not found"})

    status = await ReservationQs.get_status(sp_id)

    response = dict(smoking_place)
    response['status'] = status

    return json_response(status=200, data=response)


@router.post(r'/smoking-places/{sp_id:\d+}/reservation')
@validate_json
@validate_user_data
async def reserve_smoking_place(request: Request):
    sp_id = request.match_info['sp_id']

    sp_id_exist = await SmokingPlaceQs.check_id(sp_id)

    if not sp_id_exist:
        return json_response(status=404, data={"error": f"Smoking place with id: {sp_id} not found"})

    data = await request.json()

    try:
        reservation = ReservationPostDTO(**data)
    except ValidationError as e:
        return json_response(status=400, data={error["loc"][0]: error["msg"] for error in e.errors()})

    if reservation.start < datetime.now():
        return json_response(status=400, data={"field": "start",
                                               "error": "The entered time must be greater than the current one"})

    if reservation.start > reservation.end:
        return json_response(status=400, data={"field": "end",
                                               "error": "The entered time must be greater than the start"})

    if reservation.end - reservation.start > timedelta(minutes=30):
        return json_response(status=400, data={"error": "The duration of the reservation cannot exceed 30 minutes"})

    auth_header = request.headers.get('Authorization')
    username, password, encoding = BasicAuth.decode(auth_header)

    user_id = await UserQs.get_user_id(username)

    user_data = {
        'user_id': user_id,
        'sp_id': sp_id,
        'start': reservation.start,
        'end': reservation.end
    }

    res_time_exist = await ReservationQs.check_time(**user_data)

    if res_time_exist:
        return json_response(status=400, data={"error": "The reservation for the entered time already exists"})

    try:
        reservation_id = await ReservationQs.add_reservation(**user_data)
    except UniqueError as e:
        return json_response(status=400, data={"error": f"{e.message}"})

    user_reservation = await ReservationQs.get_user_reservation(user_id, reservation_id)

    response = dict(user_reservation)
    response.pop("username")

    return json_response(status=201, data=response)


@router.get('/reservations')
@validate_user_data
async def get_all_reservations(request: Request):
    reservations = await ReservationQs.get_all_reservations()

    if not reservations:
        return json_response(status=200, data={"message": "There are no reservations yet"})

    response = {}

    for reservation in reservations:
        response[reservations.index(reservation)+1] = dict(reservation)

    return json_response(status=200, data=response)


@router.get('/reservations/my-reservations')
@validate_user_data
async def get_user_reservations(request: Request):
    auth_header = request.headers.get('Authorization')
    username, password, encoding = BasicAuth.decode(auth_header)
    user_id = await UserQs.get_user_id(username)

    user_reservations = await ReservationQs.get_user_reservations(user_id)

    if not user_reservations:
        return json_response(status=200, data={"message": "You don't have any reservations yet"})

    response = {}

    for user_reservation in user_reservations:
        user_res_dict = dict(user_reservation)
        user_res_dict.pop('username')
        response[user_reservations.index(user_reservation) + 1] = user_res_dict

    return json_response(status=200, data=response)


@router.get(r'/reservations/my-reservations/{res_id:\d+}')
@validate_user_data
async def get_user_reservation(request: Request):
    res_id = request.match_info['res_id']

    auth_header = request.headers.get('Authorization')
    username, password, encoding = BasicAuth.decode(auth_header)
    user_id = await UserQs.get_user_id(username)

    user_reservation = await ReservationQs.get_user_reservation(user_id, res_id)

    if not user_reservation:
        return json_response(status=404, data={"error": f"Reservation with id: {res_id} not found"})

    response = dict(user_reservation)
    response.pop("username")

    return json_response(status=200, data=response)


@router.put(r'/reservations/my-reservations/{res_id:\d+}')
@validate_json
@validate_user_data
async def update_user_reservation(request: Request):
    res_id = request.match_info['res_id']

    data = await request.json()

    try:
        reservation = ReservationPutDTO(**data)
    except ValidationError as e:
        return json_response(status=400, data={error["loc"][0]: error["msg"] for error in e.errors()})

    if reservation.start < datetime.now():
        return json_response(status=400, data={"field": "start",
                                               "error": "The update time must be greater than the current one"})

    if reservation.start > reservation.end:
        return json_response(status=400, data={"field": "end",
                                               "error": "The entered time must be greater than the start"})

    if reservation.end - reservation.start > timedelta(minutes=30):
        return json_response(status=400, data={"error": "The duration of the update reservation cannot exceed 30 "
                                                        "minutes"})

    auth_header = request.headers.get('Authorization')
    username, password, encoding = BasicAuth.decode(auth_header)

    user_id = await UserQs.get_user_id(username)
    sp_id = await SmokingPlaceQs.get_smoking_place_id(reservation.sp_number, reservation.city, reservation.street)

    if not sp_id:
        return json_response(status=400, data={"error": "You entered the wrong address"})

    check_data = {
        'user_id': user_id,
        'sp_id': sp_id[0],
        'start': reservation.start,
        'end': reservation.end
    }

    res_time_exist = await ReservationQs.check_time(**check_data)

    if res_time_exist:
        return json_response(status=400, data={"error": "The reservation for the entered time already exists"})

    update_data = {
        'res_id': res_id,
        'sp_id': sp_id[0],
        'start': reservation.start,
        'end': reservation.end
    }

    res_id_exist = await ReservationQs.check_id(res_id)

    if res_id_exist:
        await ReservationQs.update_user_reservation(**update_data)
        status = 200
    else:
        await ReservationQs.put_reservation(**update_data)
        status = 201

    user_reservation = await ReservationQs.get_user_reservation(user_id, res_id)

    response = dict(user_reservation)
    response.pop("username")

    return json_response(status=status, data=response)


@router.delete(r'/reservations/my-reservations/{res_id:\d+}')
@validate_user_data
async def delete_user_reservation(request: Request):
    res_id = request.match_info['res_id']

    res_id_exist = await ReservationQs.check_id(res_id)

    if not res_id_exist:
        return json_response(status=404, data={"error": f"Reservation with id: {res_id} not found"})

    auth_header = request.headers.get('Authorization')
    username, password, encoding = BasicAuth.decode(auth_header)
    user_id = await UserQs.get_user_id(username)

    await ReservationQs.delete_reservation(res_id, user_id)

    return json_response(status=204)
