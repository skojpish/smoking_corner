import bcrypt
from aiohttp import BasicAuth
from aiohttp.web import middleware
from aiohttp.web_response import json_response

from src.database.db_queries import UserQs


@middleware
async def basic_auth_middleware(request, handler):
    if request.path_qs == '/registration':
        return await handler(request)

    auth_header = request.headers.get('Authorization')

    if auth_header:
        username, password, encoding = BasicAuth.decode(auth_header)

        password_db = await UserQs.get_user_password(username)

        if bcrypt.checkpw(password.encode('utf8'), bytes(password_db, 'utf8')):
            return await handler(request)

    return json_response(status=401, data={"error": "You are not authorized"}, headers={
                'WWW-Authenticate': 'Basic realm="Restricted Access"'
            })
