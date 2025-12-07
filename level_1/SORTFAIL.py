# -*- coding: utf-8 -*-
import csv
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class SortFail(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)

    # ---------- locator helpers ----------

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

    # ---------- login helper ----------

    def _login_saucedemo(self):
        driver = self.driver
        wait = self.wait

        driver.get("https://www.saucedemo.com/")

        # username
        self._find(driver, "id=user-name").send_keys("standard_user")
        # password
        self._find(driver, "id=password").send_keys("secret_sauce")
        # login button
        self._find(driver, "id=login-button").click()

        # wait until inventory page is visible
        wait.until(EC.visibility_of_element_located((By.ID, "inventory_container")))

    # ---------- test: sort fail ----------

    def test_sort_fail(self):
        driver = self.driver
        wait = self.wait

        # login once
        self._login_saucedemo()

        with open("level_1/data/sort-fail.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader, start=1):
                sort_type = row["SortType"].strip()      # az / za / lohi / hilo
                product_price = row["ProductPrice"].strip()

                with self.subTest(dataset=i, sort=sort_type):
                    # always go back to inventory page for each dataset
                    driver.get("https://www.saucedemo.com/inventory.html")

                    # chọn kiểu sort
                    select_elem = self._find(
                        driver,
                        "css=select[data-test='product-sort-container']"
                    )
                    Select(select_elem).select_by_value(sort_type)

                    # price of the first product after sort
                    price_xpath_first = (
                        "//div[@id='inventory_container']/div/div/div/"
                        "div[1]/div[2]/div[2]/div"
                    )

                    price_elem_1 = wait.until(
                        EC.visibility_of_element_located((By.XPATH, price_xpath_first))
                    )
                    actual_price_1 = price_elem_1.text.strip()

                    # so sánh lần 1
                    self.assertEqual(product_price, actual_price_1)

                    # click cart icon
                    self._find(driver, "xpath=//div[@id='shopping_cart_container']/a").click()

                    # wait for cart page
                    wait.until(
                        EC.visibility_of_element_located(
                            (By.ID, "cart_contents_container")
                        )
                    )

                    # click continue shopping
                    self._find(driver, "id=continue-shopping").click()

                    # back to inventory, check again
                    price_elem_2 = wait.until(
                        EC.visibility_of_element_located((By.XPATH, price_xpath_first))
                    )
                    actual_price_2 = price_elem_2.text.strip()

                    self.assertEqual(product_price, actual_price_2)

                    print(f"Dataset {i}: PASSED")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main(verbosity=2)
