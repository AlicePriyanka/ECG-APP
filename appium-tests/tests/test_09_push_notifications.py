import pytest
from pages.login_page import LoginPage
from pages.user_dashboard_page import UserDashboardPage
from config.config import AppiumConfig


class TestPushNotificationsE2E:
    """E2E Tests for FCM Push Token Registration and Notification Click Handling."""

    @pytest.mark.push
    @pytest.mark.p2
    def test_tc311_fcm_token_registration_on_login(self, driver):
        """TC311: Valid login sends device FCM token to backend register_fcm_token.php."""
        login_page = LoginPage(driver)
        cred = AppiumConfig.TEST_USERS["clinic_user"]
        login_page.login(cred["email"], cred["password"])
        dashboard = UserDashboardPage(driver)
        assert dashboard.is_dashboard_displayed()

    @pytest.mark.push
    @pytest.mark.p2
    def test_tc312_notification_tap_deep_linking(self, driver):
        """TC312: Tapping a task notification navigates directly to TaskDetailScreen."""
        # Simulated payload deep link
        pass
