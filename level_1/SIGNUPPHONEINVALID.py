# -*- coding: utf-8 -*-
import csv
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

class SignupPhoneInvalid(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)

    def _find(self, driver, locator):
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

    def test_signup_phone_invalid(self):
        driver = self.driver

        with open("level_1/data/signup-phone-invalid.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader, start=1):
                firstname_input = row["FName"].strip()
                lastname_input = row["LName"].strip()
                email_input = row["Email"].strip()
                phone_input = row["Phone"].strip()
                password_input = row["Password"].strip()
                expected_result = row["ExpectedRes"].strip()
                
                with self.subTest(dataset=i, firstname=firstname_input, lastname=lastname_input):

                    # open register page
                    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/register")

                    # first name input
                    firstname_elem = self._find(driver, "id=input-firstname")
                    firstname_elem.clear()
                    firstname_elem.send_keys(firstname_input)
                    
                    # last name input
                    lastname_elem = self._find(driver, "id=input-lastname")
                    lastname_elem.clear()
                    lastname_elem.send_keys(lastname_input)
                    
                    # email input
                    email_elem = self._find(driver, "id=input-email")
                    email_elem.clear()
                    email_elem.send_keys(email_input)
                    
                    # phone input
                    phone_elem = self._find(driver, "id=input-telephone")
                    phone_elem.clear()
                    phone_elem.send_keys(phone_input)
                    
                    # password input
                    password_elem = self._find(driver, "id=input-password")
                    password_elem.clear()
                    password_elem.send_keys(password_input)
                    
                    # confirm password input
                    confirm_elem = self._find(driver, "id=input-confirm")
                    confirm_elem.clear()
                    confirm_elem.send_keys(password_input)

                    # agree to privacy policy
                    self._find(driver, "xpath=//div[@id='content']/form/div/div/div/label").click()

                    # click Continue
                    self._find(driver, "xpath=//input[@value='Continue']").click()

                    # === verifyText ${targetResult} ${expectedResult} ===
                    result_elem = self._find(driver, "xpath=//fieldset[@id='account']/div[5]/div/div")
                    self.assertEqual(expected_result, result_elem.text.strip())
                    
                    print(f"Dataset {i}: PASSED")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main(verbosity=2)
