import pytest
import os
import sys
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config.config import AppiumConfig
from pages.login_page import LoginPage
from pages.user_dashboard_page import UserDashboardPage
from pages.doctor_dashboard_page import DoctorDashboardPage


@pytest.fixture(scope="function")
def driver(request):
    """Initializes Appium WebDriver session per test."""
    caps = AppiumConfig.get_capabilities()
    
    if AppiumConfig.PLATFORM == "Android":
        options = UiAutomator2Options().load_capabilities(caps)
    else:
        options = XCUITestOptions().load_capabilities(caps)

    driver = webdriver.Remote(
        command_executor=AppiumConfig.APPIUM_SERVER_URL,
        options=options
    )
    driver.implicitly_wait(AppiumConfig.IMPLICIT_WAIT)

    # Attach driver to test node for failure hook
    request.node.driver = driver

    yield driver

    # Teardown: Capture screenshot if failed
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        test_name = request.node.name
        screenshots_dir = os.path.join(os.path.dirname(__file__), "reports", "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshots_dir, f"FAIL_{test_name}.png")
        try:
            driver.save_screenshot(screenshot_path)
            print(f"\n[Screenshot Captured] Saved failure screenshot to: {screenshot_path}")
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")

    try:
        driver.quit()
    except Exception:
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test execution outcome on item for failure hooks."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(scope="function")
def logged_in_clinic_user(driver):
    """Logs in as Peripheral Doctor / Clinic User and navigates to User Dashboard."""
    login_page = LoginPage(driver)
    user_cred = AppiumConfig.TEST_USERS["clinic_user"]
    login_page.login(user_cred["email"], user_cred["password"])
    dashboard = UserDashboardPage(driver)
    assert dashboard.is_dashboard_displayed(), "User Dashboard failed to display after login"
    return dashboard


@pytest.fixture(scope="function")
def logged_in_doctor(driver):
    """Logs in as Cardiologist and navigates to Doctor Dashboard."""
    login_page = LoginPage(driver)
    doc_cred = AppiumConfig.TEST_USERS["doctor"]
    login_page.login(doc_cred["email"], doc_cred["password"])
    dashboard = DoctorDashboardPage(driver)
    assert dashboard.is_dashboard_displayed(), "Doctor Dashboard failed to display after login"
    return dashboard
