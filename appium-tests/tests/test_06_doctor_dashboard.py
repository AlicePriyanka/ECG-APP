import pytest
from pages.doctor_dashboard_page import DoctorDashboardPage


class TestDoctorDashboardE2E:
    """E2E Tests for Doctor Assigned Review Queue and Duty Controls."""

    @pytest.mark.doctor
    @pytest.mark.p1
    def test_tc216_doctor_review_queue_metrics(self, logged_in_doctor):
        """TC216: Verify Total Review, Pending Review, and Completed Review counts render on Doctor Dashboard."""
        dashboard = logged_in_doctor
        counts = dashboard.get_review_counts()
        assert "total" in counts, "Total Review card missing"
        assert "pending" in counts, "Pending Review card missing"
        assert "completed" in counts, "Completed Review card missing"

    @pytest.mark.doctor
    @pytest.mark.p1
    def test_tc217_doctor_can_open_assigned_patient(self, logged_in_doctor):
        """TC217: Clicking on an assigned patient navigates to ECG Detail review screen."""
        dashboard = logged_in_doctor
        dashboard.click_first_assigned_patient()
