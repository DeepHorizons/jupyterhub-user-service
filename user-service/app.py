import os
from aiohttp import web
import aiohttp_jinja2
import jinja2
from models import objects as db
from api import apiapp
from views import Index

prefix = os.environ.get('JUPYTERHUB_SERVICE_PREFIX', '/')


def create_app(argv=''):
    """
    Create and return the aiohttp app
    Used for `adev runserver`
    """
    app = web.Application()
    app['db'] = db
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates'))
    app.add_routes([web.get('/', Index)])
    app.add_subapp(prefix + 'api', apiapp)
    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app, port=16001)
