from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from aiohttp.web_routedef import RouteTableDef
from pydantic import ValidationError

from src.database.db_queries import SmokingPlaceQs, UserQs, SmokingPlaceAddressQs, ReservationQs
from src.decorators import validate_admin_data, validate_json
from src.exceptions import UniqueError
from src.schemas import SmokingPlacePostDTO, SetUserRoleDTO, SmokingPlaceAddressPostDTO

router = RouteTableDef()


@router.get('/admin/addresses')
@validate_admin_data
async def get_smoking_places_addresses(request: Request):
    sp_addresses = await SmokingPlaceAddressQs.get_all_addresses()

    if not sp_addresses:
        return json_response(status=200, data={"message": "There are no addresses yet"})

    response = {}

    for address in sp_addresses:
        sp_amount = await SmokingPlaceQs.get_sp_amount(address.id)

        response[sp_addresses.index(address) + 1] = dict(address)
        response[sp_addresses.index(address) + 1]['sp_amount'] = sp_amount

    return json_response(status=200, data=response)


@router.post('/admin/addresses/new-address')
@validate_json
@validate_admin_data
async def add_smoking_place_address(request: Request):
    data = await request.json()

    try:
        address = SmokingPlaceAddressPostDTO(**data)
    except ValidationError as e:
        return json_response(status=400, data={error["loc"][0]: error["msg"] for error in e.errors()})

    try:
        new_address = await SmokingPlaceAddressQs.add_address(**dict(address))
    except UniqueError as e:
        return json_response(status=400, data={"error": f"{e.message}"})

    return json_response(status=201, data=dict(new_address))


@router.get(r'/admin/addresses/{address_id:\d+}')
@validate_admin_data
async def get_address(request: Request):
    address_id = request.match_info['address_id']
    address = await SmokingPlaceAddressQs.get_address(address_id)

    if not address:
        return json_response(status=404, data={"error": f"Address with id: {address_id} not found"})

    sp_amount = await SmokingPlaceQs.get_sp_amount(address_id)

    response = dict(address)
    response['sp_amount'] = sp_amount

    return json_response(status=200, data=response)


@router.get(r'/admin/addresses/{address_id:\d+}/smoking-places')
@validate_admin_data
async def get_smoking_places_on_address(request: Request):
    address_id = request.match_info['address_id']
    smoking_places = await SmokingPlaceQs.get_smoking_places_on_address(address_id)

    if not smoking_places:
        return json_response(status=200, data={"message": "There are no smoking places yet"})

    response = {}

    for smoking_place in smoking_places:
        status = await ReservationQs.get_status(smoking_place.id)

        response[smoking_places.index(smoking_place) + 1] = dict(smoking_place)
        response[smoking_places.index(smoking_place) + 1]['status'] = status

    return json_response(status=200, data=response)


@router.get(r'/admin/addresses/{address_id:\d+}/smoking-places/{sp_id:\d+}')
@validate_admin_data
async def get_smoking_place_on_address(request: Request):
    address_id = request.match_info['address_id']
    sp_id = request.match_info['sp_id']

    address_id_exist = await SmokingPlaceAddressQs.check_id(address_id)

    if not address_id_exist:
        return json_response(status=404, data={"error": f"Address with id: {address_id} not found"})

    smoking_place = await SmokingPlaceQs.get_smoking_place_on_address(sp_id, address_id)

    if not smoking_place:
        return json_response(status=404, data={"error": f"Smoking place with id: {sp_id} not found "
                                                        f"on address with id {address_id}"})

    status = await ReservationQs.get_status(smoking_place.id)

    response = dict(smoking_place)
    response['status'] = status

    return json_response(status=200, data=response)


@router.post(r'/admin/addresses/{address_id:\d+}/smoking-places/new-smoking-place')
@validate_json
@validate_admin_data
async def add_smoking_place(request: Request):
    address_id = request.match_info['address_id']

    address_id_exist = await SmokingPlaceAddressQs.check_id(address_id)

    if not address_id_exist:
        return json_response(status=404, data={"error": f"Address with id: {address_id} not found"})

    data = await request.json()

    try:
        smoking_place = SmokingPlacePostDTO(**data)
    except ValidationError as e:
        return json_response(status=400, data={error["loc"][0]: error["msg"] for error in e.errors()})

    sp_id = await SmokingPlaceQs.add_smoking_place(smoking_place.number, address_id)
    new_sp = await SmokingPlaceQs.get_smoking_place(sp_id)

    return json_response(status=201, data=dict(new_sp))


@router.put(r'/admin/addresses/{address_id:\d+}')
@validate_json
@validate_admin_data
async def update_address(request: Request):
    address_id = request.match_info['address_id']

    data = await request.json()

    try:
        address = SmokingPlaceAddressPostDTO(**data)
    except ValidationError as e:
        return json_response(status=400, data={error["loc"][0]: error["msg"] for error in e.errors()})

    address_dict = dict(address)
    address_dict['address_id'] = address_id

    address_id_exist = await SmokingPlaceAddressQs.check_id(address_id)

    if address_id_exist:
        updated_address = await SmokingPlaceAddressQs.update_address(**address_dict)
        status = 200
    else:
        updated_address = await SmokingPlaceAddressQs.put_address(**address_dict)
        status = 201

    return json_response(status=status, data=dict(updated_address))


