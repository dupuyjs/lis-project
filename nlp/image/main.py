import os
import pathlib
from fastapi import FastAPI, Depends
from transformers import pipeline
from aad import AadBearerMiddleware, authorize, oauth2_scheme
from starlette.middleware.authentication import AuthenticationMiddleware
from dotenv import load_dotenv
from starlette.requests import Request

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

classifier = pipeline("sentiment-analysis")

@app.get('/api/healthcheck', status_code=200)
async def healthcheck():
    return 'Ready'

@app.get('/api/sentiment') 
async def predict(sentence: str, request: Request, token=Depends(oauth2_scheme())):
    result = classifier(sentence)
    return result[0]

@app.get('/api/me') 
async def predict(request: Request, token=Depends(oauth2_scheme())):
    return request.user