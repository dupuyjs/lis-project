from flask import Flask
from transformers import pipeline

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/test")
def test():
    classifier = pipeline("sentiment-analysis")
    result = classifier("I've been waiting for a HuggingFace course my whole life.")
    return tupple(result)