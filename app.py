from flask import Flask, request
from article_compare_tool import compare_two, compare_with_target
from article_crawler_crunchbase import ArticleCrawlerCrunchbase
from page_crawler import PageCrawler
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


@app.route("/page/crawler", methods=['POST'])
def handle_page_crawler():
    try:
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            input_content = request.json
            url = input_content['url']
            commands = input_content['commands']
            return PageCrawler(url, commands).process()
        else:
            return 'Content-Type not supported!'
    except Exception as e:
        print(f'exception occurred {e}')
        return 'exception occurred'

@app.route("/articles/crawler/crunchbase", methods=['POST'])
def handle_articles_crawler():
    """
    crawler to crunchbase, date format is like 'November 9, 2023'
    the return articles need transfer with json
    """
    try:
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            input_content = request.json
            date = input_content['date']
            articles = ArticleCrawlerCrunchbase(date).process()
            return json.dumps(articles, default=lambda o: o.__dict__)
        else:
            return 'Content-Type not supported!'
    except Exception as e:
        print(f'exception occurred {e}')
        return 'exception occurred'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
