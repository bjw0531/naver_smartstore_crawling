from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class WebDriver:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--disable-blink-features=AutomationControlled")  # 봇 탐지 방지
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("disable-gpu")
        self.options.add_argument("disable-infobars")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument("--disable-extensions")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        self.options.add_argument("--disable-dev-shm-usage")

        # 드라이버 설치 및 실행
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)

        # 드라이버 흔적 삭제
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
            """
        })

        self.driver.implicitly_wait(10)

    def __del__(self):
        self.driver.quit()

    def get(self, url):
        self.driver.get(url)

    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def wait_page_load(self, xpath, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

    def scroll_down(self, scroll_amount=3000):
        self.driver.execute_script(f"window.scrollTo(0, {scroll_amount});")

    def find_xpath(self, xpath):
        return self.driver.find_element(By.XPATH, xpath)
