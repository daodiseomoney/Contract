/**
 * Contracts.js - Handle contract data display and interaction
 * This file connects the contracts UI with the backend data
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize contracts page functionality
    if (document.getElementById('contractsTableBody')) {
        loadContracts();
    }

    // Add event listener for new contract button
    const newContractBtn = document.getElementById('newContractBtn');
    if (newContractBtn) {
        newContractBtn.addEventListener('click', function() {
            // Open new contract modal or show form
            alert('New contract functionality will be implemented here');
            // Future implementation: showNewContractForm();
        });
    }

    // Initialize contract charts if they exist
    if (document.getElementById('distribution-chart')) {
        initializeContractCharts();
    }
});

/**
 * Load contracts from the API
 */
function loadContracts() {
    const contractsTableBody = document.getElementById('contractsTableBody');
    if (!contractsTableBody) return;
    
    // Show loading state
    contractsTableBody.innerHTML = '<tr><td colspan="8" class="text-center">Loading contracts...</td></tr>';
    
    // Fetch contracts from the API
    fetch('/api/contracts')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(contracts => {
            if (contracts.length === 0) {
                contractsTableBody.innerHTML = '<tr><td colspan="8" class="text-center">No contracts found</td></tr>';
                return;
            }
            
            // Clear loading state
            contractsTableBody.innerHTML = '';
            
            // Populate the table with contract data
            contracts.forEach(contract => {
                const row = createContractRow(contract);
                contractsTableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching contracts:', error);
            contractsTableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">Error loading contracts: ${error.message}</td></tr>`;
        });
}

/**
 * Create a table row for a contract
 * @param {Object} contract - Contract data object
 * @returns {HTMLTableRowElement} - Table row element
 */
function createContractRow(contract) {
    const row = document.createElement('tr');
    
    // Format status badge
    const statusBadge = getStatusBadge(contract.status || 'pending');
    
    // Format due diligence state
    const dueDiligence = getDueDiligenceState(contract.due_diligence_status || 'incomplete');
    
    // Format date
    const createdDate = formatDate(contract.created_at || new Date().toISOString());
    
    row.innerHTML = `
        <td><a href="#" class="contract-link" data-contract-id="${contract.id}">${contract.id}</a></td>
        <td>${contract.property || 'Unknown Property'}</td>
        <td>${contract.token_symbol || 'N/A'}</td>
        <td>$${formatNumber(contract.value || 0)}</td>
        <td>${statusBadge}</td>
        <td>${dueDiligence}</td>
        <td>${createdDate}</td>
        <td>
            <div class="btn-group">
                <button type="button" class="btn btn-sm btn-outline-info view-contract" data-contract-id="${contract.id}">
                    <i data-feather="eye" class="icon-inline-sm"></i>
                </button>
                <button type="button" class="btn btn-sm btn-outline-secondary" disabled>
                    <i data-feather="edit-2" class="icon-inline-sm"></i>
                </button>
                <button type="button" class="btn btn-sm btn-outline-info sign-contract" data-contract-id="${contract.id}">
                    <i data-feather="key" class="icon-inline-sm"></i>
                </button>
            </div>
        </td>
    `;
    
    // Initialize Feather icons
    if (window.feather) {
        feather.replace(row.querySelectorAll('[data-feather]'));
    }
    
    // Add click handlers
    const viewButtons = row.querySelectorAll('.view-contract, .contract-link');
    viewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const contractId = this.getAttribute('data-contract-id');
            viewContractDetails(contractId);
        });
    });
    
    const signButtons = row.querySelectorAll('.sign-contract');
    signButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const contractId = this.getAttribute('data-contract-id');
            signContract(contractId);
        });
    });
    
    return row;
}

/**
 * View contract details
 * @param {string} contractId - Contract ID
 */
