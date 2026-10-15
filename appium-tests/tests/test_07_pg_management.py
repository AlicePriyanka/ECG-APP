import pytest
from pages.doctor_dashboard_page import DoctorDashboardPage
from pages.pg_management_page import PGManagementPage


class TestPGManagementE2E:
    """E2E Tests for Postgraduate Assistant Creation, Password Rules, and Duty Toggles."""

    @pytest.mark.pg
    @pytest.mark.p1
    def test_tc246_create_pg_password_complexity_rules(self, logged_in_doctor):
        """TC246: Enforcing PG password rules (min 8 chars, uppercase, lowercase, numbers)."""
        dashboard = logged_in_doctor
        dashboard.open_create_pg_dialog()
        pg_page = PGManagementPage(dashboard.driver)

        # Test short password
        pg_page.create_pg("Dr Resident", "resident@test.com", "abc")
        assert pg_page.is_visible(pg_page.PASS_LENGTH_ERR)

        # Test missing uppercase
        pg_page.create_pg("Dr Resident", "resident@test.com", "password123")
        assert pg_page.is_visible(pg_page.PASS_UPPER_ERR)

        # Test missing numbers
        pg_page.create_pg("Dr Resident", "resident@test.com", "PasswordABC")
        assert pg_page.is_visible(pg_page.PASS_NUM_ERR)

    @pytest.mark.pg
    @pytest.mark.p1
    def test_tc247_create_pg_name_character_restriction(self, logged_in_doctor):
        """TC247: Name field rejects special characters like @, #, numbers."""
        dashboard = logged_in_doctor
        dashboard.open_create_pg_dialog()
        pg_page = PGManagementPage(dashboard.driver)
        pg_page.create_pg("Dr Resident #123", "resident@test.com", "ValidPass@123")
        assert pg_page.is_visible(pg_page.NAME_CHAR_ERR)
