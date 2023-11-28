from selenium.common.exceptions import NoSuchElementException
import threading
from article import Article
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from abc import ABC, abstractmethod
import configparser

lock = threading.Lock()

class PageCrawler(ABC):
    _htmlContent = ''

    def __init__(self, page_url, commands):
        self._page_url = page_url
        self._commands = commands
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
        print(f'open page {self._page_url}')
        self._driver.get(self._page_url)

    def __close_driver(self):
        if self._driver:
            self._driver.close()
            self._driver.quit()

    def __get_page_source(self):
        # find body
        wait = WebDriverWait(self._driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.__process_commands()  
        self._htmlContent = self._driver.page_source

        # elem = self._driver.find_element("xpath", "//*")
        # self._htmlContent = elem.get_attribute("outerHTML")

    def __process_commands(self):
        for command in self._commands:
            if command['action'] == 'click':
                if 'selector' in command:
                    loop =  command['loop'] if 'loop' in command else 1
                    print(f'click {command["selector"]} {loop} times')
                    for i in range(loop):
                        wait = WebDriverWait(self._driver, 10)
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, command['selector']))).click()
            else:
                raise CrawlerProcessException('command not supported')

    @property
    def driver(self):
        return self._driver


    def process(self):
        try:
            lock.acquire()
            self.__init_driver()
            self.__open_page()
            self.__get_page_source()
        except CrawlerProcessException:
            print(f'Exception occurred {Exception}')
        finally:
            self.__close_driver()
            lock.release()
        return self._htmlContent

class CrawlerProcessException(Exception):
    """Raised when the process error occurred"""
    pass