function viewContractDetails(contractId) {
    // Fetch contract details from API
    fetch(`/api/contracts/${contractId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(contract => {
            updateContractDetailsSection(contract);
        })
        .catch(error => {
            console.error(`Error fetching contract ${contractId}:`, error);
            showAlert(`Error loading contract details: ${error.message}`, 'danger');
        });
}

/**
 * Update the contract details section with contract data
 * @param {Object} contract - Contract data object
 */
function updateContractDetailsSection(contract) {
    // Update contract header
    const contractTitle = document.querySelector('.contract-title');
    if (contractTitle) {
        contractTitle.innerHTML = `${contract.property || 'Unnamed Contract'} <span class="badge bg-${getStatusColor(contract.status || 'pending')} ms-2">${contract.verified ? 'VERIFIED' : 'UNVERIFIED'}</span>`;
    }
    
    const contractId = document.querySelector('.contract-id');
    if (contractId) {
        contractId.textContent = `Contract ID: ${contract.id} (${contract.wallet_address || 'No Address'})`;
    }
    
    const contractStatus = document.querySelector('.contract-status');
    if (contractStatus) {
        contractStatus.textContent = contract.status || 'Pending';
        contractStatus.className = `contract-status status-${contract.status?.toLowerCase() || 'pending'}`;
    }
    
    // Update contract meta info
    updateContractMetaInfo(contract);
    
    // Update contract description
    const contractDesc = document.querySelector('.contract-content p');
    if (contractDesc) {
        contractDesc.textContent = contract.description || 'No description available.';
    }
    
    // Update due diligence information
    updateDueDiligenceInfo(contract.due_diligence || {});
    
    // Update chart data
    if (window.contractChart) {
        updateContractChart(contract);
    }
    
    // Show contract details section
    const contractDetails = document.querySelector('.contract-details');
    if (contractDetails) {
        contractDetails.style.display = 'block';
        scrollToElement(contractDetails);
    }
}

/**
 * Update the contract meta information
 * @param {Object} contract - Contract data object
 */
function updateContractMetaInfo(contract) {
    // Meta values mapping
    const metaMapping = {
        'Token Symbol': contract.token_symbol || 'N/A',
        'Total Value': `$${formatNumber(contract.value || 0)}`,
        'Token Supply': `${formatNumber(contract.token_supply || 0)} ${contract.token_symbol || ''}`,
        'Current Token Price': `$${(contract.value / contract.token_supply || 0).toFixed(2)}`,
        'Creation Date': formatDate(contract.created_at || new Date().toISOString()),
        'Blockchain': contract.blockchain || 'Odiseo Testnet'
    };
    
    // Update all meta values
    document.querySelectorAll('.meta-label').forEach(label => {
        const key = label.textContent.trim();
        if (metaMapping[key]) {
            const valueElement = label.nextElementSibling;
            if (valueElement && valueElement.classList.contains('meta-value')) {
                valueElement.textContent = metaMapping[key];
            }
        }
    });
}

/**
 * Update due diligence information
 * @param {Object} dueDiligence - Due diligence data object
 */
function updateDueDiligenceInfo(dueDiligence) {
    const dueDiligenceItems = {
        'IFC File Validation': dueDiligence.ifc_validation || 'incomplete',
        'Legal Document Review': dueDiligence.legal_review || 'incomplete',
        'Validator Approval': dueDiligence.validator_approval || 'incomplete',
        'SPV Formation': dueDiligence.spv_formation || 'incomplete',
        'KYC Verification': dueDiligence.kyc_verification || 'incomplete'
    };
    
    // Update status for each due diligence item
    document.querySelectorAll('.list-group-item').forEach(item => {
        const label = item.querySelector('span:first-child')?.textContent.trim();
        if (label && dueDiligenceItems[label]) {
            const status = dueDiligenceItems[label];
            const badge = item.querySelector('.badge');
            if (badge) {
                badge.textContent = status === 'complete' ? 'Complete' : 'Pending';
                badge.className = `badge ${status === 'complete' ? 'bg-success' : 'bg-warning'} rounded-pill`;
            }
        }
    });
}

/**
 * Sign a contract using Keplr wallet
 * @param {string} contractId - Contract ID
 */
function signContract(contractId) {
    // Check if Keplr wallet is available
    if (!window.keplr) {
        showAlert('Please install Keplr extension to sign contracts', 'warning');
        return;
    }
    
    showAlert('Preparing to sign contract...', 'info');
    
    // Fetch contract details to prepare signature
    fetch(`/api/contracts/${contractId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(contract => {
            // Here we would integrate with Keplr wallet signing process
            // For now, show a message about the functionality
            showAlert('Signing functionality will be implemented with Keplr wallet integration', 'info');
        })
        .catch(error => {
            console.error(`Error preparing contract ${contractId} for signing:`, error);
            showAlert(`Error preparing contract for signing: ${error.message}`, 'danger');
        });
}

/**
 * Initialize contract charts
 */
function initializeContractCharts() {
    const distributionChart = document.getElementById('distribution-chart');
    if (!distributionChart) return;
    
    // Sample data - will be replaced with API data
    const data = {
        labels: ['Investors', 'Developers', 'Property Manager', 'Reserve'],
        datasets: [{
            data: [45, 30, 15, 10],
            backgroundColor: ['#36a2eb', '#ff6384', '#4bc0c0', '#ffcd56'],
            borderWidth: 0
        }]
    };
    
    // Create the chart
    window.contractChart = new Chart(distributionChart, {
        type: 'pie',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                position: 'bottom',
                labels: {
                    fontColor: '#ced4da',
                    boxWidth: 15
                }
            }
        }
    });
}

