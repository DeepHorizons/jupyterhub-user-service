
import json
import peewee
from playhouse.shortcuts import model_to_dict, dict_to_model
from aiohttp import web
from models import User, Group
from .common import BaseView

app_routes = web.RouteTableDef()
app = web.Application()


@app_routes.view('', name='user')
class UserView(BaseView):
    """
    List users or add a user to the database

    Expects:
        * GET: Nothing
        * POST: A JSON object that has all the fields to the model

    Returns:
        * GET: 200: A dictionary of users to permissions
        * POST: 204: Created successfully

    Errors on:
        * POST:
            * 400: No JSON found or the JSON is malformed
            * 401: User is not an admin
            * 409: User already in database

    POST is available to only admins
    """
    async def get(self):
        db = self.request.config_dict['db']
        all_users = await db.execute(User.select())
        response = {user.username: model_to_dict(user) for user in all_users}
        return web.json_response(response)

    @BaseView.authenticated(admin=True)
    async def post(self):
        request = self.request
        jpy_user = request['jupyterhub-user']
        app = request.app
        db = self.request.config_dict['db']

        body = await request.json()
        if body is None:
            return web.json_response({'msg': "No data found; is the Content-Type `application/json`?"}, status=400)
        body = {k: v for k, v in body.items() if v}  # Sanitize; we don't like empty strings
        app.logger.info("body: {}".format(str(body)))

        try:
            await db.create(User, **body)
        except peewee.IntegrityError as e:
            return web.json_response({'msg': "Error creating; {}".format(str(e))}, status=409)
        app.logger.warning("User `{admin_user}` added user: `{body}`".format(admin_user=jpy_user['name'], body=str(body)))

        return web.json_response({}, status=204)


@app_routes.view('/{username}', name='getuser')
class GetUserView(BaseView):
    """
    Get or delete a user

    Expects:
        * a 'username` in the url

    Returns:
        * GET: 200: A formated string under the key `string` in a JSON object
        * DELETEL 204: Was successful

    Errors on:
        * 404: Nothing with that username

    Delete is available to only admins
    """
    async def get(self):
        username = self.request.match_info['username']
        db = self.request.config_dict['db']
        # Try to get the image
        try:
            user = await db.get(User, User.username == username)
        except User.DoesNotExist:
            response = {'msg': "`{}` is not a valid username".format(username)}
            raise web.HTTPNotFound(content_type='application/json', text=json.dumps(response))

        user = model_to_dict(user)
        return web.json_response(user)

    @BaseView.authenticated(admin=True)
    async def delete(self):
        username = self.request.match_info['username']
        jpy_user = self.request['jupyterhub-user']
        app = self.request.app
        db = self.request.config_dict['db']

        # Try to get the image
        try:
            user = await db.get(User, User.username == username)
        except User.DoesNotExist:
            response = {'msg': "`{}` is not a valid username".format(username)}
            raise web.HTTPNotFound(content_type='application/json', text=json.dumps(response))

        await db.delete(user)

        app.logger.warning("User `{admin_user}` deleted User `{username}`".format(admin_user=jpy_user['name'], username=str(username)))
        return web.json_response({}, status=204)


app.add_routes(app_routes)
