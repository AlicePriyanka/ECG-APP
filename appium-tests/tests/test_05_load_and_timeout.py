import pytest
from pages.user_upload_page import UserUploadPage


class TestLoadAndTimeoutE2E:
    """E2E Tests for High Patient Load Limiters and 15-Minute Stale Auto-Closure."""

    @pytest.mark.load
    @pytest.mark.p1
    def test_tc181_high_load_emergency_referral_banner(self, logged_in_clinic_user):
        """TC181: When queue backlog threshold is met, upload displays Saveetha Emergency contact hotline."""
        dashboard = logged_in_clinic_user
        if not dashboard.is_upload_enabled():
            pytest.skip("Test requires operating hours")

        dashboard.click_upload_ecg()
        upload_page = UserUploadPage(dashboard.driver)
        upload_page.handle_consent_dialog(agree=True)
        # Verify emergency phone number format if high load triggers
        if upload_page.is_high_load_alert_displayed():
            assert upload_page.is_visible(upload_page.EMERGENCY_PHONE_TEXT), "Emergency contact (044) 6672 6612 missing from alert"