/**
 * Update contract chart with data
 * @param {Object} contract - Contract data object
 */
function updateContractChart(contract) {
    // Get distribution data from contract
    const distribution = contract.distribution || {
        'Investors': 45,
        'Developers': 30,
        'Property Manager': 15,
        'Reserve': 10
    };
    
    // Update chart data
    window.contractChart.data.labels = Object.keys(distribution);
    window.contractChart.data.datasets[0].data = Object.values(distribution);
    window.contractChart.update();
}

/**
 * Get status badge HTML
 * @param {string} status - Contract status
 * @returns {string} - HTML for the status badge
 */
function getStatusBadge(status) {
    const statusMap = {
        'active': { text: 'Active', color: 'success' },
        'pending': { text: 'Pending', color: 'warning' },
        'expired': { text: 'Expired', color: 'danger' },
        'default': { text: status.charAt(0).toUpperCase() + status.slice(1), color: 'secondary' }
    };
    
    const statusInfo = statusMap[status.toLowerCase()] || statusMap.default;
    return `<span class="badge bg-${statusInfo.color}">${statusInfo.text}</span>`;
}

/**
 * Get status color
 * @param {string} status - Contract status
 * @returns {string} - Bootstrap color class
 */
function getStatusColor(status) {
    const colorMap = {
        'active': 'success',
        'pending': 'warning',
        'expired': 'danger'
    };
    
    return colorMap[status.toLowerCase()] || 'secondary';
}

/**
 * Get due diligence state HTML
 * @param {string} state - Due diligence state
 * @returns {string} - HTML for the due diligence state
 */
function getDueDiligenceState(state) {
    const stateMap = {
        'complete': { text: 'Complete', color: 'success' },
        'in_progress': { text: 'In Progress', color: 'warning' },
        'incomplete': { text: 'Incomplete', color: 'secondary' },
        'default': { text: state.charAt(0).toUpperCase() + state.slice(1).replace('_', ' '), color: 'info' }
    };
    
    const stateInfo = stateMap[state.toLowerCase()] || stateMap.default;
    return `<span class="badge bg-${stateInfo.color}">${stateInfo.text}</span>`;
}

/**
 * Format a number with commas
 * @param {number} num - Number to format
 * @returns {string} - Formatted number
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Format a date string
 * @param {string} dateStr - ISO date string
 * @returns {string} - Formatted date string
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Scroll to an element
 * @param {HTMLElement} element - Element to scroll to
 */
function scrollToElement(element) {
    window.scrollTo({
        top: element.offsetTop - 20,
        behavior: 'smooth'
    });
}

/**
 * Show an alert message
 * @param {string} message - The message to display
 * @param {string} type - Alert type (success, danger, warning, info)
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    // Create alert element
    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${type} alert-dismissible fade show`;
    alertEl.role = 'alert';
    
    // Add message text
    alertEl.textContent = message;
    
    // Add dismiss button
    const dismissButton = document.createElement('button');
    dismissButton.type = 'button';
    dismissButton.className = 'btn-close';
    dismissButton.setAttribute('data-bs-dismiss', 'alert');
    dismissButton.setAttribute('aria-label', 'Close');
    alertEl.appendChild(dismissButton);
    
    // Add to container
    alertContainer.appendChild(alertEl);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertEl.parentNode) {
            const bsAlert = new bootstrap.Alert(alertEl);
            bsAlert.close();
        }
    }, 5000);
}