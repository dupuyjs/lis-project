from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()
classifier = pipeline("sentiment-analysis")

@app.get('/api/healthcheck', status_code=200)
async def healthcheck():
    return 'Ready'

@app.get('/api/sentiment')
async def predict(sentence: str):
    result = classifier(sentence)
    return result[0]