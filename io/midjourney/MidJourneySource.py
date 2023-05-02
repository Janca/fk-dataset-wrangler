import hashlib
import json
import time
import traceback

import cryptocode
import selenium
import selenium.webdriver
import selenium.webdriver.common.by
import selenium.webdriver.support.expected_conditions as expected_conditions
import selenium.webdriver.support.ui

from tasks.FkTask import FkImage as _FkImage
from tasks.io.FkSource import FkSource as _FkSource


class MidJourneySource(_FkSource):
    _XPATH_SIGN_IN_BUTTON = '//button[.//span[contains(text(), "Sign In")]]'

    def __init__(self, src_path: str, username: str, password: str, driver: str = "firefox"):
        self.username = username
        self.password = password
        self.driver = driver
        super().__init__(src_path)

    def _load_cookies(self):
        username_hash = hashlib.sha256(self.username.encode("utf-8")).hexdigest()
        cookies_path = f"./{username_hash}.cookies.json"

        cookies: dict[str, any] = {}

        with open(cookies_path, "r", encoding="utf-8") as cookie_file:
            decrypted_cookies = cryptocode.decrypt(cookie_file.read(), self.password)
            json_cookies = json.loads(decrypted_cookies)

        for json_cookie in json_cookies:
            c_name = json_cookie["name"]
            c_value = json_cookie["value"]

            if c_name == "__Secure-next-auth.session-token":
                c_expiry = json_cookie["expiry"] if "expiry" in json_cookie else -1
                c_expiry = int(c_expiry)

                now = int(time.time())
                if now >= c_expiry:
                    return None

            cookies[c_name] = c_value

        return cookies

    def load_cookies_from_browser(self):

        driver = None
        if self.driver == "firefox":
            driver = selenium.webdriver.Firefox()
        elif self.driver == "chrome":
            driver = selenium.webdriver.Chrome()
        else:
            raise RuntimeError(f"Unknown selenium driver '{self.driver}'.")

        def _find_element(by, selector):
            try:
                return selenium.webdriver.support.ui.WebDriverWait(driver, 10).until(
                    expected_conditions.presence_of_element_located(
                        (by, selector)
                    )
                )

            except:
                return None

        def _click_signin_button():
            sign_in_btn = _find_element(
                selenium.webdriver.common.by.By.XPATH,
                MidJourneySource._XPATH_SIGN_IN_BUTTON
            )

            if not sign_in_btn:
                return False

            driver.execute_script("arguments[0].scrollIntoView();", sign_in_btn)
            driver.execute_script("arguments[0].click();", sign_in_btn)

            return True

        def _handle_login_form():
            email_input = _find_element(
                selenium.webdriver.common.by.By.NAME,
                "email"
            )

            if not email_input:
                return False

            password_input = _find_element(
                selenium.webdriver.common.by.By.XPATH,
                "//input[@name='password']"
            )

            if not password_input:
                return False

            email_input.send_keys(self.username)
            password_input.send_keys(self.password)

            login_btn = _find_element(
                selenium.webdriver.common.by.By.XPATH,
                "//button[.//div[contains(text(), 'Log In')]]"
            )

            if not login_btn:
                return False

            login_btn.click()
            return True

        def _handle_additional_authorization():
            captcha_2fa_elem = _find_element(
                selenium.webdriver.common.by.By.XPATH,
                '//a[contains(@href, "https://www.hcaptcha.com/")] '
                '| //input[contains(@placeholder, "6-digit authentication code/8-digit backup code")] '
                '| //*[contains(text(), "Enter Discord Auth/Backup Code")]'
            )

            if not captcha_2fa_elem:
                return False

            print("2FA or catcha detected, please solve manually...")
            input("Press [Enter] to continue after solving captcha/2-factor...")

            return True

        def _authorize_app():
            authorize_btn = _find_element(
                selenium.webdriver.common.by.By.XPATH,
                '//button[.//div[contains(text(), "Authorize")]]'
            )

            if not authorize_btn:
                return False

            time.sleep(5)

            authorize_btn.click()
            return True

        def _save_cookies():
            if "https://www.midjourney.com/app/" not in driver.current_url:
                return False

            selenium_cookies = driver.get_cookies()

            json_cookies = json.dumps(selenium_cookies)
            encrypted_cookies = cryptocode.encrypt(json_cookies, self.password)

            username_hash = hashlib.sha256(self.username.encode("utf-8"))
            cookies_path = f"./{username_hash}.cookies.json"

            with open(cookies_path, "w+", encoding="utf-8") as cookies_file:
                cookies_file.write(encrypted_cookies)

            return True

        for attempt in range(3):
            try:
                driver.get("https://www.midjourney.com/home/")
                time.sleep(10)

                if not _click_signin_button():
                    continue

                time.sleep(5)
                if not _handle_login_form():
                    continue

                time.sleep(5)
                if not _handle_additional_authorization():
                    continue

                time.sleep(5)
                if not _authorize_app():
                    continue

                time.sleep(5)
                if not _save_cookies():
                    continue

            except Exception as e:
                print(f"Login attempt {attempt} failed...")
                traceback.print_exception(e)



    def yield_next(self) -> _FkImage:
        pass
