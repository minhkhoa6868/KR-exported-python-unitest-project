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

        with open("level_2/data/success_login.csv", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # One row per data set (like Katalon’s data-driven run)
            for i, row in enumerate(reader, start=1):
                site_url = row["siteUrl"]
                target_email = row["targetEmail"]
                email_input = row["emailInput"].strip()
                target_password = row["targetPassword"]
                password_input = row["passwordInput"].strip()
                btn_login = row["btnLoginTarget"]
                target_result = row["targetResult"]
                expected_result = row["expectedResult"].strip()
                btn_logout = row["btnLogoutTarget"]
                
                with self.subTest(dataset=i, siteUrl=site_url):
                
                    # === open ${siteUrl} ===
                    driver.get(site_url)

                    # === click + type email ===
                    email_elem = self._find(driver, target_email)
                    email_elem.clear()
                    email_elem.send_keys(email_input)

                    # === click + type password ===
                    pwd_elem = self._find(driver, target_password)
                    pwd_elem.clear()
                    pwd_elem.send_keys(password_input)

                    # === click login button ===
                    self._find(driver, btn_login).click()

                    # === verifyText ${targetResult} ${expectedResult} ===
                    result_elem = self._find(driver, target_result)
                    self.assertEqual(expected_result, result_elem.text.strip())

                    # === click logout button ===
                    self._find(driver, btn_logout).click()
                    
                    print(f"Dataset {i}: PASSED")

        # === endLoadVars (nothing to do, loop finished) ===

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
