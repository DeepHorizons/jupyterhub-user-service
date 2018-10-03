
import json
import peewee
from playhouse.shortcuts import model_to_dict, dict_to_model
from aiohttp import web
from models import User, Group
from .common import BaseView

app_routes = web.RouteTableDef()
app = web.Application()


@app_routes.view('', name='group')
class GroupView(BaseView):
    """
    List groups or add a group to the database

    Expects:
        * GET: Nothing
        * POST: A JSON object that has all the fields to the model

    Returns:
        * GET: 200: A dictionary of groups
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
        all_groups = await db.execute(Group.select())
        response = {group.groupname: model_to_dict(group) for group in all_groups}
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
            await db.create(Group, **body)
        except peewee.IntegrityError as e:
            return web.json_response({'msg': "Error creating; {}".format(str(e))}, status=409)

        app.logger.warning("User `{user}` added group: `{body}`".format(user=user['name'], body=str(body)))
        return web.json_response({}, status=204)


@app_routes.view('/{groupname}', name='getgroup')
class GetGroupView(BaseView):
    """
    Get or delete a group

    Expects:
        * a 'groupname` in the url

    Returns:
        * GET: 200: A formated string under the key `string` in a JSON object
        * DELETEL 204: Was successful

    Errors on:
        * 404: Nothing with that groupname

    Delete is available to only admins
    """
    async def get(self):
        groupname = self.request.match_info['groupname']
        db = self.request.config_dict['db']

        # Try to get the image
        try:
            group = await db.get(Group, Group.groupname == groupname)
        except User.DoesNotExist:
            response = {'msg': "`{}` is not a valid group name".format(groupname)}
            raise web.HTTPNotFound(content_type='application/json', text=json.dumps(response))

        group_dict = model_to_dict(group)
        return web.json_response(group_dict)

    @BaseView.authenticated(admin=True)
    async def delete(self):
        groupname = self.request.match_info['groupname']
        jpy_user = self.request['jupyterhub-user']
        app = self.request.app
        db = self.request.config_dict['db']

        # Try to get the image
        try:
            group = await db.get(Group, Group.groupname == groupname)
        except User.DoesNotExist:
            response = {'msg': "`{}` is not a valid group name".format(groupname)}
            raise web.HTTPNotFound(content_type='application/json', text=json.dumps(response))

        await db.delete(group)
        app.logger.warning("User `{admin_user}` deleted Group `{groupname}`".format(admin_user=jpy_user['name'], groupname=str(groupname)))
        return web.json_response({}, status=204)


app.add_routes(app_routes)
