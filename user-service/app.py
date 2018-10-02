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
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(template_path))
    app.add_routes([web.get(prefix, Index)])
    app.add_subapp(prefix + 'api', apiapp)
    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app, port=int(os.environ.get('PORT', 8080)))
