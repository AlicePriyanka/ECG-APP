from typing import Optional
from appium.webdriver.webdriver import WebDriver
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object for Login Screen (Simats Cardio)."""

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        # Locators
        self.APP_TITLE = self.by_text_contains("Simats Cardio")
        self.EMAIL_INPUT = self.by_accessibility_id("email_input") or self.by_text_contains("Email")
        self.PASSWORD_INPUT = self.by_accessibility_id("password_input") or self.by_text_contains("Password")
        self.LOGIN_BUTTON = self.by_text_exact("Sign In")
        self.TOGGLE_PASSWORD_VISIBILITY = self.by_accessibility_id("toggle_password")
        self.LOADING_INDICATOR = self.by_accessibility_id("loading_indicator")
        
        # Error & Message Locators
        self.SNACKBAR = self.by_accessibility_id("snackbar")
        self.BLOCKED_ALERT = self.by_text_contains("Your account has been blocked")
        self.PENDING_ALERT = self.by_text_contains("Your account is pending approval")
        self.INVALID_CREDENTIALS_ALERT = self.by_text_contains("Invalid credentials")
        self.ACCOUNT_NOT_FOUND_ALERT = self.by_text_contains("Account does not exist")
        self.EMPTY_FIELDS_ALERT = self.by_text_contains("Please enter both email and password")

    def wait_for_splash_screen(self, timeout: int = 10):
        """Wait for splash screen loading indicator to complete."""
        self.wait_for_invisibility(self.LOADING_INDICATOR, timeout=timeout)

    def enter_email(self, email: str):
        """Input email or username into identifier field."""
        self.type_text(self.by_text_contains("Email"), email)

    def enter_password(self, password: str):
        """Input password."""
        self.type_text(self.by_text_contains("Password"), password)

    def click_sign_in(self):
        """Click the Sign In button."""
        self.click(self.LOGIN_BUTTON)

    def login(self, email: str, password: str):
        """Perform full login action."""
        self.enter_email(email)
        self.enter_password(password)
        self.click_sign_in()

    def is_login_screen_displayed(self) -> bool:
        """Verify login screen title and submit button are present."""
        return self.is_visible(self.LOGIN_BUTTON, timeout=8)

    def get_error_message(self) -> Optional[str]:
        """Fetch error message from snackbar or alert banner."""
        for locator in [
            self.BLOCKED_ALERT,
            self.PENDING_ALERT,
            self.INVALID_CREDENTIALS_ALERT,
            self.ACCOUNT_NOT_FOUND_ALERT,
            self.EMPTY_FIELDS_ALERT
        ]:
            if self.is_visible(locator, timeout=4):
                return self.get_text(locator)
        return None
