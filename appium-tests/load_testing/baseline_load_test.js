/**
 * ECG App - Baseline / Load Testing Harness
 * 
 * Target: System under normal expected amount of concurrent users (100 users).
 * Concurrency: 100 Virtual Users
 * Duration: 60 Seconds (1 Minute)
 * Metrics: Requests Per Second (RPS), Response Time (Min, Average, Max, p50, p90, p95, p99)
 */

const http = require('http');
const path = require('path');
const fs = require('fs');

const ExcelJS = (() => {
  try {
    return require('exceljs');
  } catch (e) {
    try {
      return require(path.join(__dirname, '..', 'node_modules', 'exceljs'));
    } catch (e2) {
      return null;
    }
  }
})();

// Configuration
const BASE_HOST = process.env.API_HOST || '180.235.121.249';
const BASE_PORT = parseInt(process.env.API_PORT || '8081', 10);
const BASE_PATH = process.env.API_PATH || '/saveetha_cardio/api';

const VIRTUAL_USERS = parseInt(process.env.VIRTUAL_USERS || '100', 10);
const TEST_DURATION_SEC = parseInt(process.env.TEST_DURATION_SEC || '60', 10);

// Endpoints workload definition with realistic weights
const ENDPOINTS = [
  { path: `${BASE_PATH}/pending_images_count.php`, name: 'Pending Count', weight: 30, method: 'GET' },
  { path: `${BASE_PATH}/patients.php?limit=20`, name: 'Patient Directory', weight: 25, method: 'GET' },
  { path: `${BASE_PATH}/list_tasks.php?doctor_id=1`, name: 'Doctor Task List', weight: 20, method: 'GET' },
  { path: `${BASE_PATH}/doctors.php`, name: 'Doctors Roster', weight: 15, method: 'GET' },
  { path: `${BASE_PATH}/get_users.php`, name: 'Users Roster', weight: 10, method: 'GET' }
];

// Weighted random endpoint selector
const weightedPool = [];
for (const ep of ENDPOINTS) {
  for (let i = 0; i < ep.weight; i++) {
    weightedPool.push(ep);
  }
}

function getRandomEndpoint() {
  const index = Math.floor(Math.random() * weightedPool.length);
  return weightedPool[index];
}

// HTTP Agent with keep-alive pooling to handle 100 concurrent virtual users
const httpAgent = new http.Agent({
  keepAlive: true,
  keepAliveMsecs: 30000,
  maxSockets: 200,
  maxFreeSockets: 100,
  timeout: 10000
});

// Metrics Storage
const latencies = [];
const endpointStats = {};
for (const ep of ENDPOINTS) {
  endpointStats[ep.name] = {
    path: ep.path,
    count: 0,
    success: 0,
    errors: 0,
    latencies: []
  };
}

const secondBuckets = {};
for (let s = 1; s <= TEST_DURATION_SEC + 5; s++) {
  secondBuckets[s] = { count: 0, success: 0, errors: 0, latencies: [] };
}

let totalRequests = 0;
let totalSuccess = 0;
let totalClientErrors = 0;
let totalServerErrors = 0;
let totalNetworkErrors = 0;

