import pytest
from pages.user_upload_page import UserUploadPage


class TestECGUploadWorkflowE2E:
    """E2E Tests for Voluntary Consent, Multi-Image Capture, Priority, and Task Creation."""

    @pytest.mark.upload
    @pytest.mark.p1
    def test_tc111_consent_dialog_terms_required(self, logged_in_clinic_user):
        """TC111: Consent modal enforces checking 'I agree to the terms' before capture is allowed."""
        dashboard = logged_in_clinic_user
        if not dashboard.is_upload_enabled():
            pytest.skip("Test requires operating hours")

        dashboard.click_upload_ecg()
        upload_page = UserUploadPage(dashboard.driver)
        assert upload_page.is_visible(upload_page.CONSENT_TITLE), "Consent terms dialog did not appear"
        # Click Cancel and ensure modal closes
        upload_page.handle_consent_dialog(agree=False)
        assert not upload_page.is_visible(upload_page.CONSENT_TITLE, timeout=2)

    @pytest.mark.upload
    @pytest.mark.p1
    def test_tc112_priority_selection_and_notes(self, logged_in_clinic_user):
        """TC112: Setting priority (Urgent) and entering patient clinical symptoms."""
        dashboard = logged_in_clinic_user
        if not dashboard.is_upload_enabled():
            pytest.skip("Test requires operating hours")

        dashboard.click_upload_ecg()
        upload_page = UserUploadPage(dashboard.driver)
        upload_page.handle_consent_dialog(agree=True)
        upload_page.select_priority("Urgent")
        upload_page.enter_notes("Patient presenting with acute sub-sternal chest pressure radiating to left arm")
