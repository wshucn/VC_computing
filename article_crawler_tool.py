from selenium.common.exceptions import NoSuchElementException

from selenium import webdriver
from selenium.webdriver.common.by import By
from article import Article
import datetime
import os
import json

# const
ARG_ENABLE_LOCAL_STORE = "user-data-dir=selenium"
ARG_DISABLE_INFOBAR = "disable-infobars"
ARG_DISABLE_IMAGE = "blink-settings=imagesEnabled=false"
ARG_ORIGIN_PASS = "--remote-allow-origins=*"
ARG_HEADLESS = "--headless"
ARG_DISABLE_AUTO_CONTROL = "--disable-blink-features=AutomationControlled"
ARG_NO_SANDBOX = "--no-sandbox"
ARG_DISABLE_DEV = "--disable-dev-shm-usage"
ARG_USER_AGENT = "user-agent=Mozilla/5.0 (Macintosh Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
# prepare chrome driver options
options = webdriver.ChromeOptions()
options.add_argument(ARG_ORIGIN_PASS)
options.add_argument(ARG_DISABLE_AUTO_CONTROL)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument(ARG_DISABLE_INFOBAR)
options.add_argument(ARG_NO_SANDBOX)
options.add_argument(ARG_DISABLE_DEV)
options.add_argument(ARG_USER_AGENT)
options.add_argument(ARG_ENABLE_LOCAL_STORE)
options.add_argument(ARG_DISABLE_IMAGE)
options.add_argument(ARG_HEADLESS)

# selector
headerDiv = "div#herald-module-0-0 div.entry-header,div#herald-module-1-0 div.entry-header"
titleAHref = "h2.entry-title a"
metaItemDiv = "div.meta-item"
contentP = "div.entry-content p,div.entry-content h2"
updateSpan = "span.updated"
titleH1 = "h1.entry-title"
categorySpan = "header.entry-header span.meta-category a"

# instance driver
driver = webdriver.Chrome(executable_path="./chrome_driver/chromedriver_chromium", options=options)
articles = []
search_day = 'November 7, 2023'


def open_page(site):
    driver.get(site)


def list_articles():
    global articles
    headers = driver.find_elements(By.CSS_SELECTOR, headerDiv)
    articles = [search_from_header(header) for header in headers]


def process_each():
    for article in articles:
        driver.get(article.url)
        try:
            update_time = driver.find_element(By.CSS_SELECTOR, updateSpan).text
            if update_time == search_day:
                title = driver.find_element(By.CSS_SELECTOR, titleH1).text
                article.set_title(title)
                els = driver.find_elements(By.CSS_SELECTOR, contentP)
                contents = [el.text for el in els]
                article.set_content(os.sep.join(contents))
                c_els = driver.find_elements(By.CSS_SELECTOR, categorySpan)
                categories = [el.text for el in c_els]
                article.set_categories(categories)
        except NoSuchElementException:
            print('no such element')


def close_driver():
    driver.close()
    driver.quit()


def search_from_header(header):
    article = Article(None, None, None, None, None)
    article.set_update_time(search_day)
    title_els = header.find_elements(By.CSS_SELECTOR, titleAHref)
    if len(title_els) > 0:
        article.set_url(title_els[0].get_attribute("href"))
        article.set_title(title_els[0].text)
    date_els = header.find_elements(By.CSS_SELECTOR, metaItemDiv)
    date_str = [el.text for el in date_els]
    for s in date_str:
        if validate(s):
            article.set_update_time(s)
            break
    return article


def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%B %-d %Y')
        return True
    except ValueError:
        return False


def article_crawler(site, date):
    global search_day
    search_day = date
    try:
        open_page(site)
        list_articles()
        process_each()
        result = [article for article in articles if article.content is not None]
        return json.dumps(result, default=lambda o: o.__dict__)
    finally:
        close_driver()


if __name__ == '__main__':
    article_crawler("https://news.crunchbase.com/", "November 7, 2023")
