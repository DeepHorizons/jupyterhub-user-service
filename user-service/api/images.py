import json
import peewee
from playhouse.shortcuts import model_to_dict
from aiohttp import web
from models import Image
from .common import BaseView

app_routes = web.RouteTableDef()
app = web.Application()


@app_routes.view('', name='group')
class ImageView(BaseView):
    """
    List images that can be used

    Expects:
        * GET: Nothing
        * POST: A JSON object that has all the fields to the model

    Returns:
        * GET: 200: A dictionary of images
        * POST: 204: Created successfully

    Errors on:
        * POST:
            * 400: No JSON found or the JSON is malformed
            * 401: User is not an admin
            * 409: Image already in database

    POST is available to only admins
    """
    async def get(self):
        db = self.request.config_dict['db']
        all_images = await db.execute(Image.select())
        response = {image.id: model_to_dict(image) for image in all_images}
        return web.json_response(response)

    @BaseView.authenticated(admin=True)
    async def post(self):
        request = self.request
        user = request['jupyterhub-user']
        app = request.app
        db = self.request.config_dict['db']

        body = await request.json()
        if body is None:
            return web.json_response({'msg': "No data found; is the Content-Type `application/json`?"}, status=400)
        body = {k: v for k, v in body.items() if v}  # Sanitize; we don't like empty strings
        app.logger.info("body: {}".format(str(body)))

        try:
            await db.create(Image, **body)
        except peewee.IntegrityError as e:
            return web.json_response({'msg': "Error creating; {}".format(str(e))}, status=409)

        app.logger.warning("User `{user}` added image: `{body}`".format(user=user['name'], body=str(body)))
        return web.json_response({}, status=204)


@app_routes.view('/{imageid}', name='deleteimage')
class GetGroupView(BaseView):
    """
    Delete an image

    Expects:
        * a 'id` in the url

    Returns:
        * DELETE 204: Was successful

    Errors on:
        * 404: Nothing with that image id

    Delete is available to only admins
    """

    @BaseView.authenticated(admin=True)
    async def delete(self):
        imageid = self.request.match_info['imageid']
        jpy_user = self.request['jupyterhub-user']
        app = self.request.app
        db = self.request.config_dict['db']

        # Try to get the image
        try:
            image = await db.get(Image, Image.id == imageid)
        except Image.DoesNotExist:
            response = {'msg': "`{}` is not a valid group name".format(imageid)}
            raise web.HTTPNotFound(content_type='application/json', text=json.dumps(response))

        await db.delete(image)
        app.logger.warning("User `{admin_user}` deleted Image `{imageid}`".format(admin_user=jpy_user['name'], imageid=str(imageid)))
        return web.json_response({}, status=204)


app.add_routes(app_routes)
