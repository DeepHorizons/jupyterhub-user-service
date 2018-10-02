import functools
import os
import urllib
import urllib.parse
import aiohttp
from aiohttp import web


class BaseView(web.View):
    @classmethod
    def gen_docstring(cls):
        return cls.__doc__

    async def _api_request(self, endpoint):
        async with aiohttp.ClientSession() as session:
            JUPYTERHUB_API_URL = os.environ["JUPYTERHUB_API_URL"]
            JUPYTERHUB_API_TOKEN = os.environ['JUPYTERHUB_API_TOKEN']
            url = '/'.join(([JUPYTERHUB_API_URL,
                           endpoint,
                           ]))
            headers = {'Authorization': 'token %s' % JUPYTERHUB_API_TOKEN}

            async with session.get(url, headers=headers) as resp:
                user = await resp.json()
                return user

    async def user_for_cookie(self, encrypted_cookie, use_cache=True, session_id=''):
            endpoint = '/'.join(["authorizations/cookie/jupyterhub-services",
                                 urllib.parse.quote(encrypted_cookie, safe='')])
            return await self._api_request(endpoint)

    async def user_for_token(self, token, use_cache=True, session_id=''):
        endpoint = '/'.join(["authorizations/token",
                             urllib.parse.quote(token, safe='')])
        return await self._api_request(endpoint)

    @staticmethod
    def authenticated(group='', admin=False):
        def decorator(f):
            @functools.wraps(f)
            async def inner(self: BaseView, *args, **kwargs):
                user = {}
                try:
                    encrypted_cookie = self.request.cookies['jupyterhub-services']
                    if encrypted_cookie:
                        user = await self.user_for_cookie(encrypted_cookie)

                except KeyError:
                    try:
                        token = self.request.headers['token']
                        if token:
                            user = await self.user_for_token(token)
                    except KeyError:
                        pass

                self.request['jupyterhub-user'] = user  # Make it so the handlers can get the user

                if user:
                    if admin and group:
                        if (user['admin'] is True) and ('groups' in user) and (group in user['groups']):
                            return await f(self, *args, **kwargs)
                        else:
                            raise web.HTTPUnauthorized(reason="Could not authenticate user, Not an administrator or not in group `{group}`".format(group=group))
                    elif admin:
                        if user['admin'] is True:
                            return await f(self, *args, **kwargs)
                        else:
                            raise web.HTTPUnauthorized(reason="Could not authenticate user, Not an administrator")
                    elif group:
                        if ('groups' in user) and (group in user['groups']):
                            return await f(self, *args, **kwargs)
                        else:
                            raise web.HTTPUnauthorized(reason="Could not authenticate user, Not part of group `{group}`".format(group=group))
                    else:
                        return await f(self, *args, **kwargs)
                else:
                    # The user is not authenticated, go log in or use a token
                    raise web.HTTPUnauthorized(reason="Could not authenticate user, missing cookie or token")
            return inner
        return decorator
