// Application State - storing results in memory (no localStorage)
const appState = {
    results: [],
    currentAlgorithm: 'ecc',
    chart: null
};

// Algorithm Data
const algorithms = {
    ecc: {
        id: 1,
        name: 'ECC',
        fullName: 'ECC (NIST P-256)',
        code: 'ecc',
        color: '#3498db',
        privateKeySize: '32 bytes',
        publicKeySize: '64 bytes',
        signatureSize: '64 bytes',
        avgTime: '2.34 ms',
        security: '128-bit (classical)',
        description: 'Traditional elliptic-curve cryptography',
        advantages: ['Fast performance', 'Small key sizes', 'Well-studied'],
        disadvantages: ['Vulnerable to quantum attacks', 'Threat from quantum computing']
    },
    dilithium: {
        id: 2,
        name: 'CRYSTALS-Dilithium',
        fullName: 'CRYSTALS-Dilithium',
        code: 'dilithium',
        color: '#2ecc71',
        privateKeySize: '2528 bytes',
        publicKeySize: '1312 bytes',
        signatureSize: '2044 bytes',
        avgTime: '4.56 ms',
        security: '128-bit (quantum-resistant)',
        description: 'NIST-standardized lattice-based digital signature',
        advantages: ['Quantum-resistant', 'NIST standardized', 'Strong security proof'],
        disadvantages: ['Larger keys', 'Slower than ECC', 'Newer, less deployed']
    }
};

// Operation Names
const operations = {
    keygen: {
        id: 1,
        name: 'Key Generation',
        code: 'keygen',
        description: 'Generate a cryptographic key pair'
    },
    sign: {
        id: 2,
        name: 'Message Signing',
        code: 'sign',
        description: 'Create a digital signature'
    },
    verify: {
        id: 3,
        name: 'Signature Verification',
        code: 'verify',
        description: 'Verify a digital signature'
    }
};

// Cryptographic Implementation Simulator
class CryptographicInterface {
    constructor(algorithmType) {
        this.algorithmType = algorithmType;
    }

    async generateKeys(messageSize) {
        await this.simulateDelay();
        const baseTime = this.algorithmType === 'ecc' ? 2.0 : 4.0;
        const baseMemory = this.algorithmType === 'ecc' ? 512 : 768;
        const variation = 0.3;
        
        return {
            executionTime: baseTime + (Math.random() * variation * 2 - variation),
            memoryUsage: baseMemory + (Math.random() * 256),
            status: 'success'
        };
    }

    async sign(messageSize) {
        await this.simulateDelay();
        const sizeMultiplier = Math.sqrt(messageSize / 256);
        const baseTime = this.algorithmType === 'ecc' ? 1.5 : 3.2;
        const baseMemory = this.algorithmType === 'ecc' ? 384 : 512;
        const variation = 0.25;
        
        return {
            executionTime: (baseTime * sizeMultiplier) + (Math.random() * variation * 2 - variation),
            memoryUsage: (baseMemory * sizeMultiplier) + (Math.random() * 128),
            status: 'success'
        };
    }

    async verify(messageSize) {
        await this.simulateDelay();
        const sizeMultiplier = Math.sqrt(messageSize / 256);
        const baseTime = this.algorithmType === 'ecc' ? 2.5 : 2.8;
        const baseMemory = this.algorithmType === 'ecc' ? 256 : 384;
        const variation = 0.2;
        const successRate = 0.98;
        
        return {
            executionTime: (baseTime * sizeMultiplier) + (Math.random() * variation * 2 - variation),
            memoryUsage: (baseMemory * sizeMultiplier) + (Math.random() * 100),
            status: Math.random() < successRate ? 'success' : 'failure'
        };
    }

    simulateDelay() {
        const minDelay = 400;
        const maxDelay = 800;
        return new Promise(resolve => 
            setTimeout(resolve, minDelay + Math.random() * (maxDelay - minDelay))
        );
    }
}

// Test Controller
class TestController {
    constructor() {
        this.eccImplementation = new CryptographicInterface('ecc');
        this.dilithiumImplementation = new CryptographicInterface('dilithium');
    }

    async runTest(algorithm, operation, messageSize) {
        const implementation = algorithm === 'ecc' ? 
            this.eccImplementation : this.dilithiumImplementation;
        
        let result;
        switch(operation) {
            case 'keygen':
                result = await implementation.generateKeys(messageSize);
                break;
            case 'sign':
                result = await implementation.sign(messageSize);
                break;
            case 'verify':
                result = await implementation.verify(messageSize);
                break;
            default:
                throw new Error('Unknown operation');
        }

        return {
            timestamp: new Date().toISOString(),
            algorithm: algorithm,
            operation: operation,
            messageSize: messageSize,
            executionTime: Math.max(0.1, result.executionTime),
            memoryUsage: Math.max(10, result.memoryUsage),
            status: result.status
        };
    }
}

const controller = new TestController();

// UI Functions
function initializeApp() {
    console.log('Initializing application...');
    
    // Load sample data
    loadSampleData();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize UI
    updateAlgorithmInfo('ecc');
    updateChart();
    updateStatistics();
    
    console.log('Application initialized successfully!');
}

