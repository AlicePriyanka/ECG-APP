from typing import Optional
from appium.webdriver.webdriver import WebDriver
from pages.base_page import BasePage


class TaskDetailPage(BasePage):
    """Page Object for ECG Image Review, Pinch-Zoom, and Medical Opinion Screen."""

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        # Header Locators
        self.PATIENT_NAME_HEADER = self.by_accessibility_id("patient_name_header")
        self.PATIENT_ID_HEADER = self.by_accessibility_id("patient_id_header")
        
        # Image Viewer Locators
        self.ECG_IMAGE_THUMBNAIL = self.by_accessibility_id("ecg_image_thumbnail")
        self.FULLSCREEN_IMAGE_VIEWER = self.by_accessibility_id("fullscreen_image_viewer")
        self.CLOSE_FULLSCREEN_BUTTON = self.by_accessibility_id("close_fullscreen")

        # Feedback & Medical Opinion Locators
        self.IMAGE_FEEDBACK_INPUT = self.by_text_contains("Enter your opinion")
        self.APPLY_TO_ALL_CHECKBOX = self.by_text_contains("Apply to all images")
        self.SAVE_OPINION_BUTTON = self.by_text_contains("Submit Opinion") or self.by_text_contains("Save Opinion")
        self.STATUS_CHIP = self.by_accessibility_id("task_status_chip")

        # Success Banner
        self.OPINION_SUCCESS_SNACKBAR = self.by_text_contains("Opinion updated successfully")

    def click_first_image_thumbnail(self):
        """Open first ECG image in high-resolution interactive viewer."""
        thumbnails = self.find_all(self.ECG_IMAGE_THUMBNAIL)
        if thumbnails:
            thumbnails[0].click()
        else:
            self.click(self.by_text_contains("TASK"))

    def is_fullscreen_viewer_open(self) -> bool:
        """Verify full-screen interactive viewer is rendered."""
        return self.is_visible(self.FULLSCREEN_IMAGE_VIEWER, timeout=5)

    def close_fullscreen_viewer(self):
        """Dismiss full-screen image viewer."""
        self.click(self.CLOSE_FULLSCREEN_BUTTON)

    def enter_opinion(self, feedback: str, apply_to_all: bool = False):
        """Type clinical opinion and optionally check apply to all."""
        self.type_text(self.IMAGE_FEEDBACK_INPUT, feedback)
        if apply_to_all:
            self.click(self.APPLY_TO_ALL_CHECKBOX)
        self.click(self.SAVE_OPINION_BUTTON)

    def is_opinion_saved(self) -> bool:
        """Check for success message."""
        return self.is_visible(self.OPINION_SUCCESS_SNACKBAR, timeout=8)
