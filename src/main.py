from aiohttp import web

from routes import auth_routes, public_routes, admin_routes
from middlewares import basic_auth_middleware

app = web.Application(middlewares=[
    basic_auth_middleware,
])
app.add_routes(auth_routes.router)
app.add_routes(public_routes.router)
app.add_routes(admin_routes.router)

if __name__ == '__main__':
    web.run_app(app)
