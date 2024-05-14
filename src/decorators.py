from json import JSONDecodeError

from aiohttp import BasicAuth
from aiohttp.web_response import json_response

from src.database.db_queries import UserQs
from src.exceptions import DatabaseError


def validate_user_data(func):
    async def wrapper(request, *args, **kwargs):
        try:
            return await func(request, *args, **kwargs)
        except DatabaseError as e:
            return json_response(status=500, data={'error': 'Internal server error'})
    return wrapper


def validate_admin_data(func):
    async def wrapper(request, *args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            username, password, encoding = BasicAuth.decode(auth_header)
            role = await UserQs.get_user_role(username)

            if role != 'admin':
                return json_response(status=403, data={'error': 'Access denied'})

            return await func(request, *args, **kwargs)
        except DatabaseError as e:
            return json_response(status=500, data={'error': 'Internal server error'})
    return wrapper


def validate_json(func):
    async def wrapper(request, *args, **kwargs):
        try:
            await request.json()
        except JSONDecodeError:
            return json_response(status=400, data={'error': 'Invalid JSON data'})
        else:
            return await func(request, *args, **kwargs)
    return wrapper
