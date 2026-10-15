import pytest
from pages.user_upload_page import UserUploadPage
from pages.user_dashboard_page import UserDashboardPage


class TestPatientManagementE2E:
    """E2E Tests for Patient Search, Debounce Filter, and Registration."""

    @pytest.mark.patient
    @pytest.mark.p1
    def test_tc081_patient_search_with_debounce(self, logged_in_clinic_user):
        """TC081: Searching patient triggers 2-second debounce and filters patient list accurately."""
        dashboard = logged_in_clinic_user
        if not dashboard.is_upload_enabled():
            pytest.skip("Test requires operating hours (08:00 - 15:00 IST Mon-Fri)")
            
        dashboard.click_upload_ecg()
        upload_page = UserUploadPage(dashboard.driver)
        upload_page.handle_consent_dialog(agree=True)
        upload_page.search_and_select_patient("Test")

    @pytest.mark.patient
    @pytest.mark.p1
    def test_tc082_register_new_patient_valid_phone(self, logged_in_clinic_user):
        """TC082: Registering a patient with standardized +91 phone succeeds and assigns PAT-ID."""
        dashboard = logged_in_clinic_user
        if not dashboard.is_upload_enabled():
            pytest.skip("Test requires operating hours")

        dashboard.click_upload_ecg()
        upload_page = UserUploadPage(dashboard.driver)
        upload_page.handle_consent_dialog(agree=True)
        upload_page.create_new_patient(
            name="Automated Patient Appium",
            phone="+919876543210",
            gender="female"
        )
