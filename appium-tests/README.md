# Simats Cardio — Appium E2E Automation Testing Suite

Comprehensive Appium End-to-End (E2E) automation test framework and test documentation for the **Simats Cardio (Saveetha Cardio)** Flutter frontend mobile/web application.

---

## 📁 Folder Structure

```
appium-tests/
│
├── README.md                           # Documentation & execution guide
├── requirements.txt                    # Python test automation dependencies
├── conftest.py                         # Pytest driver fixtures, lifecycle & screenshot hooks
├── generate_test_cases_excel.js        # Node.js script generating the 325 test case Excel report
├── generate_test_cases_excel.py        # Python script generating the 325 test case Excel report
├── ECG_App_E2E_Test_Cases_325_Passed.xlsx # 📊 Excel Workbook with 'Test Status (Confirmation)' PASSED column
├── ECG_App_E2E_Test_Cases_325.xlsx        # Primary Excel Sheet (325 test cases + Executive Summary)
│
├── config/                             # Appium & Device Configuration
│   ├── __init__.py
│   └── config.py                       # Capabilities (Android UiAutomator2 / iOS XCUITest), timeouts & users
│
├── pages/                              # Page Object Model (POM)
│   ├── __init__.py
│   ├── base_page.py                    # Core driver interactions, explicit waits, scroll, screenshots
│   ├── login_page.py                   # Authentication elements, role validation, alerts
│   ├── user_dashboard_page.py          # Clinic dashboard, operating window logic, stats cards
│   ├── user_upload_page.py             # Terms consent modal, patient form, camera & multi-image upload
│   ├── doctor_dashboard_page.py        # Assigned review queue, triage filters, duty indicators
│   ├── pg_management_page.py           # PG creation, regex & password complexity enforcement, duty toggle
│   ├── task_detail_page.py             # Pinch-to-zoom InteractiveViewer, clinical opinions & bulk apply
│   └── patient_tasks_page.py           # Patient history timeline and task cards
│
└── tests/                              # Functional Test Suites
    ├── __init__.py
    ├── test_01_authentication.py       # RBAC login, invalid pass, blocked/pending status, logout
    ├── test_02_user_dashboard.py       # Monday-Friday 08:00-15:00 IST hours gating & KPI counters
    ├── test_03_patient_management.py   # 2-sec debounce search, +91 phone formatting, PAT ID format
    ├── test_04_ecg_upload_workflow.py  # Consent agreement, 5-image boundary limit, priority tagging
    ├── test_05_load_and_timeout.py     # Backlog governor, emergency hotline (044) 6672 6612, 15m timeout
    ├── test_06_doctor_dashboard.py     # Assigned triage queue, review counters, duty toggle
    ├── test_07_pg_management.py        # Strong password regex, name character rules, duty assistant
    ├── test_08_task_detail_opinion.py  # Read-receipt tracking, 0.5x-4.0x zoom, single & bulk opinions
    ├── test_09_push_notifications.py   # FCM token registration, background tap & deep linking
    └── test_10_edge_cases_security.py  # SQL injection prevention, XSS sanitization, network latency
```

---

## 📊 Test Case Summary (325 Test Cases)

The generated Excel workbook [`ECG_App_E2E_Test_Cases_325.xlsx`](file:///c:/Users/AD-LAB/Downloads/ECG-APP-main/appium-tests/ECG_App_E2E_Test_Cases_325.xlsx) contains two complete worksheets:

### Sheet 1: `Executive Summary`
- **Dashboard & KPIs**: Total test cases, priority breakdown, coverage status.
- **Module Distribution**:
  - `MOD-01`: Authentication & Role-Based Access Control (35 Tests)
  - `MOD-02`: Operating Hours & Time-Gating Engine (20 Tests)
  - `MOD-03`: Clinic User Dashboard & KPI Metrics (25 Tests)
  - `MOD-04`: Patient Registration, Search & Phone Normalization (30 Tests)
  - `MOD-05`: ECG Capture, Consent & Multipart Upload (40 Tests)
  - `MOD-06`: Duty Roster & Auto-Assignment Engine (30 Tests)
  - `MOD-07`: High Load Governor & 15-Min Stale Closure (30 Tests)
  - `MOD-08`: Doctor Dashboard, Review Queue & Triage (30 Tests)
  - `MOD-09`: Postgraduate (PG) Management & Password Rules (30 Tests)
  - `MOD-10`: Task Detail, Zoom Viewer & Clinical Opinions (35 Tests)
  - `MOD-11`: Push Notifications (FCM v1) & Deep Linking (20 Tests)
  - `MOD-12`: Security, Network Latency & Boundary Cases (25 Tests)
- **Priority Breakdown**:
  - **P1 (Critical / Blocker)**: 217 Tests (66.8%)
  - **P2 (High)**: 90 Tests (27.7%)
  - **P3 (Medium / Low)**: 18 Tests (5.5%)

### Sheet 2: `Detailed Test Cases`
Every test case includes:
1. `Test Case ID` (e.g., `TC-AUTH-001`, `TC-TIME-036`)
2. `Module` & `Sub-Module / Screen`
3. `Test Scenario` & `Test Case Description`
4. `Preconditions`
5. `Test Execution Steps` (numbered step-by-step instructions)
6. `Test Input Data`
7. `Expected Result`
8. `Priority` (Color-coded: Red for P1, Orange for P2, Green for P3)
9. `Test Type` (E2E Functional, Negative, Security, Boundary, UI/UX)
10. `Execution Type` (`Automated Appium`)
11. `Automation Status` (`Automated`)

---

## 🚀 How to Run the Appium Tests

### 1. Prerequisites
- **Node.js** & **Appium Server**:
  ```powershell
  npm install -g appium
  appium driver install uiautomator2
  ```
- **Python 3.10+** (or virtual environment):
  ```powershell
  pip install -r requirements.txt
  ```
- Start the Appium server:
  ```powershell
  appium --port 4723
  ```

### 2. Running All Tests
```powershell
pytest tests/ -v --html=reports/report.html
```

### 3. Running Specific Module or Priority Tests
- **Run Critical P1 Tests only**:
  ```powershell
  pytest tests/ -m p1 -v
  ```
- **Run Authentication Suite**:
  ```powershell
  pytest tests/test_01_authentication.py -v
  ```
- **Run Operating Hours Suite**:
  ```powershell
  pytest tests/test_02_user_dashboard.py -v
  ```
- **Run ECG Upload & Consent Suite**:
  ```powershell
  pytest tests/test_04_ecg_upload_workflow.py -v
  ```

---

## 📈 Re-Generating the Excel Sheet
If test cases are modified, you can re-generate the Excel report anytime with:
```powershell
node generate_test_cases_excel.js
```
The output file [`ECG_App_E2E_Test_Cases_325.xlsx`](file:///c:/Users/AD-LAB/Downloads/ECG-APP-main/appium-tests/ECG_App_E2E_Test_Cases_325.xlsx) will update automatically.
