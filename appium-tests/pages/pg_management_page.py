from typing import Optional
from appium.webdriver.webdriver import WebDriver
from pages.base_page import BasePage


class PGManagementPage(BasePage):
    """Page Object for Doctor's Postgraduate (PG) Assistant Management."""

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        # Create PG Dialog
        self.DIALOG_TITLE = self.by_text_exact("Create New PG")
        self.NAME_FIELD = self.by_text_contains("Name *")
        self.EMAIL_FIELD = self.by_text_contains("Email *")
        self.PASSWORD_FIELD = self.by_text_contains("Password *")
        self.SUBMIT_CREATE_PG = self.by_text_exact("Create")
        self.CANCEL_BUTTON = self.by_text_exact("Cancel")

        # Validation Messages
        self.NAME_REQUIRED_ERR = self.by_text_exact("Name is required")
        self.NAME_LENGTH_ERR = self.by_text_exact("Name must be 2-100 characters")
        self.NAME_CHAR_ERR = self.by_text_exact("Name can only contain letters, spaces, and dots")
        self.EMAIL_REQUIRED_ERR = self.by_text_exact("Email is required")
        self.EMAIL_INVALID_ERR = self.by_text_exact("Please enter a valid email address")
        self.PASS_LENGTH_ERR = self.by_text_exact("Password must be at least 8 characters")
        self.PASS_LOWER_ERR = self.by_text_exact("Password must contain lowercase letters")
        self.PASS_UPPER_ERR = self.by_text_exact("Password must contain uppercase letters")
        self.PASS_NUM_ERR = self.by_text_exact("Password must contain numbers")

        # PG Item & Actions Dialog
        self.PG_ITEM = self.by_accessibility_id("pg_list_item")
        self.EDIT_PG_OPTION = self.by_text_exact("Edit")
        self.SET_DUTY_OPTION = self.by_text_exact("Set Duty")
        self.DELETE_PG_OPTION = self.by_text_exact("Delete")
        self.CONFIRM_DELETE_BUTTON = self.by_text_exact("Delete")

    def create_pg(self, name: str, email: str, password: str):
        """Fill and submit new PG creation form."""
        self.type_text(self.NAME_FIELD, name)
        self.type_text(self.EMAIL_FIELD, email)
        self.type_text(self.PASSWORD_FIELD, password)
        self.click(self.SUBMIT_CREATE_PG)

    def set_pg_as_duty(self, pg_name: str):
        """Open PG options and toggle duty status."""
        self.click(self.by_text_contains(pg_name))
        self.click(self.SET_DUTY_OPTION)

    def delete_pg(self, pg_name: str):
        """Delete PG with confirmation."""
        self.click(self.by_text_contains(pg_name))
        self.click(self.DELETE_PG_OPTION)
        self.click(self.CONFIRM_DELETE_BUTTON)
