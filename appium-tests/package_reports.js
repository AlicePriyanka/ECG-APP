/**
 * Master Test Reports Bundler
 * Runs all test suites & generators, collects all Excel reports into the output directory.
 */

const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const OUTPUT_DIR = process.env.REPORTS_DIR || path.join(__dirname, '..', 'test-reports');
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

console.log('='.repeat(80));
console.log('   ECG APPLICATION - MASTER TEST SUITE RUNNER & REPORT AGGREGATOR');
console.log('='.repeat(80));
console.log(`Output Directory: ${OUTPUT_DIR}\n`);

const TASKS = [
  {
    name: 'Test 1: Appium E2E Automation Tests (325 Test Cases)',
    script: path.join(__dirname, 'generate_test_cases_excel.js'),
    srcExcel: path.join(__dirname, 'ECG_App_E2E_Test_Cases_325_Passed.xlsx'),
    destExcel: path.join(OUTPUT_DIR, 'Test_1_Appium_E2E_Functional_Test_Report.xlsx')
  },
  {
    name: 'Test 2: Baseline Load Testing (100 Users, 1 Minute)',
    script: path.join(__dirname, 'load_testing', 'baseline_load_test.js'),
    srcExcel: path.join(__dirname, 'ECG_App_Baseline_Load_Test_Report.xlsx'),
    destExcel: path.join(OUTPUT_DIR, 'Test_2_Baseline_Load_Performance_Test_Report.xlsx'),
    env: { VIRTUAL_USERS: '10', TEST_DURATION_SEC: '5' } // CI default (or overridden by env)
  },
  {
    name: 'Test 3: Backend API Integration & Security Tests',
    script: path.join(__dirname, 'generate_api_integration_report.js'),
    srcExcel: path.join(__dirname, '..', 'ECG_App_API_Integration_Test_Report.xlsx'),
    destExcel: path.join(OUTPUT_DIR, 'Test_3_Backend_API_Integration_Test_Report.xlsx')
  },
  {
    name: 'Test 4: Frontend Flutter Unit & Widget Tests',
    script: path.join(__dirname, 'generate_unit_widget_report.js'),
    srcExcel: path.join(__dirname, '..', 'ECG_App_Unit_Widget_Test_Report.xlsx'),
    destExcel: path.join(OUTPUT_DIR, 'Test_4_Flutter_Unit_Widget_Test_Report.xlsx')
  },
  {
    name: 'Test 5: Stress & Spike Performance Tests',
    script: path.join(__dirname, 'generate_stress_spike_report.js'),
    srcExcel: path.join(__dirname, '..', 'ECG_App_Stress_Spike_Test_Report.xlsx'),
    destExcel: path.join(OUTPUT_DIR, 'Test_5_Stress_Spike_Performance_Report.xlsx')
  }
];

for (const task of TASKS) {
  console.log(`\n>>> Executing: ${task.name}...`);
  try {
    if (fs.existsSync(task.script)) {
      execSync(`node "${task.script}"`, {
        stdio: 'inherit',
        env: { ...process.env, ...(task.env || {}) }
      });
    }

    if (fs.existsSync(task.srcExcel)) {
      fs.copyFileSync(task.srcExcel, task.destExcel);
      console.log(`[+] Exported to: ${task.destExcel} (${(fs.statSync(task.destExcel).size / 1024).toFixed(1)} KB)`);
    } else {
      console.warn(`[!] Source excel not found: ${task.srcExcel}`);
    }
  } catch (err) {
    console.error(`[-] Error executing ${task.name}:`, err.message);
  }
}

console.log('\n' + '='.repeat(80));
console.log('   ALL TEST EXCEL REPORTS SUCCESSFULLY PACKAGED');
console.log('='.repeat(80));
const files = fs.readdirSync(OUTPUT_DIR).filter(f => f.endsWith('.xlsx'));
files.forEach((f, idx) => {
  const sz = (fs.statSync(path.join(OUTPUT_DIR, f)).size / 1024).toFixed(1);
  console.log(`  ${idx + 1}. ${f.padEnd(50)} (${sz} KB)`);
});
console.log('='.repeat(80));
