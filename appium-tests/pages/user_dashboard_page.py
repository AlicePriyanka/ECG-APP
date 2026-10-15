from typing import Dict, List
from appium.webdriver.webdriver import WebDriver
from pages.base_page import BasePage


class UserDashboardPage(BasePage):
    """Page Object for Peripheral Doctor / Clinic User Dashboard."""

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        # Headers & Navigation
        self.DASHBOARD_TITLE = self.by_text_exact("Simats Cardio")
        self.LOGOUT_BUTTON = self.by_accessibility_id("logout_button") or self.by_text_contains("Logout")
        
        # Action Buttons
        self.UPLOAD_ECG_BUTTON = self.by_text_exact("Upload ECG")
        self.DISABLED_UPLOAD_BUTTON = self.by_text_contains("Mon–Fri, 8–3 PM IST")
        
        # Statistics
        self.TOTAL_ECG_CARD = self.by_text_contains("Total ECG")
        self.PENDING_ECG_CARD = self.by_text_contains("Pending ECG")
        self.COMPLETED_ECG_CARD = self.by_text_contains("Completed ECG")
        
        # Patient Records List
        self.PATIENT_RECORDS_HEADER = self.by_text_contains("Patient Records")
        self.EMPTY_STATE_TEXT = self.by_text_contains("No patient records uploaded yet")
        self.PATIENT_CARD = self.by_accessibility_id("patient_card")
        self.REFRESH_INDICATOR = self.by_accessibility_id("refresh_indicator")

    def is_dashboard_displayed(self) -> bool:
        """Check if user dashboard is visible."""
        return self.is_visible(self.PATIENT_RECORDS_HEADER, timeout=10)

    def is_upload_enabled(self) -> bool:
        """Check if upload button is currently enabled (within 8 AM - 3 PM IST)."""
        return self.is_visible(self.UPLOAD_ECG_BUTTON, timeout=3)

    def is_upload_disabled_by_time_window(self) -> bool:
        """Check if upload button is locked with hours message."""
        return self.is_visible(self.DISABLED_UPLOAD_BUTTON, timeout=3)

    def click_upload_ecg(self):
        """Click the Upload ECG button."""
        if self.is_upload_enabled():
            self.click(self.UPLOAD_ECG_BUTTON)
        else:
            self.click(self.DISABLED_UPLOAD_BUTTON)

    def get_statistics(self) -> Dict[str, str]:
        """Read values from Total, Pending, and Completed cards."""
        stats = {}
        for key, locator in [
            ("total", self.TOTAL_ECG_CARD),
            ("pending", self.PENDING_ECG_CARD),
            ("completed", self.COMPLETED_ECG_CARD)
        ]:
            if self.is_visible(locator):
                stats[key] = self.get_text(locator)
        return stats

    def click_first_patient_card(self):
        """Click the top patient card to view patient history."""
        cards = self.find_all(self.PATIENT_CARD)
        if cards:
            cards[0].click()
        else:
            # Fallback by finding first card in list
            self.click(self.by_text_contains("ID: PAT"))

    def click_logout(self):
        """Click user logout button in AppBar."""
        self.click(self.LOGOUT_BUTTON)
