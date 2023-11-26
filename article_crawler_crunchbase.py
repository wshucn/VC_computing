from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.common.by import By
from article import Article
import os
from article_crawler import ArticleCrawler
from utils import validate_date


class ArticleCrawlerCrunchbase(ArticleCrawler):
    headerDiv = "div#herald-module-0-0 div.entry-header,div#herald-module-1-0 div.entry-header"
    titleAHref = "h2.entry-title a"
    metaItemDiv = "div.meta-item"
    contentP = "div.entry-content p,div.entry-content h2"
    updateSpan = "span.updated"
    titleH1 = "h1.entry-title"
    categorySpan = "header.entry-header span.meta-category a"
    _articles: list[Article] = []

    def _get_site(self):
        return 'https://news.crunchbase.com/'

    def _list_articles(self):
        headers = super().driver.find_elements(By.CSS_SELECTOR, self.headerDiv)
        self._articles = [self.__search_from_header(header) for header in headers]

    def _process_each(self):
        for article in self._articles:
            super().driver.get(article.url)
            try:
                update_time = super().driver.find_element(By.CSS_SELECTOR, self.updateSpan).text
                if update_time == super().date:
                    title = super().driver.find_element(By.CSS_SELECTOR, self.titleH1).text
                    article.set_title(title)
                    els = super().driver.find_elements(By.CSS_SELECTOR, self.contentP)
                    contents = [el.text for el in els]
                    article.set_content(os.sep.join(contents))
                    c_els = super().driver.find_elements(By.CSS_SELECTOR, self.categorySpan)
                    categories = [el.text for el in c_els]
                    article.set_categories(categories)
            except NoSuchElementException:
                print('no such element')

    def _get_articles(self) -> list[Article]:
        result = [article for article in self._articles if article.content is not None]
        return result

    def __search_from_header(self, header):
        article = Article(None, None, None, None, None)
        article.set_update_time(super().date)
        title_els = header.find_elements(By.CSS_SELECTOR, self.titleAHref)
        if len(title_els) > 0:
            article.set_url(title_els[0].get_attribute("href"))
            article.set_title(title_els[0].text)
        date_els = header.find_elements(By.CSS_SELECTOR, self.metaItemDiv)
        date_str = [el.text for el in date_els]
        for s in date_str:
            if validate_date(s, '%B %-d %Y'):
                article.set_update_time(s)
                break
        return article
