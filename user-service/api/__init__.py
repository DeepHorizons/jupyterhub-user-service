import inspect
from aiohttp import web
from .users import app as user_app
from .groups import app as group_app

apiapp_routes = web.RouteTableDef()
apiapp = web.Application()
apiapp.add_subapp('/user', user_app)
apiapp.add_subapp('/group', group_app)


@apiapp_routes.view('', name='api')
class Api(web.View):
    """
    Update a users or groups permissions for the RIT Jupyterhub service
    """
    @classmethod
    def gen_docstring(cls):
        # Display the docstrings for each endpoint
        # XXX TODO This currently does not work, claming an error about a key error 'path'

        routes = [route for a in (user_app, group_app) for router_name in a.router for route in a.router[router_name]._routes]
        docstrings = {}
        for route in routes:
            try:
                path = route.get_info()['path']
            except KeyError:
                # If they have a {variable} then its formatter
                path = route.get_info()['formatter']

            docstrings[path] = route.handler.gen_docstring()

        doc = "{doc}\n{routes}".format(doc=inspect.getdoc(cls), routes='\n\n'.join(['{path}:\n{doc}'.format(path=key, doc=value) for key, value in docstrings.items()]))
        return doc

    async def get(self):
        """
        Get some text
        """
        return web.Response(text=self.gen_docstring())


apiapp.add_routes(apiapp_routes)
