from flask import Flask, request
from transformers import pipeline

app = Flask(__name__)
classifier = pipeline("sentiment-analysis")

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/sentiment")
def test():
    args = request.args

    if "sentence" in args:
        sentence = args.get("sentence")
        result = classifier(sentence)
        return result[0], 200
    else:
        return "No query string received", 200