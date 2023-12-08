from datetime import time
import pickle
from urllib.parse import urlparse
from selenium.common.exceptions import NoSuchElementException
import threading
from article import Article
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from abc import ABC, abstractmethod
import configparser

lock = threading.Lock()


class PageCrawler(ABC):
    _htmlContent = ""

    def __init__(self, headless, page_url, commands):
        self._headless = headless or False
        self._page_url = page_url
        self._commands = commands
        self._driver = None
        self._cookies_path = ""

    def __load_cookies(self):
        if self._cookies_path:
            try:
                host_name = urlparse(self._page_url).hostname
                home_url = "https://" + host_name
                self.__driver.get(home_url)
                cookies = pickle.load(open(self._cookies_path, "rb"))
                for cookie in cookies:
                    if "expiry" in cookie:
                        del cookie["expiry"]
                    else:
                        self._driver.add_cookie(cookie)
                self._driver.refresh()
            except Exception as e:
                # it'll fail for the first time, when cookie file is not present
                print(str(e))
                print("Error loading cookies")

    def __save_cookies(self):
        # save cookies
        cookies = self._driver.get_cookies()
        pickle.dump(cookies, open(self._cookies_path, "wb"))

    def __init_driver(self):
        cfp = configparser.RawConfigParser()
        cfp.read("config.ini", encoding="utf-8")
        driver_path = cfp["driver"]["driverPath"]
        self._cookies_path = cfp["driver"]["cookiesPath"]

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
        if self._headless:
            options.add_argument(arg_headless)

        self._driver = webdriver.Chrome(executable_path=driver_path, options=options)
        self.__load_cookies()

    def __open_page(self):
        print(f"open page {self._page_url}")
        self._driver.get(self._page_url)

    def __close_driver(self):
        if self._driver:
            self.__save_cookies()
            self._driver.close()
            self._driver.quit()

    def __get_page_source(self):
        # find body
        wait = WebDriverWait(self._driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.__process_commands()
        print(f"after process commands, get page source")
        self._htmlContent = self._driver.page_source

        # elem = self._driver.find_element("xpath", "//*")
        # self._htmlContent = elem.get_attribute("outerHTML")

    def __process_click_command(self, command):
        if "selector" in command:
            loop = command["loop"] if "loop" in command else 1
            print(f'click {command["selector"]} {loop} times')
            for i in range(loop):
                try:
                    wait = WebDriverWait(self._driver, 10)
                    result = wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, command["selector"])
                        )
                    )
                    print(f'element found {command["selector"]} {result}')
                    result = self.driver.find_element(
                        By.CSS_SELECTOR, command["selector"]
                    ).click()
                    print(f'element click {command["selector"]} {result}')
                    wait = WebDriverWait(self._driver, 10)
                    result = wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, command["selector"])
                        )
                    )
                except TimeoutException as ex:
                    print(f'click {command["selector"]} timeout')

    def __process_wait_element(self, command):
        if "selector" in command:
            try:
                wait = WebDriverWait(self._driver, 10)
                result = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, command["selector"])
                    )
                )
                return True
            except TimeoutException as ex:
                print(f'wait {command["selector"]} timeout')
                return False

    def __process_commands(self):
        for command in self._commands:
            if command["action"] == "click":
                self.__process_click_command(command)
            if command["action"] == "wait":
                self.__process_wait_element(command)
            if command["action"] == "scrolldown":
                self.__process_scrolldown(command)
            if command["action"] == "login":
                result = self.__process_login(command)
                if result == False:
                    raise CrawlerProcessException("login failed")

    def __process_scrolldown(self, command):
        # Get scroll height.
        last_height = self._driver.execute_script("return document.body.scrollHeight")
        loop = command["loop"] if "loop" in command else 1
        print(f'scroll {command["selector"]} {loop} times')
        for i in range(loop):
            # Scroll down to the bottom.
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            # Wait to load the page.
            time.sleep(2)

            # Calculate new scroll height and compare with last scroll height.
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                continue

            last_height = new_height

            self._driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

    def __process_login(self, command):
        # check if logined
        logined = self.__process_wait_element(
            {"selector": command["logined"]["selector"]}
        )
        if logined:
            print("already logined")
            return True

        if command["show_login_button"] and "selector" in command["show_login_button"]:
            show_login_button = self._driver.find_element_by_css_selector(
                command["show_login_button"]["selector"]
            )
            if show_login_button == None:
                print(f"show login button not found")
                return False
            show_login_button.click()

        # wait login button appear
        self.__process_wait_element({"selector": command["login_button"]["selector"]})

        login_box = self._driver.find_element_by_css_selector(
            command["login_button"]["selector"]
        )
        if login_box == None:
            print(f"login button not found")
            return False

        username_box = self._driver.find_element_by_css_selector(
            command["username"]["selector"]
        )
        username_box.send_keys(command["username"]["value"])
        password_box = self._driver.find_element_by_css_selector(
            command["password"]["selector"]
        )
        password_box.send_keys(command["password"]["value"])
        login_box = self._driver.find_element_by_css_selector(
            command["login_button"]["selector"]
        )
        if login_box:
            login_box.click()
        else:
            print(f"login button not found")
            return False

        logined = self.__process_wait_element(
            {"selector": command["logined"]["selector"]}
        )

        if logined:
            print("login success")
            return True

        print("login failed")

        return False

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
            print(f"Exception occurred {Exception}")
        finally:
            self.__close_driver()
            lock.release()
        return self._htmlContent


class CrawlerProcessException(Exception):
    """Raised when the process error occurred"""

    pass
