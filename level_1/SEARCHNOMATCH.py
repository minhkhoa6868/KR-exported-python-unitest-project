# -*- coding: utf-8 -*-
import csv
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

class SearchNoMatch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)              # for locating elements
        self.wait = WebDriverWait(self.driver, 10)   # for explicit waits

    def _find(self, driver, locator: str):
        if locator is None:
            raise ValueError("Empty locator")

        locator = locator.strip()

        # Strip wrapping quotes from CSV like "xpath=...." or "//a[...]"
        if locator.startswith('"') and locator.endswith('"') and len(locator) >= 2:
            locator = locator[1:-1].strip()

        # Katalon / Selenium IDE style locators
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

        # Bare XPath (//, .//, (//)
        if locator.startswith("//") or locator.startswith(".//") or locator.startswith("(//"):
            return driver.find_element(By.XPATH, locator)

        # Fallback: treat as CSS selector
        return driver.find_element(By.CSS_SELECTOR, locator)

    def test_search_no_match(self):
        driver = self.driver
        wait = self.wait

        with open("level_1/data/search-no-match.csv", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                search_input = row["Keywords"].strip()
                expected_result = row["ExpectedRes"].strip()

                # open home page
                driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=common/home")

                # Enter search keywords
                search_elem = self._find(driver, "name=search")
                search_elem.clear()
                search_elem.send_keys(search_input)

                # Click search button
                self._find(driver, "xpath=//button[@type='submit']").click()

                # ---- verify error ----
                error_locator = (By.XPATH, "//div[@id='entry_212469']/p")
                result_elem = wait.until(EC.visibility_of_element_located(error_locator))
                actual_text = result_elem.text.strip()

                self.assertEqual(expected_result, actual_text)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