function setupEventListeners() {
    // Algorithm selection
    document.querySelectorAll('input[name="algorithm"]').forEach(radio => {
        radio.addEventListener('change', handleAlgorithmChange);
    });

    // Message size slider
    const messageSizeInput = document.getElementById('messageSize');
    const messageSizeValue = document.getElementById('messageSizeValue');
    messageSizeInput.addEventListener('input', (e) => {
        messageSizeValue.textContent = e.target.value;
    });

    // Run test button
    document.getElementById('runTestBtn').addEventListener('click', runTest);
    
    // Export CSV button
    document.getElementById('exportCsvBtn').addEventListener('click', exportToCSV);
    
    // Clear results button
    document.getElementById('clearResultsBtn').addEventListener('click', clearResults);
}

function loadSampleData() {
    const sampleResults = [
        {
            timestamp: '2025-11-03T18:00:00Z',
            algorithm: 'ecc',
            operation: 'keygen',
            messageSize: 256,
            executionTime: 2.34,
            memoryUsage: 512.5,
            status: 'success'
        },
        {
            timestamp: '2025-11-03T18:00:05Z',
            algorithm: 'ecc',
            operation: 'sign',
            messageSize: 256,
            executionTime: 1.23,
            memoryUsage: 384.2,
            status: 'success'
        },
        {
            timestamp: '2025-11-03T18:00:10Z',
            algorithm: 'dilithium',
            operation: 'keygen',
            messageSize: 256,
            executionTime: 4.56,
            memoryUsage: 768.3,
            status: 'success'
        },
        {
            timestamp: '2025-11-03T18:00:15Z',
            algorithm: 'dilithium',
            operation: 'sign',
            messageSize: 256,
            executionTime: 3.45,
            memoryUsage: 512.1,
            status: 'success'
        }
    ];

    appState.results = sampleResults;
    renderResultsTable();
}

function handleAlgorithmChange(event) {
    appState.currentAlgorithm = event.target.value;
    updateAlgorithmInfo(appState.currentAlgorithm);
}

function updateAlgorithmInfo(algorithmCode) {
    const algo = algorithms[algorithmCode];
    
    document.getElementById('infoPrivateKey').textContent = algo.privateKeySize;
    document.getElementById('infoPublicKey').textContent = algo.publicKeySize;
    document.getElementById('infoSignature').textContent = algo.signatureSize;
    document.getElementById('infoSecurity').textContent = algo.security;
    document.getElementById('infoDescription').textContent = algo.description;
}

