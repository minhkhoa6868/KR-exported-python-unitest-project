# -*- coding: utf-8 -*-
import csv
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginFail(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)

    # ---------- locator helpers ----------

    def _parse_locator(self, locator: str):
        if locator is None:
            raise ValueError("Empty locator")

        locator = locator.strip()

        # Strip wrapping quotes like "xpath=//div[...]"
        if locator.startswith('"') and locator.endswith('"') and len(locator) >= 2:
            locator = locator[1:-1].strip()

        if locator.startswith("id="):
            return By.ID, locator[3:]
        elif locator.startswith("name="):
            return By.NAME, locator[5:]
        elif locator.startswith("css="):
            return By.CSS_SELECTOR, locator[4:]
        elif locator.startswith("xpath="):
            return By.XPATH, locator[6:]
        elif locator.startswith("link="):
            return By.LINK_TEXT, locator[5:]

        if locator.startswith("//") or locator.startswith(".//") or locator.startswith("(//"):
            return By.XPATH, locator

        # fallback: treat as CSS
        return By.CSS_SELECTOR, locator

    def _find(self, locator: str):
        by, value = self._parse_locator(locator)
        return self.driver.find_element(by, value)

    # ---------- test ----------

    def test_login_fail(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        with open("level_1/data/login_error.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader, start=1):
                email_input = row["Email"].strip()
                password_input = row["Password"].strip()
                expected_result = row["ExpectedRes"].strip()
                
                with self.subTest(dataset=i, email=email_input):

                    # open login page
                    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/login")

                    # email
                    email_elem = self._find("id=input-email")
                    email_elem.clear()
                    email_elem.send_keys(email_input)

                    # password
                    pwd_elem = self._find("id=input-password")
                    pwd_elem.clear()
                    pwd_elem.send_keys(password_input)

                    # click login
                    self._find("xpath=//input[@value='Login']").click()

                    # otherwise, we expect an error message containing expected_result
                    by, value = self._parse_locator("css=div.alert.alert-danger")

                    # wait for the error alert to be visible
                    alert_elem = wait.until(EC.visibility_of_element_located((by, value)))

                    actual_text = alert_elem.text.strip()

                    self.assertIn(expected_result, actual_text)
                    
                    print(f"Dataset {i}: PASSED")

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)