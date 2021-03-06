from typing import List, Optional

from authlib.jose.rfc7519.claims import JWTClaims
from starlette.authentication import SimpleUser

from .aad_token import AuthToken


class AadUser(SimpleUser):
    @staticmethod
    def create_user(**kwargs):

        user = AadUser(kwargs["username"])

        for key, value in kwargs.items():
            user.__dict__[key] = value

        return user

    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    username: str = None
    auth_token: Optional[AuthToken] = None
    roles_id: Optional[List[str]] = None
    groups: Optional[List[str]] = None
    scopes: Optional[List[str]] = None
    claims: Optional[JWTClaims] = None
    company: Optional[any] = None
    is_interactive: bool = True
