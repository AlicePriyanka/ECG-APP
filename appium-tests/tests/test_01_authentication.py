import pytest
from pages.login_page import LoginPage
from pages.user_dashboard_page import UserDashboardPage
from pages.doctor_dashboard_page import DoctorDashboardPage
from config.config import AppiumConfig


class TestAuthenticationE2E:
    """End-to-End Functional Tests for User Authentication and Role Redirection."""

    @pytest.mark.auth
    @pytest.mark.p1
    def test_tc001_clinic_user_valid_login(self, driver):
        """TC001: Clinic User successfully logs in with valid credentials and lands on User Dashboard."""
        login_page = LoginPage(driver)
        cred = AppiumConfig.TEST_USERS["clinic_user"]
        login_page.login(cred["email"], cred["password"])
        dashboard = UserDashboardPage(driver)
        assert dashboard.is_dashboard_displayed(), "User Dashboard did not render after valid clinic login"

    @pytest.mark.auth
    @pytest.mark.p1
    def test_tc002_doctor_valid_login(self, driver):
        """TC002: Duty Doctor successfully logs in and lands on Doctor Dashboard."""
        login_page = LoginPage(driver)
        cred = AppiumConfig.TEST_USERS["doctor"]
        login_page.login(cred["email"], cred["password"])
        dashboard = DoctorDashboardPage(driver)
        assert dashboard.is_dashboard_displayed(), "Doctor Dashboard did not render after valid doctor login"
        assert dashboard.is_pg_management_visible(), "PG Management should be visible for Doctor role"

    @pytest.mark.auth
    @pytest.mark.p1
    def test_tc003_pg_valid_login(self, driver):
        """TC003: PG logs in and sees Doctor Dashboard without PG Management controls."""
        login_page = LoginPage(driver)
        cred = AppiumConfig.TEST_USERS["pg"]
        login_page.login(cred["email"], cred["password"])
        dashboard = DoctorDashboardPage(driver)
        assert dashboard.is_dashboard_displayed(), "Dashboard did not render for PG login"
        assert not dashboard.is_pg_management_visible(), "PG Management controls must be hidden for PG role"

    @pytest.mark.auth
    @pytest.mark.p2
    def test_tc004_invalid_password_error(self, driver):
        """TC004: Entering an incorrect password shows Invalid Credentials error."""
        login_page = LoginPage(driver)
        cred = AppiumConfig.TEST_USERS["doctor"]
        login_page.login(cred["email"], "WrongPassword123")
        err = login_page.get_error_message()
        assert err and "Invalid credentials" in err, f"Expected Invalid credentials alert, got: {err}"

    @pytest.mark.auth
    @pytest.mark.p2
    def test_tc005_non_existent_account_error(self, driver):
        """TC005: Entering an unregistered email triggers Account does not exist prompt."""
        login_page = LoginPage(driver)
        login_page.login("nonexistent_doctor_999@test.com", "Password@123")
        err = login_page.get_error_message()
        assert err and "Account does not exist" in err, f"Expected Account does not exist, got: {err}"

    @pytest.mark.auth
    @pytest.mark.p1
    def test_tc006_blocked_account_prevention(self, driver):
        """TC006: User with blocked status (blocked=1) is rejected with account blocked message."""
        login_page = LoginPage(driver)
        cred = AppiumConfig.TEST_USERS["blocked_user"]
        login_page.login(cred["email"], cred["password"])
        err = login_page.get_error_message()
        assert err and "blocked by the admin" in err, f"Expected account blocked alert, got: {err}"

    @pytest.mark.auth
    @pytest.mark.p1
    def test_tc007_pending_approval_account_prevention(self, driver):
        """TC007: User with inactive status (active=0) is rejected with pending approval message."""
        login_page = LoginPage(driver)
        cred = AppiumConfig.TEST_USERS["pending_user"]
        login_page.login(cred["email"], cred["password"])
        err = login_page.get_error_message()
        assert err and "pending approval by the admin" in err, f"Expected pending approval alert, got: {err}"

    @pytest.mark.auth
    @pytest.mark.p2
    def test_tc008_logout_clears_session(self, driver):
        """TC008: Logging out clears SharedPreferences and redirects back to Login Screen."""
        login_page = LoginPage(driver)
        cred = AppiumConfig.TEST_USERS["clinic_user"]
        login_page.login(cred["email"], cred["password"])
        dashboard = UserDashboardPage(driver)
        assert dashboard.is_dashboard_displayed()
        dashboard.click_logout()
        assert login_page.is_login_screen_displayed(), "App did not return to login screen after logout"
