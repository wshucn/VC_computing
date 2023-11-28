from selenium.common.exceptions import NoSuchElementException

from article import Article
from selenium import webdriver
from abc import ABC, abstractmethod
import configparser


class ArticleCrawler(ABC):
    
    def __init__(self, query_date):
        self._site = self._get_site()
        self._query_date = query_date
        self._driver = None

    def __init_driver(self):
        cfp = configparser.RawConfigParser()
        cfp.read('config.ini', encoding="utf-8")
        driver_path = cfp['driver']['driverPath']
        arg_enable_local_store = "user-data-dir=selenium"
        arg_disable_infobar = "disable-infobars"
        arg_disable_image = "blink-settings=imagesEnabled=false"
        arg_origin_pass = "--remote-allow-origins=*"
        arg_headless = "--headless"
        arg_disable_auto_control = "--disable-blink-features=AutomationControlled"
        arg_no_sandbox = "--no-sandbox"
        arg_disable_dev = "--disable-dev-shm-usage"
        arg_user_agent = "user-agent=Mozilla/5.0 (Macintosh Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        # prepare chrome driver options
        options = webdriver.ChromeOptions()
        options.add_argument(arg_origin_pass)
        options.add_argument(arg_disable_auto_control)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(arg_disable_infobar)
        options.add_argument(arg_no_sandbox)
        options.add_argument(arg_disable_dev)
        options.add_argument(arg_user_agent)
        options.add_argument(arg_enable_local_store)
        options.add_argument(arg_disable_image)
        options.add_argument(arg_headless)
        self._driver = webdriver.Chrome(executable_path=driver_path, options=options)

    def __open_page(self):
        self._driver.get(self._site)

    def __close_driver(self):
        if self._driver:
            self._driver.close()
            self._driver.quit()

    @property
    def driver(self):
        return self._driver

    @property
    def date(self):
        return self._query_date

    @abstractmethod
    def _get_site(self):
        return ''

    @abstractmethod
    def _list_articles(self):
        pass

    @abstractmethod
    def _process_each(self):
        pass

    @abstractmethod
    def _get_articles(self) -> list[Article]:
        return []

    def process(self):
        try:
            self.__init_driver()
            self.__open_page()
            self._list_articles()
            self._process_each()
        except CrawlerProcessException:
            print(f'Exception occurred {Exception}')
        finally:
            self.__close_driver()
        return self._get_articles()


class CrawlerProcessException(Exception):
    """Raised when the process error occurred"""
    pass
