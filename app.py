from flask import Flask, request
from article_compare_tool import compare_two, compare_relative, compare_with_target
import json

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>hello</p>"


@app.route("/articles/two", methods=['POST'])
def handle_articles_two():
    try:
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            article_array = request.json
            return compare_two(article_array)
        else:
            return 'Content-Type not supported!'
    except Exception as e:
        print(f'exception occurred {e}')
        return 'exception occurred'


@app.route("/articles/compare", methods=['POST'])
def handle_articles_compare():
    try:
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            input_content = request.json
            target = input_content['target']
            compares = input_content['compares']
            return compare_with_target(target, compares)
        else:
            return 'Content-Type not supported!'
    except Exception as e:
        print(f'exception occurred {e}')
        return 'exception occurred'

