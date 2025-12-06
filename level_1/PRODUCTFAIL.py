# -*- coding: utf-8 -*-
import csv
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ProductFail(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)          # for element *finding*
        self.wait = WebDriverWait(self.driver, 10)  # for explicit waits

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

    def test_product_fail(self):
        driver = self.driver
        wait = self.wait

        with open("level_1/data/product-fail.csv", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                name_input = row["Name"].strip()
                review_input = row["Review"].strip()
                expected_result_1 = row["ExpectedRes1"].strip()
                expected_result_2 = row["ExpectedRes2"].strip()
                expected_result_3 = row["ExpectedRes3"].strip()

                # open product page
                driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=product/product&path=34&product_id=33")

                # Name
                name_elem = self._find(driver, "id=input-name")
                name_elem.clear()
                name_elem.send_keys(name_input)

                # Review text
                review_elem = self._find(driver, "id=input-review")
                review_elem.clear()
                review_elem.send_keys(review_input)

                # Submit review
                self._find(driver, "id=button-review").click()

                # ---- Wait for validation message ----
                # This is the same locator you used, but now we **wait** for its text.
                by = By.XPATH
                value = "//form[@id='form-review']/div[2]"

                # Wait until the container is visible
                wait.until(EC.visibility_of_element_located((by, value)))
                # Wait until it contains some non-empty text
                wait.until(lambda d: d.find_element(by, value).text.strip() != "")

                result_elem = driver.find_element(by, value)
                actual_text = result_elem.text.strip()

                # Safer to use "contains" just like Katalon often does
                self.assertIn(expected_result_1, actual_text)
                self.assertIn(expected_result_2, actual_text)
                self.assertIn(expected_result_3, actual_text)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