@router.put(r'/admin/addresses/{address_id:\d+}/smoking-places/{sp_id:\d+}')
@validate_json
@validate_admin_data
async def update_smoking_place(request: Request):
    address_id = request.match_info['address_id']
    sp_id = request.match_info['sp_id']

    address_id_exist = await SmokingPlaceAddressQs.check_id(address_id)

    if not address_id_exist:
        return json_response(status=404, data={"error": f"Address with id: {address_id} not found"})

    data = await request.json()

    try:
        smoking_place = SmokingPlacePostDTO(**data)
    except ValidationError as e:
        return json_response(status=400, data={error["loc"][0]: error["msg"] for error in e.errors()})

    sp_dict = dict(smoking_place)
    sp_dict['sp_id'] = sp_id

    sp_id_exist = await SmokingPlaceQs.check_id(sp_id)

    if sp_id_exist:
        updated_sp = await SmokingPlaceQs.update_smoking_place(**sp_dict)
        status = 200
    else:
        sp_dict['address_id'] = address_id
        updated_sp = await SmokingPlaceQs.put_smoking_place(**sp_dict)
        status = 201

    updated_sp_dict = dict(updated_sp)
    updated_sp_dict['address_id'] = address_id

    return json_response(status=status, data=updated_sp_dict)


@router.delete(r'/admin/addresses/{address_id:\d+}')
@validate_admin_data
async def delete_address(request: Request):
    address_id = request.match_info['address_id']

    address_id_exist = await SmokingPlaceAddressQs.check_id(address_id)

    if not address_id_exist:
        return json_response(status=404, data={"error": f"Address with id: {address_id} not found"})

    await SmokingPlaceAddressQs.delete_address(address_id)

    return json_response(status=204)


@router.delete(r'/admin/addresses/{address_id:\d+}/smoking-places/{sp_id:\d+}')
@validate_admin_data
async def delete_smoking_place(request: Request):
    sp_id = request.match_info['sp_id']

    sp_id_exist = await SmokingPlaceQs.check_id(sp_id)

    if not sp_id_exist:
        return json_response(status=404, data={"error": f"Smoking place with id: {sp_id} not found"})

    await SmokingPlaceQs.delete_smoking_place(sp_id)

    return json_response(status=204)


@router.get("/admin/users")
@validate_admin_data
async def get_all_users(request: Request):
    users = await UserQs.get_all_users()

    response = {}

    for user in users:
        response[users.index(user) + 1] = dict(user)

    return json_response(status=200, data=response)


@router.get(r"/admin/users/{user_id:\d+}")
@validate_admin_data
async def get_user_by_id(request: Request):
    user_id = request.match_info['user_id']
    user = await UserQs.get_user(user_id)

    if not user:
        return json_response(status=404, data={"error": f"User with id: {user_id} not found"})

    response = dict(user)

    return json_response(status=200, data=response)


@router.patch(r"/admin/users/{user_id:\d+}")
@validate_json
@validate_admin_data
async def update_user_role(request: Request):
    user_id = request.match_info['user_id']

    user_id_exist = await UserQs.check_id(user_id)

    if not user_id_exist:
        return json_response(status=404, data={"error": f"User with id: {user_id} not found"})

    data = await request.json()

    try:
        user_role_dto = SetUserRoleDTO(**data)
        user_role = user_role_dto.role
    except ValidationError as e:
        return json_response(status=400, data={error["loc"][0]: error["msg"] for error in e.errors()})

    if user_role not in ('user', 'admin'):
        return json_response(status=400, data={"field": "role",
                                               "error": "The value must be equal to 'user' or 'admin'"})

    user = await UserQs.update_user_role(user_id, user_role)

    return json_response(status=200, data=dict(user))


@router.delete(r"/admin/users/{user_id:\d+}")
@validate_admin_data
async def delete_user(request: Request):
    user_id = request.match_info['user_id']

    user_id_exist = await UserQs.check_id(user_id)

    if not user_id_exist:
        return json_response(status=404, data={"error": f"User with id: {user_id} not found"})

    role = await UserQs.get_user_role_by_id(user_id)

    if role == 'admin':
        return json_response(status=403, data={"error": "You can't delete a user with the admin role"})

    await UserQs.delete_user(user_id)

    return json_response(status=204)


@router.get("/admin/reservations")
@validate_admin_data
async def get_all_reservations_admin(request: Request):
    reservations = await ReservationQs.get_all_reservations()

    if not reservations:
        return json_response(status=200, data={"message": "There are no reservations yet"})

    response = {}

    for reservation in reservations:
        response[reservations.index(reservation) + 1] = dict(reservation)

    return json_response(status=200, data=response)


@router.get(r"/admin/reservations/{res_id:\d+}")
@validate_admin_data
async def get_reservation_admin(request: Request):
    res_id = request.match_info['res_id']

    reservation = await ReservationQs.get_reservation_admin(res_id)

    if not reservation:
        return json_response(status=404, data={"error": f"Reservation with id: {res_id} not found"})

    response = dict(reservation)

    return json_response(status=200, data=response)


@router.delete(r"/admin/reservations/{res_id:\d+}")
@validate_admin_data
async def delete_reservation_admin(request: Request):
    res_id = request.match_info['res_id']

    res_id_exist = await ReservationQs.check_id(res_id)

    if not res_id_exist:
        return json_response(status=404, data={"error": f"Reservation with id: {res_id} not found"})

    await ReservationQs.delete_reservation_admin(res_id)

    return json_response(status=204)
