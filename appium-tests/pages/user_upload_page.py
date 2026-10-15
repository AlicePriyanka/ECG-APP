from typing import Optional
from appium.webdriver.webdriver import WebDriver
from pages.base_page import BasePage


class UserUploadPage(BasePage):
    """Page Object for ECG Upload, Patient Registration, and Consent Screen."""

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        # Consent Modal Locators
        self.CONSENT_TITLE = self.by_text_exact("ECG Submission Terms")
        self.CONSENT_CHECKBOX = self.by_accessibility_id("consent_checkbox")
        self.AGREE_BUTTON = self.by_text_contains("Agree & Capture ECG")
        self.CANCEL_CONSENT_BUTTON = self.by_text_exact("Cancel")

        # Patient Search / Select Locators
        self.PATIENT_SEARCH_INPUT = self.by_text_contains("Search Patient")
        self.PATIENT_OPTION_ITEM = self.by_accessibility_id("patient_search_result")
        
        # Create Patient Modal Locators
        self.CREATE_PATIENT_TRIGGER = self.by_text_contains("Add New Patient")
        self.PATIENT_NAME_INPUT = self.by_text_contains("Patient Name")
        self.PATIENT_PHONE_INPUT = self.by_text_contains("Contact")
        self.GENDER_DROPDOWN = self.by_text_contains("Gender")
        self.SAVE_PATIENT_BUTTON = self.by_text_exact("Save Patient")

        # ECG Form Locators
        self.PRIORITY_DROPDOWN = self.by_text_contains("Priority")
        self.NOTES_INPUT = self.by_text_contains("Clinical Notes / Symptoms")
        self.CAMERA_BUTTON = self.by_text_contains("Capture ECG")
        self.GALLERY_BUTTON = self.by_text_contains("Choose from Gallery")
        self.SELECTED_IMAGE_THUMBNAIL = self.by_accessibility_id("selected_image_thumbnail")
        self.MAX_IMAGES_ERROR = self.by_text_contains("Maximum 5 images allowed per upload")
        self.SUBMIT_TASK_BUTTON = self.by_text_exact("Submit Task")
        self.UPLOADING_PROGRESS = self.by_accessibility_id("upload_progress")

        # Load / Queue Governor Alert
        self.HIGH_LOAD_ALERT = self.by_text_contains("High Patient Load at Present")
        self.EMERGENCY_PHONE_TEXT = self.by_text_contains("(044) 6672 6612")

    def handle_consent_dialog(self, agree: bool = True):
        """Handle mandatory voluntary terms consent dialog."""
        if self.is_visible(self.CONSENT_TITLE, timeout=5):
            if agree:
                # Click checkbox to enable agreement button
                self.click(self.by_text_contains("I agree to the terms"))
                self.click(self.AGREE_BUTTON)
            else:
                self.click(self.CANCEL_CONSENT_BUTTON)

    def search_and_select_patient(self, query: str):
        """Type in search box, wait for 2-sec debounce, and select patient."""
        self.type_text(self.PATIENT_SEARCH_INPUT, query)
        # Select first matching result
        first_result = self.by_text_contains(query)
        self.click(first_result, timeout=6)

    def create_new_patient(self, name: str, phone: str, gender: str = "male"):
        """Create a new patient via inline form."""
        self.click(self.CREATE_PATIENT_TRIGGER)
        self.type_text(self.PATIENT_NAME_INPUT, name)
        self.type_text(self.PATIENT_PHONE_INPUT, phone)
        self.click(self.SAVE_PATIENT_BUTTON)

    def select_priority(self, priority: str):
        """Set task priority (low, normal, high, urgent)."""
        self.click(self.PRIORITY_DROPDOWN)
        self.click(self.by_text_exact(priority.capitalize()))

    def enter_notes(self, notes: str):
        """Enter user/clinical notes."""
        self.type_text(self.NOTES_INPUT, notes)

    def click_camera(self):
        """Trigger native camera capture."""
        self.click(self.CAMERA_BUTTON)

    def click_submit_task(self):
        """Submit the ECG task with all attachments."""
        self.click(self.SUBMIT_TASK_BUTTON)

    def is_high_load_alert_displayed(self) -> bool:
        """Check if high load limiter blocked the upload."""
        return self.is_visible(self.HIGH_LOAD_ALERT, timeout=5)