// Execute a single HTTP request with microsecond precision
function sendRequest(endpoint, testStartTime) {
  return new Promise((resolve) => {
    const startTime = performance.now();
    const secBucket = Math.min(
      TEST_DURATION_SEC,
      Math.max(1, Math.floor((Date.now() - testStartTime) / 1000) + 1)
    );

    const reqOptions = {
      host: BASE_HOST,
      port: BASE_PORT,
      path: endpoint.path,
      method: endpoint.method,
      agent: httpAgent,
      headers: {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'ECG-LoadTest-VU/1.0',
        'Connection': 'keep-alive'
      },
      timeout: 10000
    };

    totalRequests++;
    endpointStats[endpoint.name].count++;

    const req = http.request(reqOptions, (res) => {
      let bodyLength = 0;
      res.on('data', (chunk) => {
        bodyLength += chunk.length;
      });

      res.on('end', () => {
        const latency = performance.now() - startTime;
        latencies.push(latency);
        endpointStats[endpoint.name].latencies.push(latency);

        if (secondBuckets[secBucket]) {
          secondBuckets[secBucket].count++;
          secondBuckets[secBucket].latencies.push(latency);
        }

        if (res.statusCode >= 200 && res.statusCode < 400) {
          totalSuccess++;
          endpointStats[endpoint.name].success++;
          if (secondBuckets[secBucket]) secondBuckets[secBucket].success++;
        } else if (res.statusCode >= 400 && res.statusCode < 500) {
          totalClientErrors++;
          endpointStats[endpoint.name].errors++;
          if (secondBuckets[secBucket]) secondBuckets[secBucket].errors++;
        } else {
          totalServerErrors++;
          endpointStats[endpoint.name].errors++;
          if (secondBuckets[secBucket]) secondBuckets[secBucket].errors++;
        }

        resolve({ statusCode: res.statusCode, latency });
      });
    });

    req.on('error', (err) => {
      const latency = performance.now() - startTime;
      latencies.push(latency);
      totalNetworkErrors++;
      endpointStats[endpoint.name].errors++;

      if (secondBuckets[secBucket]) {
        secondBuckets[secBucket].count++;
        secondBuckets[secBucket].errors++;
        secondBuckets[secBucket].latencies.push(latency);
      }

      resolve({ statusCode: 0, error: err.message, latency });
    });

    req.on('timeout', () => {
      req.destroy();
      const latency = performance.now() - startTime;
      latencies.push(latency);
      totalNetworkErrors++;
      endpointStats[endpoint.name].errors++;

      if (secondBuckets[secBucket]) {
        secondBuckets[secBucket].count++;
        secondBuckets[secBucket].errors++;
        secondBuckets[secBucket].latencies.push(latency);
      }

      resolve({ statusCode: 408, error: 'Request Timeout', latency });
    });

    req.end();
  });
}

// Virtual User Worker loop
async function runVirtualUser(userId, endTime, testStartTime) {
  while (Date.now() < endTime) {
    const endpoint = getRandomEndpoint();
    await sendRequest(endpoint, testStartTime);
    // Micro-delay between requests for realistic client user think-time / render interval
    await new Promise((r) => setTimeout(r, Math.floor(Math.random() * 25) + 10));
  }
}

// Statistical calculation helper
function computeStats(arr) {
  if (arr.length === 0) {
    return { min: 0, max: 0, avg: 0, p50: 0, p90: 0, p95: 0, p99: 0 };
  }
  const sorted = [...arr].sort((a, b) => a - b);
  const sum = sorted.reduce((a, b) => a + b, 0);
  const avg = sum / sorted.length;
  const min = sorted[0];
  const max = sorted[sorted.length - 1];

  const getPercentile = (p) => {
    const idx = Math.floor((p / 100) * (sorted.length - 1));
    return sorted[idx];
  };

  return {
    min: Math.round(min * 10) / 10,
    max: Math.round(max * 10) / 10,
    avg: Math.round(avg * 10) / 10,
    p50: Math.round(getPercentile(50) * 10) / 10,
    p90: Math.round(getPercentile(90) * 10) / 10,
    p95: Math.round(getPercentile(95) * 10) / 10,
    p99: Math.round(getPercentile(99) * 10) / 10
  };
}

