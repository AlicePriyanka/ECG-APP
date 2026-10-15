from typing import Dict, List
from appium.webdriver.webdriver import WebDriver
from pages.base_page import BasePage


class DoctorDashboardPage(BasePage):
    """Page Object for Cardiologist & PG Dashboard."""

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        # Stats Locators
        self.TOTAL_REVIEW_CARD = self.by_text_contains("Total Review")
        self.PENDING_REVIEW_CARD = self.by_text_contains("Pending Review")
        self.COMPLETED_REVIEW_CARD = self.by_text_contains("Completed Review")

        # PG Management Section (Only visible for Doctor role)
        self.PG_MANAGEMENT_HEADER = self.by_text_exact("PG Management")
        self.CREATE_PG_BUTTON = self.by_accessibility_id("create_pg_button") or self.by_text_contains("Add PG")
        self.PG_SEARCH_INPUT = self.by_text_contains("Search PG")

        # Assigned Tasks
        self.ASSIGNED_PATIENTS_HEADER = self.by_text_contains("Assigned Patients")
        self.EMPTY_QUEUE_TEXT = self.by_text_contains("No patients assigned yet")
        self.PATIENT_CARD = self.by_accessibility_id("assigned_patient_card")
        self.PENDING_CHIP = self.by_text_contains("Pending")
        self.REVIEWED_CHIP = self.by_text_contains("Reviewed")

    def is_dashboard_displayed(self) -> bool:
        """Check if doctor dashboard is loaded."""
        return self.is_visible(self.ASSIGNED_PATIENTS_HEADER, timeout=10)

    def is_pg_management_visible(self) -> bool:
        """Verify PG management section is displayed (true for Doctor, false for PG)."""
        return self.is_visible(self.PG_MANAGEMENT_HEADER, timeout=3)

    def get_review_counts(self) -> Dict[str, str]:
        """Fetch total, pending, and completed review numbers."""
        counts = {}
        for key, locator in [
            ("total", self.TOTAL_REVIEW_CARD),
            ("pending", self.PENDING_REVIEW_CARD),
            ("completed", self.COMPLETED_REVIEW_CARD)
        ]:
            if self.is_visible(locator):
                counts[key] = self.get_text(locator)
        return counts

    def open_create_pg_dialog(self):
        """Click the Add PG button."""
        self.click(self.CREATE_PG_BUTTON)

    def click_first_assigned_patient(self):
        """Open the top assigned patient to review their ECG."""
        self.click(self.by_text_contains("ID: PAT"), timeout=8)
