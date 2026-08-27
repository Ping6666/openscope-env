from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException


class OpenScope_Webdriver():
    driver: WebDriver
    complete: bool

    def __init__(self, driver_path: str, url: str, render: bool):
        self.driver_path = driver_path
        self.render = render
        self.complete = False

        self.driver = None

        self._init_driver()
        self._load_webpage(url)
        return

    def __del__(self):
        if self.driver is not None:
            self.driver.quit()
            del self.driver
        return

    def _init_driver(self):
        # --- options --- #

        options = ChromeOptions()
        options.add_argument('--no-sandbox')

        if not self.render:
            options.add_argument("--headless")
        else:
            options.add_argument("--window-size=850,960")

        # desired capabilities
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

        # --- service & driver --- #

        service = Service(self.driver_path)

        self.driver = Chrome(service=service, options=options)
        return

    def _load_webpage(self, url: str):
        try:
            self.driver.get(url)
            self.complete = True
        except WebDriverException:
            print("Start the OpenScope server first!")
        except Exception as e:
            print("OpenScopeWebdriver.load_webpage | Exception", e)
            raise
        return
