import pytest
from pages.login_page import LoginPage


class TestEdgeCasesAndSecurityE2E:
    """E2E Tests for Security Injections, Boundary Conditions, and Network Resilience."""

    @pytest.mark.security
    @pytest.mark.p1
    def test_tc331_sql_injection_prevention(self, driver):
        """TC331: Supplying SQL injection payloads in login fields does not bypass authentication."""
        login_page = LoginPage(driver)
        sql_payload = "' OR '1'='1' --"
        login_page.login(sql_payload, "some_pass")
        assert not login_page.is_visible(login_page.by_text_exact("Simats Cardio"), timeout=3)
        assert login_page.is_login_screen_displayed()

    @pytest.mark.security
    @pytest.mark.p1
    def test_tc332_xss_script_injection_handling(self, driver):
        """TC332: Script injection tags in input fields are sanitized without execution."""
        login_page = LoginPage(driver)
        xss_payload = "<script>alert('xss')</script>"
        login_page.login(xss_payload, "password")
        assert login_page.is_login_screen_displayed()
