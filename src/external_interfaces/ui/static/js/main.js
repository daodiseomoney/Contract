// Initialize charts
function initializeCharts() {
    const ctx = document.getElementById('contractsChart')?.getContext('2d');
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'Active', 'Completed'],
                datasets: [{
                    data: [4, 8, 3],
                    backgroundColor: [
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(23, 162, 184, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Update stats
    const elements = {
        totalContracts: document.getElementById('totalContracts'),
        activeContracts: document.getElementById('activeContracts'),
        totalValue: document.getElementById('totalValue')
    };

    if (elements.totalContracts) elements.totalContracts.textContent = '15';
    if (elements.activeContracts) elements.activeContracts.textContent = '8';
    if (elements.totalValue) elements.totalValue.textContent = '$2.5M';

    updateRecentActivity();
    updateContractsTable();
}

// Update recent activity section
function updateRecentActivity() {
    const activities = [
        'Contract #123 tokenized successfully',
        'New property added to blockchain',
        'Budget split updated for Contract #456',
        'Compliance check completed'
    ];

    const activityList = document.getElementById('recentActivity');
    if (activityList) {
        activities.forEach(activity => {
            const item = document.createElement('a');
            item.className = 'list-group-item list-group-item-action';
            item.innerHTML = `
                <div class="d-flex w-100 justify-content-between">
                    <p class="mb-1">${activity}</p>
                    <small class="text-muted">Just now</small>
                </div>
            `;
            activityList.appendChild(item);
        });
    }
}

// Update contracts table
function updateContractsTable() {
    const sampleProjects = [
        { id: 'DEMO-001', property: 'Silicon Valley Office Complex', status: 'Demo', value: '$12.5M', created: '2025-03-17' },
        { id: 'DEMO-002', property: 'Manhattan Residential Tower', status: 'Demo', value: '$25M', created: '2025-03-17' },
        { id: 'DEMO-003', property: 'Dubai Smart City Project', status: 'Demo', value: '$40M', created: '2025-03-17' }
    ];

    const contractsTable = document.querySelector('#contractsTable tbody');
    const sampleSection = document.getElementById('sampleProjectsSection');

    if (contractsTable) {
        fetch('/api/contracts')
            .then(response => response.json())
            .then(contracts => {
                const displayContracts = contracts.length > 0 ? contracts : sampleProjects;

                if (sampleSection) {
                    sampleSection.style.display = contracts.length > 0 ? 'none' : 'block';
                }

                contractsTable.innerHTML = displayContracts.map(contract => `
                    <tr>
                        <td>${contract.id}</td>
                        <td>${contract.property || 'N/A'}</td>
                        <td><span class="badge bg-${contract.status === 'Active' ? 'success' : 'info'}">${contract.status}</span></td>
                        <td>${contract.value || 'N/A'}</td>
                        <td>${contract.created || 'N/A'}</td>
                        <td>
                            <button class="btn btn-sm btn-primary">View</button>
                            <button class="btn btn-sm btn-secondary">Export</button>
                        </td>
                    </tr>
                `).join('');
            })
            .catch(error => console.error('Error fetching contracts:', error));
    }
}

// Unified form handling
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUpload);
    }

    if (document.getElementById('contractsChart')) {
        initializeCharts();
    }
});

// Add budget split field
function addBudgetSplit() {
    const container = document.getElementById('budgetSplits');
    if (container) {
        const newSplit = document.createElement('div');
        newSplit.className = 'input-group mb-2';
        newSplit.innerHTML = `
            <span class="input-group-text"><i class="bi bi-person"></i></span>
            <input type="text" class="form-control" placeholder="Role" name="roles[]">
            <input type="number" class="form-control" placeholder="%" name="percentages[]" min="0" max="100">
            <button type="button" class="btn btn-outline-danger" onclick="this.parentElement.remove()">
                <i class="bi bi-trash"></i>
            </button>
        `;
        container.appendChild(newSplit);
    }
}

// Handle file upload and contract creation
async function handleUpload(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const statusDiv = document.getElementById('uploadStatus');

    try {
        // First upload the file
        const uploadResponse = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const uploadResult = await uploadResponse.json();
        if (uploadResult.error) throw new Error(uploadResult.error);

        // Then create the contract
        const budgetSplits = {};
        formData.getAll('roles[]').forEach((role, i) => {
            const percentage = formData.getAll('percentages[]')[i];
            if (role && percentage) {
                budgetSplits[role] = parseFloat(percentage);
            }
        });

        const tokenizeResponse = await fetch('/api/tokenize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_path: uploadResult.file_path,
                budget_splits: budgetSplits
            })
        });

        const tokenizeResult = await tokenizeResponse.json();
        if (tokenizeResult.error) throw new Error(tokenizeResult.error);

        showSuccess('Contract created successfully!');
        setTimeout(() => window.location.href = '/contracts', 1500);
    } catch (error) {
        showError(error.message || 'An error occurred during upload');
    }
}

// Utility functions
function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        <i class="bi bi-exclamation-triangle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container')?.prepend(alert);
}

function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.innerHTML = `
        <i class="bi bi-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container')?.prepend(alert);
}