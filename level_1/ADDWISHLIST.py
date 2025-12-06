# -*- coding: utf-8 -*-
import csv
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AddWishList(unittest.TestCase):

    def setUp(self):
        # Chrome; works with Selenium 4 (Selenium Manager) or with chromedriver in PATH
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)

    # ---------- locator helpers ----------

    def _parse_locator(self, locator: str):
        """Convert Katalon-style locator string into (By, value)."""
        if locator is None:
            raise ValueError("Empty locator")

        locator = locator.strip()

        # Strip wrapping quotes from CSV like "xpath=//div[...]" or "//a[...]"
        if locator.startswith('"') and locator.endswith('"') and len(locator) >= 2:
            locator = locator[1:-1].strip()

        # Katalon / Selenium IDE styles
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

        # Bare XPath: //..., .//..., (//...)
        if locator.startswith("//") or locator.startswith(".//") or locator.startswith("(//"):
            return By.XPATH, locator

        # Fallback: treat as CSS selector
        return By.CSS_SELECTOR, locator

    def _find(self, locator: str):
        """Shortcut around driver.find_element using Katalon-style locators."""
        by, value = self._parse_locator(locator)
        return self.driver.find_element(by, value)

    # ---------- test ----------

    def test_add_wish_list(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        with open("data/wishlist_test_data.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                site_url = row["siteUrl"]
                target_email = row["targetEmail"]
                email_input = row["emailInput"]
                target_password = row["targetPassword"]
                password_input = row["passwordInput"]
                btn_login = row["btnLoginTarget"]
                target_result = row["targetResult"]
                expected_result = row["expectedResult"]

                # --- open ${siteUrl} ---
                driver.get(site_url)

                # --- email field ---
                email_elem = self._find(target_email)
                email_elem.clear()
                email_elem.send_keys(email_input)

                # --- password field ---
                pwd_elem = self._find(target_password)
                pwd_elem.clear()
                pwd_elem.send_keys(password_input)

                # --- click login button ---
                self._find(btn_login).click()

                # --- verifyText ${targetResult} ${expectedResult} ---

                # Wait for the result element to be visible
                by, value = self._parse_locator(target_result)
                result_elem = wait.until(
                    EC.visibility_of_element_located((by, value))
                )

                # Wait until the element actually has some text
                wait.until(lambda d: result_elem.text.strip() != "")

                actual_text = result_elem.text.strip()

                # Katalon verifyText is closer to "contains" than strict equality
                self.assertIn(expected_result, actual_text)

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