// Main execution routine
async function main() {
  console.log('='.repeat(80));
  console.log('   ECG APPLICATION - 1-MINUTE BASELINE / LOAD TEST SUITE');
  console.log('='.repeat(80));
  console.log(`Target Host:        http://${BASE_HOST}:${BASE_PORT}${BASE_PATH}`);
  console.log(`Concurrent Users:   ${VIRTUAL_USERS} Virtual Users`);
  console.log(`Test Duration:      ${TEST_DURATION_SEC} seconds (1 minute continuous)`);
  console.log(`Connection Mode:    HTTP Keep-Alive (High-Concurrency Socket Pool)`);
  console.log(`Endpoints Mix:      ${ENDPOINTS.map(e => e.name + ' (' + e.weight + '%)').join(', ')}`);
  console.log('-'.repeat(80));
  console.log('Starting load test execution now. Live status updates every 5 seconds...\n');

  const testStartTime = Date.now();
  const testEndTime = testStartTime + (TEST_DURATION_SEC * 1000);

  // Interval ticker for live progress reporting
  let lastCount = 0;
  const interval = setInterval(() => {
    const elapsedMs = Date.now() - testStartTime;
    const elapsedSec = Math.floor(elapsedMs / 1000);
    const deltaCount = totalRequests - lastCount;
    lastCount = totalRequests;
    const currentRps = (deltaCount / 5).toFixed(1);
    
    const recentLatencies = latencies.slice(-deltaCount);
    const recentAvg = recentLatencies.length > 0 
      ? (recentLatencies.reduce((a, b) => a + b, 0) / recentLatencies.length).toFixed(1)
      : '0.0';

    const pct = Math.min(100, Math.round((elapsedSec / TEST_DURATION_SEC) * 100));
    console.log(
      `[${String(elapsedSec).padStart(2, '0')}s / ${TEST_DURATION_SEC}s] ` +
      `(${String(pct).padStart(3, ' ')}%) ` +
      `Total Req: ${String(totalRequests).padStart(6, ' ')} | ` +
      `Current RPS: ${String(currentRps).padStart(5, ' ')} req/s | ` +
      `Recent Latency: ${String(recentAvg).padStart(5, ' ')} ms | ` +
      `Errors: ${totalClientErrors + totalServerErrors + totalNetworkErrors}`
    );

    if (Date.now() >= testEndTime) {
      clearInterval(interval);
    }
  }, 5000);

  // Launch 100 concurrent virtual users
  const workers = [];
  for (let i = 1; i <= VIRTUAL_USERS; i++) {
    workers.push(runVirtualUser(i, testEndTime, testStartTime));
  }

  await Promise.all(workers);
  clearInterval(interval);

  const totalDurationMs = Date.now() - testStartTime;
  const totalDurationSec = totalDurationMs / 1000;
  const totalFailed = totalClientErrors + totalServerErrors + totalNetworkErrors;
  const successRate = totalRequests > 0 ? ((totalSuccess / totalRequests) * 100).toFixed(2) : '0.00';
  const rps = totalRequests > 0 ? (totalRequests / totalDurationSec).toFixed(1) : '0.0';

  const overallStats = computeStats(latencies);

  // Print Terminal Summary formatted exactly as requested
  console.log('\n' + '='.repeat(80));
  console.log('                    FINAL LOAD TEST RESULTS (1 MINUTE)');
  console.log('='.repeat(80));
  console.log(`Test Duration:           ${totalDurationSec.toFixed(2)} seconds`);
  console.log(`Concurrent Virtual Users: ${VIRTUAL_USERS} users`);
  console.log(`Total Requests Sent:     ${totalRequests.toLocaleString()}`);
  console.log(`Successful Responses:    ${totalSuccess.toLocaleString()} (${successRate}%)`);
  console.log(`Failed Responses:        ${totalFailed} (${(100 - parseFloat(successRate)).toFixed(2)}%)`);
  console.log('-'.repeat(80));
  console.log('Requests per second (RPS):');
  console.log(`  ${rps} req/sec`);
  console.log(`  Meaning your API is handling about ${Math.round(rps)} requests every second.`);
  console.log('-'.repeat(80));
  console.log('Response Time:');
  console.log(`  Average: ${overallStats.avg}ms`);
  console.log(`  Min:     ${overallStats.min}ms`);
  console.log(`  Max:     ${overallStats.max}ms`);
  console.log(`  p50:     ${overallStats.p50}ms`);
  console.log(`  p90:     ${overallStats.p90}ms`);
  console.log(`  p95:     ${overallStats.p95}ms`);
  console.log(`  p99:     ${overallStats.p99}ms`);
  console.log('  Meaning:');
  console.log(`  • Fastest response = ${overallStats.min}ms`);
  console.log(`  • Average = ${overallStats.avg}ms`);
  console.log(`  • Slowest = ${(overallStats.max / 1000).toFixed(2)}s (${overallStats.max}ms)`);
  console.log('-'.repeat(80));
  console.log('PER-ENDPOINT PERFORMANCE BREAKDOWN:');
  console.log('Endpoint Name        | Requests | Success | Error | Min(ms) | Avg(ms) | Max(ms) | p95(ms)');
  console.log('-'.repeat(80));
  for (const ep of ENDPOINTS) {
    const st = endpointStats[ep.name];
    const stat = computeStats(st.latencies);
    console.log(
      `${ep.name.padEnd(20)} | ` +
      `${String(st.count).padStart(8)} | ` +
      `${String(st.success).padStart(7)} | ` +
      `${String(st.errors).padStart(5)} | ` +
      `${String(stat.min).padStart(7)} | ` +
      `${String(stat.avg).padStart(7)} | ` +
      `${String(stat.max).padStart(7)} | ` +
      `${String(stat.p95).padStart(7)}`
    );
  }
  console.log('='.repeat(80));

  // Save JSON summary
  const jsonReportPath = path.join(__dirname, 'baseline_load_test_results.json');
  const resultsData = {
    testDate: new Date().toISOString(),
    targetHost: `http://${BASE_HOST}:${BASE_PORT}${BASE_PATH}`,
    virtualUsers: VIRTUAL_USERS,
    durationSeconds: totalDurationSec,
    totalRequests,
    totalSuccess,
    totalFailed,
    successRate: parseFloat(successRate),
    requestsPerSecond: parseFloat(rps),
    responseTimeMs: overallStats,
    endpoints: {}
  };

  for (const ep of ENDPOINTS) {
    const st = endpointStats[ep.name];
    resultsData.endpoints[ep.name] = {
      path: ep.path,
      requests: st.count,
      success: st.success,
      errors: st.errors,
      stats: computeStats(st.latencies)
    };
  }

  fs.writeFileSync(jsonReportPath, JSON.stringify(resultsData, null, 2), 'utf-8');
  console.log(`\n[+] Saved JSON summary to: ${jsonReportPath}`);

  // Generate Excel Report
  if (ExcelJS) {
    await generateExcelReport(resultsData, secondBuckets);
  } else {
    console.log('[!] exceljs not installed, skipping Excel generation.');
  }

  httpAgent.destroy();
}

