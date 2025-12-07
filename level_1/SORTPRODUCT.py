# -*- coding: utf-8 -*-
import csv
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class SortProduct(unittest.TestCase):

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

    # ---------- helper: login once ----------

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

        # đợi vào được trang inventory
        wait.until(EC.visibility_of_element_located((By.ID, "inventory_container")))

    # ---------- test ----------

    def test_sort_product(self):
        driver = self.driver
        wait = self.wait
        
        # login 1 lần, sau đó chỉ thao tác sort + verify
        self._login_saucedemo()

        with open("level_1/data/sort-product.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader, start=1):
                sort_type = row["SortType"].strip()       # az / za / lohi / hilo
                index = int(row["Index"])
                product_name = row["ProductName"].strip()
                product_price = row["ProductPrice"].strip()

                with self.subTest(dataset=i, sort=sort_type, index=index):
                    # chọn kiểu sort
                    select_elem = self._find(
                        driver,
                        "css=select[data-test='product-sort-container']"
                    )
                    Select(select_elem).select_by_value(sort_type)

                    name_xpath = (
                        f"//div[@id='inventory_container']/div/div/div/div[{index}]"
                        "/div[2]/div[1]/a/div"
                    )
                    price_xpath = (
                        f"//div[@id='inventory_container']/div/div/div/div[{index}]"
                        "/div[2]/div[2]/div"
                    )

                    name_elem = wait.until(
                        EC.visibility_of_element_located((By.XPATH, name_xpath))
                    )
                    price_elem = wait.until(
                        EC.visibility_of_element_located((By.XPATH, price_xpath))
                    )

                    actual_name = name_elem.text.strip()
                    actual_price = price_elem.text.strip()

                    self.assertEqual(product_name, actual_name)
                    self.assertEqual(product_price, actual_price)
                    
                    print(f"Dataset {i}: PASSED")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main(verbosity=2)
