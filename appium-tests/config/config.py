import os
from typing import Dict, Any

class AppiumConfig:
    """Configuration class for Appium Test Suite."""
    
    # Appium Server URL
    APPIUM_SERVER_URL = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
    
    # Platform Selection: 'Android' or 'iOS'
    PLATFORM = os.getenv("TEST_PLATFORM", "Android").capitalize()
    
    # Application Paths
    ANDROID_APP_PATH = os.getenv(
        "ANDROID_APP_PATH",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ECG-APP-main", "build", "app", "outputs", "flutter-apk", "app-debug.apk"))
    )
    
    IOS_APP_PATH = os.getenv(
        "IOS_APP_PATH",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ECG-APP-main", "build", "ios", "iphoneos", "Runner.app"))
    )

    # Timeouts
    IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "10"))
    EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "20"))
    POLL_FREQUENCY = 0.5

    # Test Users
    TEST_USERS = {
        "admin": {
            "email": "admin@example.com",
            "password": "Password@123",
            "role": "admin",
            "name": "Admin User"
        },
        "doctor": {
            "email": "draravindcardiology@gmail.com",
            "password": "Password@123",
            "role": "doctor",
            "name": "Aravind Ganesh"
        },
        "pg": {
            "email": "testpg@doctor.com",
            "password": "Password@123",
            "role": "pg",
            "name": "Test PG"
        },
        "clinic_user": {
            "email": "clinic@doctor.com",
            "password": "Password@123",
            "role": "user",
            "name": "clinic test doctor"
        },
        "blocked_user": {
            "email": "blocked@example.com",
            "password": "Password@123",
            "role": "user",
            "name": "Blocked Doctor"
        },
        "pending_user": {
            "email": "pending@example.com",
            "password": "Password@123",
            "role": "user",
            "name": "Pending Approval Doctor"
        }
    }

    # Backend API URL for Test Harness / Preconditions
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8081/saveetha_cardio/api/")

    @classmethod
    def get_android_capabilities(cls) -> Dict[str, Any]:
        """Desired Capabilities for Android (UIAutomator2 / Flutter driver)."""
        caps = {
            "platformName": "Android",
            "automationName": "UiAutomator2",
            "deviceName": os.getenv("ANDROID_DEVICE_NAME", "Android Emulator"),
            "app": cls.ANDROID_APP_PATH if os.path.exists(cls.ANDROID_APP_PATH) else None,
            "appPackage": "com.simats.simatscardio",
            "appActivity": ".MainActivity",
            "noReset": False,
            "fullReset": False,
            "autoGrantPermissions": True,
            "newCommandTimeout": 300,
            "unicodeKeyboard": True,
            "resetKeyboard": True,
        }
        return {k: v for k, v in caps.items() if v is not None}

    @classmethod
    def get_ios_capabilities(cls) -> Dict[str, Any]:
        """Desired Capabilities for iOS (XCUITest)."""
        caps = {
            "platformName": "iOS",
            "automationName": "XCUITest",
            "deviceName": os.getenv("IOS_DEVICE_NAME", "iPhone 15 Pro"),
            "platformVersion": os.getenv("IOS_PLATFORM_VERSION", "17.0"),
            "app": cls.IOS_APP_PATH if os.path.exists(cls.IOS_APP_PATH) else None,
            "bundleId": "com.simats.simatscardio",
            "noReset": False,
            "fullReset": False,
            "autoAcceptAlerts": True,
            "newCommandTimeout": 300,
        }
        return {k: v for k, v in caps.items() if v is not None}

    @classmethod
    def get_capabilities(cls) -> Dict[str, Any]:
        if cls.PLATFORM == "Ios":
            return cls.get_ios_capabilities()
        return cls.get_android_capabilities()
