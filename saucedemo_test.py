from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import unittest
import time

class SauceDemoTest(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.driver.get("https://www.saucedemo.com")
        self.wait = WebDriverWait(self.driver, 10)

    def wait_and_click(self, by, value):
        element = self.wait.until(EC.element_to_be_clickable((by, value)))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
        element.click()

    def wait_and_send_keys(self, by, value, text):
        element = self.wait.until(EC.presence_of_element_located((by, value)))
        element.clear()
        element.send_keys(text)

    def get_text(self, by, value):
        element = self.wait.until(EC.presence_of_element_located((by, value)))
        return element.text

    def test_saucedemo_workflow(self):
        try:
            # Task 1: Login
            print("Logging in...")
            self.wait_and_send_keys(By.ID, "user-name", "standard_user")
            self.wait_and_send_keys(By.ID, "password", "secret_sauce")
            self.wait_and_click(By.ID, "login-button")
            
            # Verify login success
            self.wait.until(EC.url_contains("/inventory.html"))
            print("Login successful")

            # Task 2: Add Items from Inventory
            print("Adding items to cart...")
            # Sort items
            sort_dropdown = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "product_sort_container"))
            )
            Select(sort_dropdown).select_by_visible_text("Price (low to high)")
            time.sleep(1)

            # Add first two items
            items = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "inventory_item"))
            )
            
            # Add Bike Light and Backpack
            for item in items:
                item_name = item.find_element(By.CLASS_NAME, "inventory_item_name").text
                if item_name in ["Sauce Labs Bike Light", "Sauce Labs Backpack"]:
                    add_button = item.find_element(By.CSS_SELECTOR, "button[data-test^='add-to-cart']")
                    add_button.click()
                    time.sleep(0.5)

            cart_count = self.get_text(By.CLASS_NAME, "shopping_cart_badge")
            self.assertEqual(cart_count, "2")
            print("Added first 2 items successfully")

            # Task 3: Add Onesie
            print("Adding Onesie...")
            items = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "inventory_item"))
            )
            for item in items:
                item_name = item.find_element(By.CLASS_NAME, "inventory_item_name").text
                if "Onesie" in item_name:
                    add_button = item.find_element(By.CSS_SELECTOR, "button[data-test^='add-to-cart']")
                    add_button.click()
                    break

            cart_count = self.get_text(By.CLASS_NAME, "shopping_cart_badge")
            self.assertEqual(cart_count, "3")
            print("Added Onesie successfully")

            # Task 4: Remove Item from Cart
            print("Managing cart...")
            self.wait_and_click(By.CLASS_NAME, "shopping_cart_link")
            time.sleep(1)

            items = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "cart_item"))
            )
            for item in items:
                price_text = item.find_element(By.CLASS_NAME, "inventory_item_price").text
                price = float(price_text.replace("$", ""))
                if 8 <= price <= 10:
                    remove_button = item.find_element(By.CSS_SELECTOR, "button[data-test^='remove']")
                    remove_button.click()
                    break

            time.sleep(1)
            cart_count = self.get_text(By.CLASS_NAME, "shopping_cart_badge")
            self.assertEqual(cart_count, "2")
            print("Item removed successfully")

            # Task 5: Checkout
            print("Starting checkout...")
            self.wait_and_click(By.ID, "checkout")
            
            self.wait_and_send_keys(By.ID, "first-name", "John")
            self.wait_and_send_keys(By.ID, "last-name", "Doe")
            self.wait_and_send_keys(By.ID, "postal-code", "12345")
            self.wait_and_click(By.ID, "continue")

            total = self.get_text(By.CLASS_NAME, "summary_total_label")
            print(f"Total amount: {total}")

            self.wait_and_click(By.ID, "finish")
            
            success_msg = self.get_text(By.CLASS_NAME, "complete-header")
            self.assertEqual(success_msg, "Thank you for your order!")
            print("Checkout completed successfully")

            # Task 6: Logout with improved handling
            print("Logging out...")
            # Click burger menu and wait for animation
            self.wait_and_click(By.ID, "react-burger-menu-btn")
            time.sleep(2)  # Increased wait time for menu animation
            
            # Wait for logout link to be visible and clickable
            logout_link = self.wait.until(
                EC.element_to_be_clickable((By.ID, "logout_sidebar_link"))
            )
            time.sleep(1)  # Additional wait for stability
            logout_link.click()
            
            # Wait for login page elements instead of URL
            self.wait.until(
                EC.presence_of_element_located((By.ID, "user-name"))
            )
            self.wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            print("Logged out successfully")
            print("All tests completed successfully!")

        except Exception as e:
            print(f"Test failed with error: {str(e)}")
            self.driver.save_screenshot("error_screenshot.png")
            raise

    def tearDown(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    unittest.main()