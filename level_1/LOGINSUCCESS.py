# -*- coding: utf-8 -*-
import csv
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

class LoginSuccess(unittest.TestCase):

    def setUp(self):
        # Use your own chromedriver path or let Selenium Manager handle it
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)

    def _find(self, driver, locator):
        if locator is None:
            raise ValueError("Empty locator")

        locator = locator.strip()

        # 1) Strip wrapping quotes from CSV like "xpath=...." or "//a[...]" 
        if locator.startswith('"') and locator.endswith('"') and len(locator) >= 2:
            locator = locator[1:-1].strip()

        # 2) Katalon/Selenium IDE style locators
        if locator.startswith("id="):
            return driver.find_element(By.ID, locator[3:])
        elif locator.startswith("name="):
            return driver.find_element(By.NAME, locator[5:])
        elif locator.startswith("css="):
            return driver.find_element(By.CSS_SELECTOR, locator[4:])
        elif locator.startswith("xpath="):
            return driver.find_element(By.XPATH, locator[6:])
        elif locator.startswith("link="):
            return driver.find_element(By.LINK_TEXT, locator[5:])

        # 3) Bare XPath (e.g. //a[...], .//div, (//a)[1])
        elif locator.startswith("//") or locator.startswith(".//") or locator.startswith("(//"):
            return driver.find_element(By.XPATH, locator)

    def test_login_success(self):
        driver = self.driver

        # === this replaces Katalon: loadVars success_login.csv ===
        with open("level_1/data/login_success.csv", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # One row per data set (like Katalon’s data-driven run)
            for i, row in enumerate(reader, start=1):
                email_input = row["Email"].strip()
                password_input = row["Password"].strip()
                
                with self.subTest(dataset=i, email=email_input):
                
                    # === open ${siteUrl} ===
                    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/login")

                    # === click + type email ===
                    email_elem = self._find(driver, "id=input-email")
                    email_elem.clear()
                    email_elem.send_keys(email_input)

                    # === click + type password ===
                    pwd_elem = self._find(driver, "id=input-password")
                    pwd_elem.clear()
                    pwd_elem.send_keys(password_input)

                    # === click login button ===
                    self._find(driver, "xpath=//input[@value='Login']").click()

                    # === click logout button ===
                    self._find(driver, "link=Logout").click()
                    
                    print(f"Dataset {i}: PASSED")

        # === endLoadVars (nothing to do, loop finished) ===

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main(verbosity=2)
