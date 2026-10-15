import time
import os
from typing import List, Optional, Tuple
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.config import AppiumConfig


class BasePage:
    """Base Page Object containing reusable interaction and verification methods."""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver,
            timeout=AppiumConfig.EXPLICIT_WAIT,
            poll_frequency=AppiumConfig.POLL_FREQUENCY
        )

    def find(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> WebElement:
        """Find a single web element with explicit wait."""
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def find_clickable(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> WebElement:
        """Find a clickable element with explicit wait."""
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable(locator))

    def find_all(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> List[WebElement]:
        """Find multiple elements matching a locator."""
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        try:
            return wait.until(EC.presence_of_all_elements_located(locator))
        except TimeoutException:
            return []

    def click(self, locator: Tuple[str, str], timeout: Optional[int] = None):
        """Click an element safely after ensuring it is clickable."""
        element = self.find_clickable(locator, timeout)
        element.click()

    def type_text(self, locator: Tuple[str, str], text: str, clear_first: bool = True):
        """Send keys to an input element."""
        element = self.find(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator: Tuple[str, str]) -> str:
        """Retrieve visible text or content-desc from an element."""
        element = self.find(locator)
        text = element.text
        if not text:
            text = element.get_attribute("content-desc") or element.get_attribute("text") or ""
        return text

    def is_visible(self, locator: Tuple[str, str], timeout: int = 5) -> bool:
        """Check if an element is visible within a timeout."""
        try:
            element = self.find(locator, timeout=timeout)
            return element.is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    def is_enabled(self, locator: Tuple[str, str]) -> bool:
        """Check if an element is enabled."""
        try:
            return self.find(locator).is_enabled()
        except (TimeoutException, NoSuchElementException):
            return False

    def wait_for_invisibility(self, locator: Tuple[str, str], timeout: int = 15) -> bool:
        """Wait for an element (e.g. loader/spinner) to disappear."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(locator)
            )
        except TimeoutException:
            return False

    def scroll_to_text(self, text: str) -> Optional[WebElement]:
        """Scroll down until an element with the given text is visible on Android."""
        if AppiumConfig.PLATFORM == "Android":
            ui_selector = (
                f'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
                f'.scrollIntoView(new UiSelector().textContains("{text}").instance(0));'
            )
            try:
                return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_selector)
            except NoSuchElementException:
                return None
        else:
            # iOS predicate scroll fallback
            try:
                self.driver.execute_script("mobile: scroll", {"direction": "down"})
                return self.driver.find_element(AppiumBy.IOS_PREDICATE, f'label CONTAINS "{text}"')
            except NoSuchElementException:
                return None

    def take_screenshot(self, name: str) -> str:
        """Capture screenshot and save to screenshots folder."""
        screenshots_dir = os.path.join(os.path.dirname(__file__), "..", "reports", "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, filename)
        self.driver.save_screenshot(filepath)
        return filepath

    # Flutter-friendly element locators
    def by_accessibility_id(self, acc_id: str) -> Tuple[str, str]:
        return (AppiumBy.ACCESSIBILITY_ID, acc_id)

    def by_text_exact(self, text: str) -> Tuple[str, str]:
        if AppiumConfig.PLATFORM == "Android":
            return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')
        return (AppiumBy.IOS_PREDICATE, f'label == "{text}"')

    def by_text_contains(self, text: str) -> Tuple[str, str]:
        if AppiumConfig.PLATFORM == "Android":
            return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text}")')
        return (AppiumBy.IOS_PREDICATE, f'label CONTAINS "{text}"')
