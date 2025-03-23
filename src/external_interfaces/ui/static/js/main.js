// Initialize charts and data
function initializeCharts() {
    const ctx = document.getElementById('contractsChart')?.getContext('2d');
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Pending Signatures', 'Active', 'Completed'],
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
                        position: 'bottom',
                        align: 'center'
                    }
                }
            }
        });
    }

    updateDashboardStats();
    updateRecentActivity();
    updateContractsTable();
}

// Update dashboard statistics
function updateDashboardStats() {
    fetch('/api/contracts')
        .then(response => response.json())
        .then(contracts => {
            const stats = {
                total: contracts.length,
                active: 0,
                pendingSignatures: 0,
                completed: 0
            };

            contracts.forEach(contract => {
                switch (contract.status) {
                    case 'completed':
                        stats.completed++;
                        break;
                    case 'pending_signatures':
                        stats.pendingSignatures++;
                        break;
                    case 'active':
                        stats.active++;
                        break;
                }
            });

            // Update chart
            const ctx = document.getElementById('contractsChart')?.getContext('2d');
            if (ctx) {
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Pending Signatures', 'Active', 'Completed'],
                        datasets: [{
                            data: [stats.pendingSignatures, stats.active, stats.completed],
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

            // Update stats display
            const elements = {
                totalContracts: document.getElementById('totalContracts'),
                activeContracts: document.getElementById('activeContracts')
            };

            if (elements.totalContracts) {
                elements.totalContracts.textContent = stats.total;
            }
            if (elements.activeContracts) {
                elements.activeContracts.textContent = stats.active + stats.pendingSignatures;
            }
        })
        .catch(console.error);
}

// Update recent activity section with proper formatting
function updateRecentActivity() {
    const activityTable = document.querySelector('#recentTransactions tbody');
    if (!activityTable) return;

    fetch('/api/contracts')
        .then(response => response.json())
        .then(contracts => {
            if (!contracts || contracts.length === 0) {
                activityTable.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center text-muted">No recent transactions</td>
                    </tr>
                `;
                return;
            }

            // Sort by creation date (newest first)
            contracts.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

            // Take most recent 5
            const recentContracts = contracts.slice(0, 5);

            activityTable.innerHTML = recentContracts.map(contract => `
                <tr>
                    <td>${contract.transaction_id}</td>
                    <td>
                        <span class="badge bg-${getStatusBadgeColor(contract.status)}">
                            ${contract.status}
                        </span>
                    </td>
                    <td>${formatValue(contract.metadata?.network?.amount || '0')}</td>
                    <td>${formatDate(contract.created_at)}</td>
                </tr>
            `).join('');
        })
        .catch(error => {
            console.error('Error fetching recent activity:', error);
            activityTable.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-danger">
                        Error loading recent transactions
                    </td>
                </tr>
            `;
        });
}

// Helper function to format values
function formatValue(amount) {
    const value = parseInt(amount) / 1000000; // Convert from uodis to ODIS
    return `$${value.toFixed(2)}`;
}

// Helper function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Update contracts table with proper spacing
function updateContractsTable() {
    const contractsTable = document.querySelector('#contractsTable tbody');
    const sampleSection = document.getElementById('sampleProjectsSection');
    if (!contractsTable) return;

    fetch('/api/contracts')
        .then(response => response.json())
        .then(contracts => {
            if (sampleSection) {
                sampleSection.style.display = contracts.length > 0 ? 'none' : 'block';
            }

            contractsTable.innerHTML = contracts.map(contract => `
                <tr>
                    <td class="align-middle">
                        ${contract.transaction_id}
                        ${contract.blockchain_tx_hash ? `
                            <a href="${contract.explorer_url}" target="_blank" class="ms-2">
                                <i class="bi bi-box-arrow-up-right"></i>
                            </a>
                        ` : ''}
                    </td>
                    <td class="align-middle">${contract.metadata?.file_path || 'N/A'}</td>
                    <td class="align-middle">
                        <span class="badge bg-${getStatusBadgeColor(contract.status)}">
                            ${contract.status}
                        </span>
                    </td>
                    <td class="align-middle">${formatBudgetSplits(contract.metadata?.budget_splits)}</td>
                    <td class="align-middle">${new Date(contract.created_at).toLocaleDateString()}</td>
                    <td class="align-middle">
                        <div class="btn-group">
                            <button class="btn btn-sm btn-primary" onclick="viewContract('${contract.transaction_id}')">View</button>
                            <button class="btn btn-sm btn-success" onclick="signContract('${contract.transaction_id}')" 
                                ${contract.status === 'completed' ? 'disabled' : ''}>
                                Sign
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        })
        .catch(error => {
            console.error('Error fetching contracts:', error);
            showError('Failed to load contracts');
        });
}

// Helper functions for contract display
function getStatusBadgeColor(status) {
    switch (status) {
        case 'completed':
            return 'success';
        case 'pending_signatures':
            return 'warning';
        default:
            return 'secondary';
    }
}

function formatBudgetSplits(splits) {
    if (!splits) return 'N/A';
    return Object.entries(splits)
        .map(([role, percentage]) => `${role}: ${percentage}%`)
        .join(', ');
}

// Contract interaction functions
async function viewContract(transactionId) {
    try {
        const response = await fetch(`/api/transaction/${transactionId}`);
        const contract = await response.json();

        // Create modal to show contract details
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Contract Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <dl>
                            <dt>Transaction ID</dt>
                            <dd>${contract.transaction_id}</dd>
                            <dt>Content Hash</dt>
                            <dd>${contract.content_hash}</dd>
                            <dt>Created</dt>
                            <dd>${new Date(contract.created_at).toLocaleString()}</dd>
                            <dt>Signatures</dt>
                            <dd>
                                ${Object.entries(contract.signatures).map(([role, status]) =>
                                    `<div>${role}: <span class="badge bg-${status === 'signed' ? 'success' : 'warning'}">${status}</span></div>`
                                ).join('')}
                            </dd>
                            <dt>Explorer URL</dt>
                            <dd>${contract.explorer_url || 'N/A'}</dd>

                        </dl>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        new bootstrap.Modal(modal).show();
        modal.addEventListener('hidden.bs.modal', () => modal.remove());
    } catch (error) {
        showError('Failed to load contract details');
    }
}

async function signContract(transactionId) {
    try {
        // In test mode, we'll simulate signing as each role in sequence
        const roles = ['owner', 'contributor', 'validator'];
        const currentSignatures = (await (await fetch(`/api/transaction/${transactionId}`)).json()).signatures;

        // Find the next unsigned role
        const nextRole = Object.entries(currentSignatures)
            .find(([_, status]) => status !== 'signed')?.[0];

        if (!nextRole) {
            showSuccess('Contract is already fully signed');
            return;
        }

        const response = await fetch('/api/sign', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                transaction_id: transactionId,
                role: nextRole,
                signature: 'test_signature'
            })
        });

        const result = await response.json();
        if (result.error) throw new Error(result.error);

        showSuccess(`Successfully signed as ${nextRole}`);
        updateContractsTable();
        updateDashboardStats();
        updateRecentActivity();
    } catch (error) {
        showError(error.message || 'Failed to sign contract');
    }
}

// File upload handling
async function handleUpload(e) {
    e.preventDefault();

    // Ensure wallet is connected
    if (!window.keplerWallet?.isConnected()) {
        alert('Please connect your wallet first');
        return;
    }

    const formData = new FormData(e.target);
    const statusDiv = document.getElementById('uploadStatus');
    const contractPreview = document.getElementById('contractPreview');

    try {
        if (statusDiv) {
            statusDiv.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-arrow-repeat spin"></i> Uploading file...
                </div>
            `;
        }

        // First upload the file and get tokenization response in one request
        const uploadResponse = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            throw new Error(`Upload failed: ${uploadResponse.status}`);
        }

        const uploadResult = await uploadResponse.json();
        if (uploadResult.error) throw new Error(uploadResult.error);

        handleUploadSuccess(uploadResult);

    } catch (error) {
        console.error('Upload error:', error);
        if (statusDiv) {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i> ${error.message || 'An error occurred during upload'}
                </div>
            `;
        }
    }
}

// Handle successful upload
async function handleUploadSuccess(result) {
    // Update UI immediately
    updateDashboardStats();
    updateRecentActivity();
    updateContractsTable();

    // Store transaction ID in session storage for contracts page
    if (result.transaction) {
        sessionStorage.setItem('last_transaction', JSON.stringify(result.transaction));
        // Redirect to contracts page after successful creation
        setTimeout(() => window.location.href = '/contracts', 1500);
    }
}

// Budget split field management
function addBudgetSplit() {
    const container = document.getElementById('budgetSplits');
    if (!container) return;

    const newSplit = document.createElement('div');
    newSplit.className = 'input-group mb-2';
    newSplit.innerHTML = `
        <span class="input-group-text"><i class="bi bi-person"></i></span>
        <input type="text" class="form-control" placeholder="Role" name="roles[]" required>
        <input type="number" class="form-control" placeholder="%" name="percentages[]" min="0" max="100" required>
        <button type="button" class="btn btn-outline-danger" onclick="this.parentElement.remove()">
            <i class="bi bi-trash"></i>
        </button>
    `;
    container.appendChild(newSplit);
}

// Utility functions for alerts
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


// Update the contract display logic
function updateContractsDisplay() {
    // Check for newly created transaction
    const lastTransaction = sessionStorage.getItem('last_transaction');
    if (lastTransaction) {
        const transaction = JSON.parse(lastTransaction);
        // Clear the stored transaction
        sessionStorage.removeItem('last_transaction');
        // Highlight the new transaction in the table
        highlightTransaction(transaction.transaction_id);
    }

    // Update all contract displays
    updateDashboardStats();
    updateRecentActivity();
    updateContractsTable();
}

function highlightTransaction(transactionId) {
    setTimeout(() => {
        const row = document.querySelector(`tr[data-transaction-id="${transactionId}"]`);
        if (row) {
            row.classList.add('highlight');
            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => row.classList.remove('highlight'), 3000);
        }
    }, 500);
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Handle file upload form
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUpload);
    }

    // Initialize contracts display if on contracts page
    if (document.getElementById('contractsChart')) {
        updateContractsDisplay();
        // Refresh data every 30 seconds
        setInterval(updateContractsDisplay, 30000);
    }
});