async function runTest() {
    const algorithm = document.querySelector('input[name="algorithm"]:checked').value;
    const operation = document.getElementById('operation').value;
    const messageSize = parseInt(document.getElementById('messageSize').value);
    const iterations = parseInt(document.getElementById('iterations').value);

    if (isNaN(messageSize) || messageSize < 1) {
        alert('Please enter a valid message size');
        return;
    }

    if (isNaN(iterations) || iterations < 1) {
        alert('Please enter a valid number of iterations');
        return;
    }

    // Disable button and show loader
    const btn = document.getElementById('runTestBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    
    btn.disabled = true;
    btnText.textContent = 'Running test...';
    btnLoader.classList.remove('hidden');

    try {
        for (let i = 0; i < iterations; i++) {
            const result = await controller.runTest(algorithm, operation, messageSize);
            appState.results.unshift(result);
            
            // Show current result
            displayCurrentResult(result);
            
            // Update UI
            renderResultsTable();
            updateStatistics();
            updateChart();
            
            // Small delay between iterations
            if (i < iterations - 1) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }
    } catch (error) {
        console.error('Error during test:', error);
        alert('Error while running the test: ' + error.message);
    } finally {
        // Re-enable button
        btn.disabled = false;
        btnText.textContent = 'Run Test';
        btnLoader.classList.add('hidden');
    }
}

function displayCurrentResult(result) {
    const container = document.getElementById('currentResult');
    container.classList.remove('hidden');

    const algo = algorithms[result.algorithm];
    const op = operations[result.operation];

    document.getElementById('resAlgorithm').innerHTML = 
        `<span class="badge badge--${result.algorithm}">${algo.name}</span>`;
    document.getElementById('resOperation').textContent = op.name;
    document.getElementById('resMessageSize').textContent = `${result.messageSize} bytes`;
    document.getElementById('resExecutionTime').textContent = `${result.executionTime.toFixed(2)} ms`;
    document.getElementById('resMemoryUsage').textContent = `${result.memoryUsage.toFixed(2)} KB`;
    document.getElementById('resStatus').innerHTML = 
        `<span class="badge badge--${result.status}">${result.status === 'success' ? 'Success' : 'Failure'}</span>`;
}

function renderResultsTable() {
    const tbody = document.getElementById('resultsTableBody');
    tbody.innerHTML = '';

    const displayResults = appState.results.slice(0, 20);
    
    if (displayResults.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="7" style="text-align: center; color: var(--color-text-secondary);">No results. Run a test to see data.</td>';
        tbody.appendChild(row);
        return;
    }

    displayResults.forEach(result => {
        const row = document.createElement('tr');
        const date = new Date(result.timestamp);
        const algo = algorithms[result.algorithm];
        const op = operations[result.operation];
        
        row.innerHTML = `
            <td>${date.toLocaleTimeString('en-US')}</td>
            <td><span class="badge badge--${result.algorithm}">${algo.name}</span></td>
            <td>${op.name}</td>
            <td>${result.messageSize} B</td>
            <td>${result.executionTime.toFixed(2)} ms</td>
            <td>${result.memoryUsage.toFixed(2)} KB</td>
            <td><span class="badge badge--${result.status}">${result.status === 'success' ? 'Success' : 'Failure'}</span></td>
        `;
        
        tbody.appendChild(row);
    });
}

function updateStatistics() {
    const eccResults = appState.results.filter(r => r.algorithm === 'ecc' && r.status === 'success');
    const dilithiumResults = appState.results.filter(r => r.algorithm === 'dilithium' && r.status === 'success');

    // Average execution time
    const avgTimeEcc = eccResults.length > 0 
        ? eccResults.reduce((sum, r) => sum + r.executionTime, 0) / eccResults.length
        : 0;
    const avgTimeDilithium = dilithiumResults.length > 0
        ? dilithiumResults.reduce((sum, r) => sum + r.executionTime, 0) / dilithiumResults.length
        : 0;

    // Average memory usage
    const avgMemoryEcc = eccResults.length > 0
        ? eccResults.reduce((sum, r) => sum + r.memoryUsage, 0) / eccResults.length
        : 0;
    const avgMemoryDilithium = dilithiumResults.length > 0
        ? dilithiumResults.reduce((sum, r) => sum + r.memoryUsage, 0) / dilithiumResults.length
        : 0;

    document.getElementById('avgTimeEcc').textContent = 
        avgTimeEcc > 0 ? `${avgTimeEcc.toFixed(2)} ms` : '-';
    document.getElementById('avgTimeDilithium').textContent = 
        avgTimeDilithium > 0 ? `${avgTimeDilithium.toFixed(2)} ms` : '-';
    document.getElementById('avgMemoryEcc').textContent = 
        avgMemoryEcc > 0 ? `${avgMemoryEcc.toFixed(2)} KB` : '-';
    document.getElementById('avgMemoryDilithium').textContent = 
        avgMemoryDilithium > 0 ? `${avgMemoryDilithium.toFixed(2)} KB` : '-';
}

function updateChart() {
    const ctx = document.getElementById('comparisonChart');
    
    // Group results by operation
    const operationKeys = ['keygen', 'sign', 'verify'];
    const eccData = [];
    const dilithiumData = [];

    operationKeys.forEach(op => {
        const eccResults = appState.results.filter(r => 
            r.algorithm === 'ecc' && r.operation === op && r.status === 'success'
        );
        const dilithiumResults = appState.results.filter(r => 
            r.algorithm === 'dilithium' && r.operation === op && r.status === 'success'
        );

        const eccAvg = eccResults.length > 0
            ? eccResults.reduce((sum, r) => sum + r.executionTime, 0) / eccResults.length
            : 0;
        const dilithiumAvg = dilithiumResults.length > 0
            ? dilithiumResults.reduce((sum, r) => sum + r.executionTime, 0) / dilithiumResults.length
            : 0;

        eccData.push(eccAvg);
        dilithiumData.push(dilithiumAvg);
    });

    if (appState.chart) {
        appState.chart.destroy();
    }

    appState.chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Key Generation', 'Signing', 'Verification'],
            datasets: [
                {
                    label: 'ECC',
                    data: eccData,
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderColor: '#3498db',
                    borderWidth: 2
                },
                {
                    label: 'CRYSTALS-Dilithium',
                    data: dilithiumData,
                    backgroundColor: 'rgba(46, 204, 113, 0.7)',
                    borderColor: '#2ecc71',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Average operation execution time (ms)',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Time (ms)'
                    }
                }
            }
        }
    });
}

function clearResults() {
    if (appState.results.length === 0) {
        alert('No results to clear');
        return;
    }

    if (confirm('Are you sure you want to clear all results?')) {
        appState.results = [];
        
        // Hide current result
        document.getElementById('currentResult').classList.add('hidden');
        
        // Update UI
        renderResultsTable();
        updateStatistics();
        updateChart();
    }
}

function exportToCSV() {
    if (appState.results.length === 0) {
        alert('No results to export');
        return;
    }

    // CSV Header
    const headers = ['timestamp', 'algorithm', 'operation', 'message_size_bytes', 'execution_time_ms', 'memory_usage_kb', 'status'];
    
    // CSV Rows
    const rows = appState.results.map(result => [
        result.timestamp,
        result.algorithm,
        result.operation,
        result.messageSize,
        result.executionTime.toFixed(4),
        result.memoryUsage.toFixed(4),
        result.status
    ]);

    // Combine header and rows
    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
    ].join('\n');

    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    link.setAttribute('href', url);
    link.setAttribute('download', `crypto_benchmark_${timestamp}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
}

// Initialize the application when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}