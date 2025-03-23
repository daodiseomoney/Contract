// Initialize charts and data
function initializeCharts() {
    const ctx = document.getElementById('contractsChart')?.getContext('2d');
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Pending Signatures', 'Active', 'Completed'],
                datasets: [{
                    data: [0, 0, 0], // Will be updated by updateDashboardStats
                    backgroundColor: [
                        'rgba(255, 193, 7, 0.8)',  // warning yellow for pending
                        'rgba(40, 167, 69, 0.8)',  // success green for active
                        'rgba(23, 162, 184, 0.8)'  // info blue for completed
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

            // Update chart if it exists
            const chart = Chart.getChart('contractsChart');
            if (chart) {
                chart.data.datasets[0].data = [
                    stats.pendingSignatures,
                    stats.active,
                    stats.completed
                ];
                chart.update();
            }

            // Update stats display
            const elements = {
                totalContracts: document.getElementById('totalContracts'),
                activeContracts: document.getElementById('activeContracts'),
                valueLocked: document.getElementById('valueLocked')
            };

            if (elements.totalContracts) {
                elements.totalContracts.textContent = stats.total;
            }
            if (elements.activeContracts) {
                elements.activeContracts.textContent = stats.active;
            }
            if (elements.valueLocked) {
                const totalValue = contracts.reduce((sum, contract) => {
                    const amount = parseInt(contract.metadata?.network?.amount || '0');
                    return sum + amount;
                }, 0);
                elements.valueLocked.textContent = formatValue(totalValue.toString());
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
    if (!contractsTable) return;

    fetch('/api/contracts')
        .then(response => response.json())
        .then(contracts => {
            if (!contracts || contracts.length === 0) {
                contractsTable.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">No contracts found</td>
                    </tr>
                `;
                return;
            }

            contractsTable.innerHTML = contracts.map(contract => {
                const isNew = sessionStorage.getItem('last_transaction') && 
                    JSON.parse(sessionStorage.getItem('last_transaction')).transaction_id === contract.transaction_id;

                return `
                    <tr class="${isNew ? 'table-info' : ''}">
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
                        <td class="align-middle">${formatDate(contract.created_at)}</td>
                        <td class="align-middle">
                            <div class="btn-group">
                                <button class="btn ${isNew ? 'btn-info' : 'btn-primary'}" onclick="viewContract('${contract.transaction_id}')">
                                    <i class="bi bi-search"></i> View Details
                                </button>
                                <button class="btn btn-success" onclick="signContract('${contract.transaction_id}')" 
                                    ${contract.status === 'completed' ? 'disabled' : ''}>
                                    <i class="bi bi-pen"></i> Sign
                                </button>
                            </div>
                            ${isNew ? `
                                <div class="mt-1">
                                    <small class="text-info">
                                        <i class="bi bi-info-circle"></i> Click View Details to see blockchain information
                                    </small>
                                </div>
                            ` : ''}
                        </td>
                    </tr>
                `;
            }).join('');

            // Clear the new transaction flag after showing it
            if (sessionStorage.getItem('last_transaction')) {
                sessionStorage.removeItem('last_transaction');
            }
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
        case 'active':
            return 'primary';
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
// Update viewContract function with improved cleanup
async function viewContract(transactionId) {
    try {
        const response = await fetch(`/api/transaction/${transactionId}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch contract: ${response.status}`);
        }

        const contract = await response.json();
        if (!contract) {
            throw new Error('No contract data received');
        }

        // Remove any existing modals and backdrops
        document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
        document.querySelectorAll('.modal').forEach(el => el.remove());

        // Create modal with improved UI
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'contractDetailsModal';
        modal.setAttribute('data-bs-backdrop', 'static'); // Prevent closing on outside click
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-dark text-white">
                        <h5 class="modal-title">
                            <i class="bi bi-file-earmark-text me-2"></i>
                            Contract Details
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Transaction Status Banner -->
                        <div class="alert ${contract.status === 'completed' ? 'alert-success' : 'alert-info'} d-flex align-items-center mb-4">
                            <i class="bi ${contract.status === 'completed' ? 'bi-check-circle' : 'bi-info-circle'} me-2"></i>
                            <div>
                                <strong>Transaction Status:</strong>
                                <span class="badge bg-${getStatusBadgeColor(contract.status)} ms-2">
                                    ${contract.status.toUpperCase()}
                                </span>
                            </div>
                        </div>

                        <!-- Main Details -->
                        <div class="card mb-4">
                            <div class="card-header">
                                <h6 class="mb-0">Transaction Information</h6>
                            </div>
                            <div class="card-body">
                                <dl class="row mb-0">
                                    <dt class="col-sm-4">Transaction ID</dt>
                                    <dd class="col-sm-8">
                                        <code class="user-select-all">${contract.transaction_id}</code>
                                    </dd>

                                    <dt class="col-sm-4">Content Hash</dt>
                                    <dd class="col-sm-8">
                                        <code class="user-select-all">${contract.content_hash}</code>
                                        <button class="btn btn-sm btn-outline-secondary ms-2" onclick="navigator.clipboard.writeText('${contract.content_hash}')">
                                            <i class="bi bi-clipboard"></i>
                                        </button>
                                    </dd>

                                    <dt class="col-sm-4">Blockchain Tx Hash</dt>
                                    <dd class="col-sm-8">
                                        ${contract.blockchain_tx_hash ? 
                                            `<div class="d-flex align-items-center">
                                                <code class="user-select-all">${contract.blockchain_tx_hash}</code>
                                                <button class="btn btn-sm btn-outline-secondary ms-2" onclick="navigator.clipboard.writeText('${contract.blockchain_tx_hash}')">
                                                    <i class="bi bi-clipboard"></i>
                                                </button>
                                            </div>` : 
                                            '<span class="text-warning"><i class="bi bi-clock-history"></i> Pending...</span>'}
                                    </dd>

                                    <dt class="col-sm-4">Explorer Link</dt>
                                    <dd class="col-sm-8">
                                        ${contract.explorer_url ? 
                                            `<a href="${contract.explorer_url}" target="_blank" class="btn btn-sm btn-primary">
                                                <i class="bi bi-box-arrow-up-right"></i> View on Odiseo Explorer
                                            </a>` : 
                                            '<span class="text-muted"><i class="bi bi-clock-history"></i> Not available yet</span>'}
                                    </dd>

                                    <dt class="col-sm-4">Created</dt>
                                    <dd class="col-sm-8">${formatDate(contract.created_at)}</dd>
                                </dl>
                            </div>
                        </div>

                        <!-- Signatures Section -->
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">Signature Status</h6>
                            </div>
                            <div class="card-body">
                                <div class="d-flex flex-column gap-2">
                                    ${Object.entries(contract.signatures).map(([role, status]) => `
                                        <div class="d-flex align-items-center justify-content-between border-bottom pb-2">
                                            <div class="d-flex align-items-center">
                                                <i class="bi bi-person-circle me-2"></i>
                                                <span class="text-capitalize">${role}</span>
                                            </div>
                                            <span class="badge bg-${status === 'signed' ? 'success' : 'warning'}">
                                                ${status === 'signed' ? 
                                                    '<i class="bi bi-check-circle me-1"></i> Signed' : 
                                                    '<i class="bi bi-clock me-1"></i> Pending'}
                                            </span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        ${contract.status !== 'completed' ? 
                            `<button type="button" class="btn btn-primary" onclick="signContract('${contract.transaction_id}')">
                                <i class="bi bi-pen"></i> Sign Contract
                            </button>` : ''}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const modalInstance = new bootstrap.Modal(modal);

        // Setup proper cleanup on modal hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modalInstance.dispose();
            modal.remove();
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
        });

        modalInstance.show();
    } catch (error) {
        console.error('Error viewing contract:', error);
        showError(`Failed to load contract details: ${error.message}`);
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
    if (result.transaction) {
        // Store transaction ID in session storage
        sessionStorage.setItem('last_transaction', JSON.stringify(result.transaction));

        // Update all displays immediately before redirect
        updateDashboardStats();
        updateRecentActivity();
        updateContractsTable();

        // Redirect to contracts page after short delay
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


// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Handle file upload form
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUpload);
    }

    // Initialize contracts display if on contracts page
    if (document.getElementById('contractsChart')) {
        initializeCharts();
        // Refresh data every 30 seconds
        setInterval(updateDashboardStats, 30000);
        setInterval(updateRecentActivity, 30000);
        setInterval(updateContractsTable, 30000);
    }
});