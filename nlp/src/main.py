import os
import pathlib
from fastapi import FastAPI, Depends
from starlette.exceptions import HTTPException
from transformers import pipeline
from aad import AadBearerMiddleware, authorize, oauth2_scheme, AadAuthenticationClient, ScopeType, AuthError
from starlette.middleware.authentication import AuthenticationMiddleware
from dotenv import load_dotenv
from starlette.requests import Request
import requests

dir = pathlib.Path(__file__).parent.parent.absolute()
localenv = os.path.join(dir, "local.env")
if os.path.exists(localenv):
    load_dotenv(localenv, override=True)

client_id = os.environ.get("CLIENT_ID")

# pre fill client id
swagger_ui_init_oauth = {
    "usePkceWithAuthorizationCodeGrant": "true",
    "clientId": client_id,
    "appName": "LIS",
}

app = FastAPI(
     swagger_ui_init_oauth=swagger_ui_init_oauth,
)

# Add the bearer middleware
app.add_middleware(AuthenticationMiddleware, backend=AadBearerMiddleware())

fill_mask = pipeline("fill-mask", model="camembert-base", tokenizer="camembert-base")

@app.get('/api/healthcheck', status_code=200, tags=["api"])
async def healthcheck():
    return 'Ready'

@app.get('/api/autosuggest', tags=["api"]) 
async def autosuggest(sentence: str, request: Request, token=Depends(oauth2_scheme())):
    results = fill_mask(sentence)
    return results

@app.get('/request/me', tags=["request"]) 
async def request_user_me(request: Request, token=Depends(oauth2_scheme())):
    return request.user

@app.get('/graph/me', tags=["graph"]) 
async def graph_me(request: Request, token=Depends(oauth2_scheme())):

    aad_client = AadAuthenticationClient()

    try:
        # Get a new token on behalf of the user, with new scopes
        authorized_graph_user = await aad_client.acquire_user_token(
            user=request.user, scopes=["user.read"], validate=False
        )

    except AuthError as aex:
        raise HTTPException(aex.status_code, aex.description)
    except Exception as ex:
        httpex = HTTPException(400, "Can't get a token on behalf of the user", ex)
        raise httpex

    try:
        response = requests.get("https://graph.microsoft.com/beta/me",
            auth=authorized_graph_user.auth_token
        )

        jsonvalue = response.json()

        return jsonvalue

    except AuthError as aex:
        raise HTTPException(aex.status_code, aex.description)
    except Exception as ex:
        httpex = HTTPException(400, "Can't get user's profile", ex)
        raise httpex

