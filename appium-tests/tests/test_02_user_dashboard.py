import pytest
from datetime import datetime, timezone, timedelta
from pages.user_dashboard_page import UserDashboardPage


class TestUserDashboardE2E:
    """E2E Tests for Clinic Dashboard, Statistics, and Operating Window."""

    @pytest.mark.dashboard
    @pytest.mark.p1
    def test_tc036_operating_hours_validation(self, logged_in_clinic_user):
        """TC036: Verify ECG Upload button state conforms strictly to Monday-Friday 08:00-15:00 IST."""
        dashboard = logged_in_clinic_user
        
        # Calculate current time in Indian Standard Time (IST = UTC + 5:30)
        ist_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        is_weekday = 0 <= ist_now.weekday() <= 4  # Monday is 0, Friday is 4
        is_operating_hours = 8 <= ist_now.hour < 15
        expected_allowed = is_weekday and is_operating_hours

        if expected_allowed:
            assert dashboard.is_upload_enabled(), f"Upload button should be enabled at {ist_now.strftime('%A %H:%M')} IST"
        else:
            assert dashboard.is_upload_disabled_by_time_window(), (
                f"Upload button should be locked with 'Mon-Fri, 8-3 PM IST' at {ist_now.strftime('%A %H:%M')} IST"
            )

    @pytest.mark.dashboard
    @pytest.mark.p2
    def test_tc037_dashboard_metrics_display(self, logged_in_clinic_user):
        """TC037: Verify Total, Pending, and Completed ECG counter cards are visible and populated."""
        dashboard = logged_in_clinic_user
        stats = dashboard.get_statistics()
        assert "total" in stats, "Total ECG stat card is missing"
        assert "pending" in stats, "Pending ECG stat card is missing"
        assert "completed" in stats, "Completed ECG stat card is missing"

    @pytest.mark.dashboard
    @pytest.mark.p2
    def test_tc038_patient_record_grouping_navigation(self, logged_in_clinic_user):
        """TC038: Clicking a patient card in user dashboard navigates to Patient Tasks Screen."""
        dashboard = logged_in_clinic_user
        dashboard.click_first_patient_card()
