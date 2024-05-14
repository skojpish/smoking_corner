import bcrypt
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from aiohttp.web_routedef import RouteTableDef
from pydantic import ValidationError

from src.database.db_queries import UserQs
from src.decorators import validate_user_data, validate_json
from src.exceptions import UniqueError
from src.schemas import UserPostDTO

router = RouteTableDef()


@router.post('/registration')
@validate_json
@validate_user_data
async def reg_user(request: Request):
    data = await request.json()

    try:
        user = UserPostDTO(**data)
    except ValidationError as e:
        return json_response(status=400, data={error["loc"][0]: error["msg"] for error in e.errors()})

    password_bytes = bcrypt.hashpw(user.password.encode('utf8'), bcrypt.gensalt())
    user.password = password_bytes.decode('utf8')

    try:
        new_user = await UserQs.add_user(**dict(user))
    except UniqueError as e:
        return json_response(status=400, data={"error": f"{e.message}"})

    return json_response(status=201, data=dict(new_user))
