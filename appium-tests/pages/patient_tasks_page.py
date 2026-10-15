from appium.webdriver.webdriver import WebDriver
from pages.base_page import BasePage


class PatientTasksPage(BasePage):
    """Page Object for Patient ECG Records Timeline."""

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.SCREEN_TITLE = self.by_accessibility_id("patient_tasks_title")
        self.TASK_HISTORY_CARD = self.by_accessibility_id("patient_task_card")
        self.IMAGE_COUNT_BADGE = self.by_accessibility_id("image_count_badge")
        self.BACK_BUTTON = self.by_accessibility_id("back_button") or self.by_text_exact("Back")

    def is_screen_displayed(self) -> bool:
        return self.is_visible(self.SCREEN_TITLE, timeout=6)

    def click_task_by_index(self, index: int = 0):
        cards = self.find_all(self.TASK_HISTORY_CARD)
        if cards and len(cards) > index:
            cards[index].click()
        else:
            self.click(self.by_text_contains("TASK"))
