
import jinja2
import aiohttp_jinja2
from aiohttp import web

app_routes = web.RouteTableDef()
app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates'))


@app_routes.view('', name='index')
class Index(web.View):
    async def get(self):
        response = aiohttp_jinja2.render_template('index.j2', self.request, {})
        return response


app.add_routes(app_routes)