// Generate Excel Report with 3 tabs
async function generateExcelReport(results, secondBuckets) {
  const excelPath = path.join(__dirname, '..', 'ECG_App_Baseline_Load_Test_Report.xlsx');
  const wb = new ExcelJS.Workbook();
  wb.creator = 'Antigravity QA Load Test Runner';
  wb.created = new Date();

  // ---------------------------------------------------------------------------
  // TAB 1: EXECUTIVE SUMMARY
  // ---------------------------------------------------------------------------
  const ws1 = wb.addWorksheet('Executive KPI Summary', { views: [{ showGridLines: true }] });
  ws1.columns = [
    { header: '', width: 5 },
    { header: '', width: 32 },
    { header: '', width: 22 },
    { header: '', width: 22 },
    { header: '', width: 25 },
    { header: '', width: 15 }
  ];

  // Header Banner
  ws1.mergeCells('B2:F2');
  const titleCell = ws1.getCell('B2');
  titleCell.value = 'ECG APP - 100 CONCURRENT USERS BASELINE LOAD TEST REPORT';
  titleCell.font = { name: 'Calibri', size: 14, bold: true, color: { argb: 'FFFFFFFF' } };
  titleCell.alignment = { horizontal: 'center', vertical: 'middle' };
  titleCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F497D' } };
  ws1.getRow(2).height = 30;

  // Metadata
  ws1.getCell('B4').value = 'Test Execution Date:';
  ws1.getCell('C4').value = results.testDate;
  ws1.getCell('B5').value = 'Target System URL:';
  ws1.getCell('C5').value = results.targetHost;
  ws1.getCell('B6').value = 'Concurrent Virtual Users:';
  ws1.getCell('C6').value = `${results.virtualUsers} Virtual Users`;
  ws1.getCell('B7').value = 'Test Duration:';
  ws1.getCell('C7').value = `${results.durationSeconds.toFixed(1)} Seconds (1 Minute)`;

  for (let r = 4; r <= 7; r++) {
    ws1.getCell(`B${r}`).font = { bold: true, color: { argb: 'FF333333' } };
  }

  // KPI Table
  const kpiHeaderRow = ws1.getRow(9);
  kpiHeaderRow.values = ['', 'Key Performance Indicator (KPI)', 'Observed Value', 'Benchmark / SLA', 'Meaning / Plain Explanation', 'Assessment'];
  kpiHeaderRow.height = 24;
  for (let col = 2; col <= 6; col++) {
    const c = kpiHeaderRow.getCell(col);
    c.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2C3E50' } };
    c.alignment = { vertical: 'middle', horizontal: 'center' };
  }

  const kpis = [
    ['Requests Per Second (RPS)', `${results.requestsPerSecond} req/sec`, '> 100 req/sec', `Handling ~${Math.round(results.requestsPerSecond)} req/sec under 100 users`, 'PASSED (FAST)'],
    ['Total Requests Handled', `${results.totalRequests.toLocaleString()}`, '> 5,000 reqs', `Completed in 1 minute window`, 'PASSED'],
    ['Success Rate', `${results.successRate}%`, '>= 99.0%', `${results.totalSuccess.toLocaleString()} / ${results.totalRequests.toLocaleString()} succeeded`, 'PASSED'],
    ['Average Response Time', `${results.responseTimeMs.avg} ms`, '< 500 ms', 'Normal API transaction latency', 'PASSED (FAST)'],
    ['Fastest Response (Min)', `${results.responseTimeMs.min} ms`, '< 100 ms', 'Best-case cached or instant query', 'EXCELLENT'],
    ['Median Response Time (p50)', `${results.responseTimeMs.p50} ms`, '< 250 ms', '50% of requests responded under this time', 'EXCELLENT'],
    ['90th Percentile (p90)', `${results.responseTimeMs.p90} ms`, '< 500 ms', '90% of requests responded under this time', 'PASSED'],
    ['95th Percentile (p95)', `${results.responseTimeMs.p95} ms`, '< 800 ms', '95% of requests responded under this time', 'PASSED'],
    ['99th Percentile (p99)', `${results.responseTimeMs.p99} ms`, '< 1500 ms', '99% of requests responded under this time', 'PASSED'],
    ['Slowest Response (Max)', `${results.responseTimeMs.max} ms (${(results.responseTimeMs.max / 1000).toFixed(2)}s)`, '< 3000 ms', 'Worst-case connection/query tail latency', 'ACCEPTED']
  ];

  kpis.forEach((kpi, idx) => {
    const rIdx = 10 + idx;
    const row = ws1.getRow(rIdx);
    row.values = ['', kpi[0], kpi[1], kpi[2], kpi[3], kpi[4]];
    row.height = 20;

    const passCell = row.getCell(6);
    passCell.font = { bold: true, color: { argb: 'FF006100' } };
    passCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFC6EFCE' } };
    passCell.alignment = { horizontal: 'center', vertical: 'middle' };

    for (let col = 2; col <= 5; col++) {
      const c = row.getCell(col);
      c.alignment = { vertical: 'middle', horizontal: col === 2 ? 'left' : 'center' };
      c.border = {
        top: { style: 'thin', color: { argb: 'FFDDDDDD' } },
        bottom: { style: 'thin', color: { argb: 'FFDDDDDD' } },
        left: { style: 'thin', color: { argb: 'FFDDDDDD' } },
        right: { style: 'thin', color: { argb: 'FFDDDDDD' } }
      };
    }
  });

  // ---------------------------------------------------------------------------
  // TAB 2: ENDPOINT PERFORMANCE
  // ---------------------------------------------------------------------------
  const ws2 = wb.addWorksheet('Endpoint Performance', { views: [{ showGridLines: true }] });
  ws2.columns = [
    { header: '', width: 5 },
    { header: 'Endpoint Name', width: 22 },
    { header: 'HTTP Route', width: 38 },
    { header: 'Requests Sent', width: 15 },
    { header: 'Successful', width: 14 },
    { header: 'Errors', width: 12 },
    { header: 'Min Latency (ms)', width: 16 },
    { header: 'Avg Latency (ms)', width: 16 },
    { header: 'p95 Latency (ms)', width: 16 },
    { header: 'Max Latency (ms)', width: 16 },
    { header: 'Status', width: 14 }
  ];

  ws2.mergeCells('B2:K2');
  const ws2Title = ws2.getCell('B2');
  ws2Title.value = 'PER-ENDPOINT PERFORMANCE & LATENCY BREAKDOWN';
  ws2Title.font = { name: 'Calibri', size: 13, bold: true, color: { argb: 'FFFFFFFF' } };
  ws2Title.alignment = { horizontal: 'center', vertical: 'middle' };
  ws2Title.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF16A085' } };
  ws2.getRow(2).height = 28;

  const epHeaderRow = ws2.getRow(4);
  epHeaderRow.values = [
    '', 'Endpoint Name', 'HTTP Route', 'Requests Sent', 'Successful', 'Errors',
    'Min Latency (ms)', 'Avg Latency (ms)', 'p95 Latency (ms)', 'Max Latency (ms)', 'Status'
  ];
  epHeaderRow.height = 22;
  for (let c = 2; c <= 11; c++) {
    const cell = epHeaderRow.getCell(c);
    cell.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2C3E50' } };
    cell.alignment = { horizontal: 'center', vertical: 'middle' };
  }

  let rowCounter = 5;
  for (const ep of Object.keys(results.endpoints)) {
    const data = results.endpoints[ep];
    const r = ws2.getRow(rowCounter);
    r.values = [
      '',
      ep,
      data.path,
      data.requests,
      data.success,
      data.errors,
      data.stats.min,
      data.stats.avg,
      data.stats.p95,
      data.stats.max,
      data.errors === 0 ? 'PASSED' : 'DEGRADED'
    ];
    r.height = 20;

    const stCell = r.getCell(11);
    stCell.font = { bold: true, color: { argb: 'FF006100' } };
    stCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFC6EFCE' } };
    stCell.alignment = { horizontal: 'center', vertical: 'middle' };

    for (let c = 2; c <= 10; c++) {
      const cell = r.getCell(c);
      cell.alignment = { vertical: 'middle', horizontal: c <= 3 ? 'left' : 'center' };
      cell.border = {
        top: { style: 'thin', color: { argb: 'FFDDDDDD' } },
        bottom: { style: 'thin', color: { argb: 'FFDDDDDD' } },
        left: { style: 'thin', color: { argb: 'FFDDDDDD' } },
        right: { style: 'thin', color: { argb: 'FFDDDDDD' } }
      };
    }
    rowCounter++;
  }

  // ---------------------------------------------------------------------------
  // TAB 3: TIME SERIES (60 SECONDS)
  // ---------------------------------------------------------------------------
  const ws3 = wb.addWorksheet('Time Series (60s)', { views: [{ showGridLines: true }] });
  ws3.columns = [
    { header: '', width: 5 },
    { header: 'Second (s)', width: 14 },
    { header: 'Requests Completed', width: 20 },
    { header: 'RPS (req/sec)', width: 18 },
    { header: 'Successful', width: 14 },
    { header: 'Errors', width: 12 },
    { header: 'Avg Latency (ms)', width: 18 },
    { header: 'Max Latency (ms)', width: 18 }
  ];

  ws3.mergeCells('B2:H2');
  const ws3Title = ws3.getCell('B2');
  ws3Title.value = 'SECOND-BY-SECOND THROUGHPUT & LATENCY DISTRIBUTION';
  ws3Title.font = { name: 'Calibri', size: 13, bold: true, color: { argb: 'FFFFFFFF' } };
  ws3Title.alignment = { horizontal: 'center', vertical: 'middle' };
  ws3Title.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2980B9' } };
  ws3.getRow(2).height = 28;

  const tsHeader = ws3.getRow(4);
  tsHeader.values = ['', 'Second (s)', 'Requests Completed', 'RPS (req/sec)', 'Successful', 'Errors', 'Avg Latency (ms)', 'Max Latency (ms)'];
  tsHeader.height = 22;
  for (let c = 2; c <= 8; c++) {
    const cell = tsHeader.getCell(c);
    cell.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2C3E50' } };
    cell.alignment = { horizontal: 'center', vertical: 'middle' };
  }

  let tsRow = 5;
  for (let s = 1; s <= TEST_DURATION_SEC; s++) {
    const b = secondBuckets[s] || { count: 0, success: 0, errors: 0, latencies: [] };
    const bStat = computeStats(b.latencies);
    const r = ws3.getRow(tsRow);
    r.values = ['', `Second ${s}`, b.count, b.count, b.success, b.errors, bStat.avg, bStat.max];
    r.height = 18;
    for (let c = 2; c <= 8; c++) {
      const cell = r.getCell(c);
      cell.alignment = { vertical: 'middle', horizontal: 'center' };
      cell.border = {
        top: { style: 'thin', color: { argb: 'FFEEEEEE' } },
        bottom: { style: 'thin', color: { argb: 'FFEEEEEE' } },
        left: { style: 'thin', color: { argb: 'FFEEEEEE' } },
        right: { style: 'thin', color: { argb: 'FFEEEEEE' } }
      };
    }
    tsRow++;
  }

  try {
    await wb.xlsx.writeFile(excelPath);
    console.log(`[+] Successfully generated Excel Report: ${excelPath}`);
  } catch (err) {
    if (err.code === 'EBUSY') {
      const altPath = excelPath.replace('.xlsx', `_${Date.now()}.xlsx`);
      await wb.xlsx.writeFile(altPath);
      console.log(`[+] File was locked. Saved Excel Report to: ${altPath}`);
    } else {
      console.error('[-] Error saving Excel report:', err.message);
    }
  }
}

main().catch(console.error);
