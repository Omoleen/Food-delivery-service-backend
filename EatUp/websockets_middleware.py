from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from pprint import pprint
from django.contrib.auth import get_user_model

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if "headers" in scope:
            headers = dict(scope["headers"])
            if b"authorization" in headers:
                try:
                    prefix, token = headers[b"authorization"].decode().split()
                    if prefix.lower() == "bearer":
                        jwt_authentication = JWTAuthentication()
                        validated_token = await database_sync_to_async(jwt_authentication.get_validated_token)(token)
                        payload = validated_token.payload
                        user_id = payload.get("user_id")
                        if user_id is not None:
                            user = await database_sync_to_async(User.objects.get)(id=user_id)
                            scope["user"] = user
                except (ValueError, AuthenticationFailed):
                    pass
        return await super().__call__(scope, receive, send)
