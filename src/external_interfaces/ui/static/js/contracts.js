/**
 * Contracts JavaScript for the Daodiseo Real Estate Tokenization Platform
 * Handles displaying and interacting with smart contracts
 */

// Initialize contracts components when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize contracts data
    initContractsData();
    
    // Initialize contracts filtering and search
    initContractsFiltering();
    
    // Initialize contract interaction buttons
    initContractButtons();
});

// Load contracts data from API
async function initContractsData() {
    try {
        // Fetch contracts from API
        const contracts = await fetchApi('/api/contracts');
        
        // Display contracts in UI
        displayContracts(contracts);
        
        // Initialize transaction history if available
        const transactionElements = document.querySelectorAll('.transactions-table');
        if (transactionElements.length > 0) {
            // Fetch recent transactions
            const transactions = await fetchApi('/api/transactions');
            
            // Display transactions
            displayTransactions(transactions);
        }
        
    } catch (error) {
        console.error('Error initializing contracts data:', error);
        showAlert('Failed to load contracts data. Please try again later.', 'warning');
    }
}

// Display contracts in UI
function displayContracts(contracts) {
    const contractsContainer = document.querySelector('.contracts-grid');
    if (!contractsContainer) return;
    
    // Clear loading state or placeholder
    contractsContainer.innerHTML = '';
    
    if (contracts.length === 0) {
        // Display empty state
        contractsContainer.innerHTML = `
            <div class="empty-state text-center py-5">
                <i data-feather="file-text" class="text-muted mb-3" style="width: 48px; height: 48px;"></i>
                <h5 class="text-muted">No Contracts Found</h5>
                <p class="text-muted small">Connect your wallet and upload a BIM model to create your first contract.</p>
            </div>
        `;
        feather.replace();
        return;
    }
    
    // Create contract cards for each contract
    contracts.forEach(contract => {
        const card = createContractCard(contract);
        contractsContainer.appendChild(card);
    });
    
    // Update feather icons in new content
    feather.replace();
}

// Create a contract card element
function createContractCard(contract) {
    const cardElement = document.createElement('div');
    cardElement.className = 'contract-card';
    cardElement.setAttribute('data-contract-id', contract.id);
    cardElement.setAttribute('data-contract-type', contract.type);
    cardElement.setAttribute('data-contract-status', contract.status);
    
    // Format funding progress percentage
    const fundingProgress = contract.funded_amount / contract.total_amount * 100;
    
    // Format verification badge based on status
    let verificationBadge = '';
    if (contract.verified) {
        verificationBadge = '<span class="verification-badge verified" data-bs-toggle="tooltip" title="Verified by Daodiseo validators"><i data-feather="check-circle" class="icon-inline-sm"></i></span>';
    } else {
        verificationBadge = '<span class="verification-badge unverified" data-bs-toggle="tooltip" title="Awaiting verification"><i data-feather="clock" class="icon-inline-sm"></i></span>';
    }
    
    // Format tokenization status badge
    let tokenizationBadge = '';
    if (contract.tokenized) {
        tokenizationBadge = '<span class="status-badge tokenized">Tokenized</span>';
    } else if (contract.status === 'pending') {
        tokenizationBadge = '<span class="status-badge pending">Pending</span>';
    } else {
        tokenizationBadge = '<span class="status-badge processing">Processing</span>';
    }
    
    // Card HTML template
    cardElement.innerHTML = `
        <div class="card bg-dark border-info mb-4">
            <div class="card-header border-info d-flex justify-content-between align-items-center">
                <h5 class="card-title mb-0 d-flex align-items-center">
                    ${verificationBadge}
                    ${contract.name}
                </h5>
                ${tokenizationBadge}
            </div>
            <div class="card-body">
                <div class="property-details mb-3">
                    <div class="property-location d-flex align-items-center mb-2">
                        <i data-feather="map-pin" class="icon-inline-sm text-info me-2"></i>
                        <span>${contract.location}</span>
                    </div>
                    <div class="property-type d-flex align-items-center mb-2">
                        <i data-feather="home" class="icon-inline-sm text-info me-2"></i>
                        <span>${contract.type}</span>
                    </div>
                    <div class="property-size d-flex align-items-center">
                        <i data-feather="maximize" class="icon-inline-sm text-info me-2"></i>
                        <span>${formatNumber(contract.size)} sqm</span>
                    </div>
                </div>
                
                <div class="funding-details">
                    <div class="d-flex justify-content-between mb-1">
                        <span class="text-muted">Funding Progress</span>
                        <span class="text-info">${fundingProgress.toFixed(1)}%</span>
                    </div>
                    <div class="progress mb-2 bg-dark">
                        <div class="progress-bar bg-info" role="progressbar" style="width: ${fundingProgress}%" 
                            aria-valuenow="${fundingProgress}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span class="text-muted small">Current</span>
                        <span class="text-muted small">Target</span>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span class="text-light">${formatCurrency(contract.funded_amount)}</span>
                        <span class="text-light">${formatCurrency(contract.total_amount)}</span>
                    </div>
                </div>
                
                <div class="token-details mt-3">
                    <div class="d-flex justify-content-between mb-2">
                        <div>
                            <span class="text-muted small">Token Price</span>
                            <div class="text-light">${formatCurrency(contract.token_price)}</div>
                        </div>
                        <div>
                            <span class="text-muted small">Total Tokens</span>
                            <div class="text-light text-end">${formatNumber(contract.token_count)}</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-footer border-info d-flex justify-content-between">
                <button class="btn btn-sm btn-outline-light view-contract-btn" data-contract-id="${contract.id}">
                    <i data-feather="file-text" class="icon-inline-sm"></i>
                    View Details
                </button>
                <button class="btn btn-sm btn-info invest-btn" data-contract-id="${contract.id}" ${contract.status !== 'active' ? 'disabled' : ''}>
                    <i data-feather="dollar-sign" class="icon-inline-sm"></i>
                    Invest
                </button>
            </div>
        </div>
    `;
    
    return cardElement;
}

// Display transactions in UI
function displayTransactions(transactions) {
    const transactionsTable = document.querySelector('.transactions-table tbody');
    if (!transactionsTable) return;
    
    // Clear loading state or placeholder
    transactionsTable.innerHTML = '';
    
    if (transactions.length === 0) {
        // Display empty state row
        transactionsTable.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-4">
                    <div class="empty-state">
                        <i data-feather="inbox" class="text-muted mb-2" style="width: 32px; height: 32px;"></i>
                        <p class="text-muted mb-0">No transactions found</p>
                    </div>
                </td>
            </tr>
        `;
        feather.replace();
        return;
    }
    
    // Create table rows for each transaction
    transactions.forEach(transaction => {
        const row = createTransactionRow(transaction);
        transactionsTable.appendChild(row);
    });
    
    // Update feather icons in new content
    feather.replace();
}

// Create a transaction row element
function createTransactionRow(transaction) {
    const rowElement = document.createElement('tr');
    
    // Format status badge
    let statusBadge = '';
    switch (transaction.status) {
        case 'completed':
            statusBadge = '<span class="badge rounded-pill bg-success">Completed</span>';
            break;
        case 'pending':
            statusBadge = '<span class="badge rounded-pill bg-warning text-dark">Pending</span>';
            break;
        case 'failed':
            statusBadge = '<span class="badge rounded-pill bg-danger">Failed</span>';
            break;
        default:
            statusBadge = '<span class="badge rounded-pill bg-secondary">Processing</span>';
    }
    
    // Format address
    const fromAddress = truncateAddress(transaction.from_address);
    const toAddress = truncateAddress(transaction.to_address);
    
    // Format date
    const date = new Date(transaction.timestamp * 1000);
    const formattedDate = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    // Row HTML template
    rowElement.innerHTML = `
        <td>
            <div class="tx-hash" data-bs-toggle="tooltip" title="${transaction.tx_hash}">
                <a href="${transaction.explorer_url}" target="_blank" class="text-info">
                    ${truncateAddress(transaction.tx_hash, 8, 8)}
                </a>
            </div>
        </td>
        <td>
            <div class="tx-type d-flex align-items-center">
                <i data-feather="${transaction.tx_type === 'token_transfer' ? 'repeat' : 'upload'}" class="icon-inline-sm text-info me-2"></i>
                ${transaction.tx_type === 'token_transfer' ? 'Token Transfer' : 'Contract Upload'}
            </div>
        </td>
        <td>
            <div class="d-flex align-items-center">
                <span class="me-2">From:</span>
                <a href="#" class="address-link" data-address="${transaction.from_address}">
                    ${fromAddress}
                </a>
            </div>
            <div class="d-flex align-items-center mt-1">
                <span class="me-2">To:</span>
                <a href="#" class="address-link" data-address="${transaction.to_address}">
                    ${toAddress}
                </a>
            </div>
        </td>
        <td>
            <div class="amount">${formatNumber(transaction.amount)} ${transaction.denom}</div>
            <div class="timestamp text-muted small">${formattedDate}</div>
        </td>
        <td>${statusBadge}</td>
    `;
    
    return rowElement;
}

// Initialize contracts filtering functionality
function initContractsFiltering() {
    // Get filter elements
    const filterButtons = document.querySelectorAll('.contract-filter-btn');
    const searchInput = document.querySelector('.contract-search-input');
    
    // Add event listeners to filter buttons
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Get filter value
            const filterValue = this.getAttribute('data-filter');
            
            // Filter contracts
            filterContracts(filterValue, searchInput ? searchInput.value : '');
        });
    });
    
    // Add event listener to search input
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            // Get active filter
            const activeFilter = document.querySelector('.contract-filter-btn.active');
            const filterValue = activeFilter ? activeFilter.getAttribute('data-filter') : 'all';
            
            // Filter contracts
            filterContracts(filterValue, this.value);
        });
    }
}

// Filter contracts based on filter and search values
function filterContracts(filterValue, searchValue) {
    const contractCards = document.querySelectorAll('.contract-card');
    
    contractCards.forEach(card => {
        let showCard = true;
        
        // Apply filter
        if (filterValue !== 'all') {
            const cardType = card.getAttribute('data-contract-type').toLowerCase();
            const cardStatus = card.getAttribute('data-contract-status').toLowerCase();
            
            // Filter by type
            if (filterValue === 'residential' && cardType !== 'residential') {
                showCard = false;
            }
            else if (filterValue === 'commercial' && cardType !== 'commercial') {
                showCard = false;
            }
            else if (filterValue === 'industrial' && cardType !== 'industrial') {
                showCard = false;
            }
            // Filter by status
            else if (filterValue === 'active' && cardStatus !== 'active') {
                showCard = false;
            }
            else if (filterValue === 'pending' && cardStatus !== 'pending') {
                showCard = false;
            }
            else if (filterValue === 'tokenized' && !card.querySelector('.status-badge.tokenized')) {
                showCard = false;
            }
        }
        
        // Apply search
        if (searchValue && showCard) {
            const cardText = card.textContent.toLowerCase();
            if (!cardText.includes(searchValue.toLowerCase())) {
                showCard = false;
            }
        }
        
        // Show or hide card
        card.style.display = showCard ? '' : 'none';
    });
    
    // Show empty state if no contracts visible
    const visibleCards = document.querySelectorAll('.contract-card[style=""]');
    const contractsContainer = document.querySelector('.contracts-grid');
    const emptyState = document.querySelector('.empty-state');
    
    if (visibleCards.length === 0 && contractsContainer) {
        // If empty state doesn't exist, create it
        if (!emptyState) {
            const emptyStateElement = document.createElement('div');
            emptyStateElement.className = 'empty-state text-center py-5 w-100';
            emptyStateElement.innerHTML = `
                <i data-feather="search" class="text-muted mb-3" style="width: 48px; height: 48px;"></i>
                <h5 class="text-muted">No Matching Contracts</h5>
                <p class="text-muted small">Try adjusting your filters or search criteria.</p>
            `;
            contractsContainer.appendChild(emptyStateElement);
            feather.replace();
        } else {
            emptyState.style.display = '';
        }
    } else if (emptyState) {
        emptyState.style.display = 'none';
    }
}

// Initialize contract interaction buttons
function initContractButtons() {
    // Add event listener for view contract details buttons
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('view-contract-btn') || 
            event.target.closest('.view-contract-btn')) {
            
            const button = event.target.classList.contains('view-contract-btn') ? 
                event.target : event.target.closest('.view-contract-btn');
                
            const contractId = button.getAttribute('data-contract-id');
            viewContractDetails(contractId);
        }
        
        // Add event listener for invest buttons
        if (event.target.classList.contains('invest-btn') || 
            event.target.closest('.invest-btn')) {
            
            const button = event.target.classList.contains('invest-btn') ? 
                event.target : event.target.closest('.invest-btn');
                
            const contractId = button.getAttribute('data-contract-id');
            openInvestmentModal(contractId);
        }
    });
}

// View contract details
async function viewContractDetails(contractId) {
    try {
        // Fetch contract details from API
        const contractDetails = await fetchApi(`/api/contracts/${contractId}`);
        
        // Show contract details modal
        showContractDetailsModal(contractDetails);
    } catch (error) {
        console.error('Error fetching contract details:', error);
        showAlert('Failed to load contract details. Please try again later.', 'warning');
    }
}

// Show contract details modal
function showContractDetailsModal(contract) {
    // Create modal element
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'contractDetailsModal';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-labelledby', 'contractDetailsModalLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    // Format funding progress percentage
    const fundingProgress = contract.funded_amount / contract.total_amount * 100;
    
    // Format verification badge based on status
    let verificationBadge = '';
    if (contract.verified) {
        verificationBadge = '<span class="badge bg-success"><i data-feather="check" class="icon-inline-sm"></i> Verified</span>';
    } else {
        verificationBadge = '<span class="badge bg-warning text-dark"><i data-feather="clock" class="icon-inline-sm"></i> Pending</span>';
    }
    
    // Format tokenization status badge
    let tokenizationBadge = '';
    if (contract.tokenized) {
        tokenizationBadge = '<span class="badge bg-info"><i data-feather="link" class="icon-inline-sm"></i> Tokenized</span>';
    } else if (contract.status === 'pending') {
        tokenizationBadge = '<span class="badge bg-warning text-dark"><i data-feather="clock" class="icon-inline-sm"></i> Pending</span>';
    } else {
        tokenizationBadge = '<span class="badge bg-primary"><i data-feather="refresh-cw" class="icon-inline-sm"></i> Processing</span>';
    }
    
    // Modal HTML template
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content bg-dark text-light border-info">
                <div class="modal-header border-info">
                    <h5 class="modal-title" id="contractDetailsModalLabel">
                        ${contract.name}
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="contract-details">
                        <div class="status-badges mb-3">
                            ${verificationBadge} ${tokenizationBadge}
                        </div>
                        
                        <div class="row mb-4">
                            <div class="col-md-6">
                                <h6 class="text-info">Property Details</h6>
                                <div class="property-detail-item d-flex align-items-center mb-2">
                                    <i data-feather="map-pin" class="icon-inline-sm text-info me-2"></i>
                                    <div>
                                        <div class="text-muted small">Location</div>
                                        <div>${contract.location}</div>
                                    </div>
                                </div>
                                <div class="property-detail-item d-flex align-items-center mb-2">
                                    <i data-feather="home" class="icon-inline-sm text-info me-2"></i>
                                    <div>
                                        <div class="text-muted small">Property Type</div>
                                        <div>${contract.type}</div>
                                    </div>
                                </div>
                                <div class="property-detail-item d-flex align-items-center mb-2">
                                    <i data-feather="maximize" class="icon-inline-sm text-info me-2"></i>
                                    <div>
                                        <div class="text-muted small">Size</div>
                                        <div>${formatNumber(contract.size)} sqm</div>
                                    </div>
                                </div>
                                <div class="property-detail-item d-flex align-items-center">
                                    <i data-feather="calendar" class="icon-inline-sm text-info me-2"></i>
                                    <div>
                                        <div class="text-muted small">Listed Date</div>
                                        <div>${new Date(contract.created_at * 1000).toLocaleDateString('en-US', {
                                            year: 'numeric',
                                            month: 'long',
                                            day: 'numeric'
                                        })}</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6 class="text-info">Investment Details</h6>
                                <div class="property-detail-item d-flex align-items-center mb-2">
                                    <i data-feather="dollar-sign" class="icon-inline-sm text-info me-2"></i>
                                    <div>
                                        <div class="text-muted small">Target Amount</div>
                                        <div>${formatCurrency(contract.total_amount)}</div>
                                    </div>
                                </div>
                                <div class="property-detail-item d-flex align-items-center mb-2">
                                    <i data-feather="users" class="icon-inline-sm text-info me-2"></i>
                                    <div>
                                        <div class="text-muted small">Investors</div>
                                        <div>${contract.investor_count || 0}</div>
                                    </div>
                                </div>
                                <div class="property-detail-item d-flex align-items-center mb-2">
                                    <i data-feather="tag" class="icon-inline-sm text-info me-2"></i>
                                    <div>
                                        <div class="text-muted small">Token Price</div>
                                        <div>${formatCurrency(contract.token_price)}</div>
                                    </div>
                                </div>
                                <div class="property-detail-item d-flex align-items-center">
                                    <i data-feather="pie-chart" class="icon-inline-sm text-info me-2"></i>
                                    <div>
                                        <div class="text-muted small">Expected Annual Return</div>
                                        <div>${formatPercentage(contract.expected_return || 0)}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="funding-progress mb-4">
                            <h6 class="text-info">Funding Progress</h6>
                            <div class="d-flex justify-content-between mb-1">
                                <span class="text-muted">Progress</span>
                                <span class="text-info">${fundingProgress.toFixed(1)}%</span>
                            </div>
                            <div class="progress mb-2 bg-dark">
                                <div class="progress-bar bg-info" role="progressbar" style="width: ${fundingProgress}%" 
                                    aria-valuenow="${fundingProgress}" aria-valuemin="0" aria-valuemax="100"></div>
                            </div>
                            <div class="d-flex justify-content-between">
                                <div>
                                    <div class="text-muted small">Current</div>
                                    <div>${formatCurrency(contract.funded_amount)}</div>
                                </div>
                                <div class="text-end">
                                    <div class="text-muted small">Target</div>
                                    <div>${formatCurrency(contract.total_amount)}</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="contract-description mb-4">
                            <h6 class="text-info">Description</h6>
                            <p>${contract.description || 'No description available.'}</p>
                        </div>
                        
                        <div class="blockchain-details">
                            <h6 class="text-info">Blockchain Details</h6>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="blockchain-detail-item mb-2">
                                        <div class="text-muted small">Contract Address</div>
                                        <div class="d-flex align-items-center">
                                            <span class="me-2 text-break">${truncateAddress(contract.contract_address, 12, 8)}</span>
                                            <button class="btn btn-sm btn-outline-info copy-btn" data-copy="${contract.contract_address}">
                                                <i data-feather="copy" class="icon-inline-sm"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="blockchain-detail-item mb-2">
                                        <div class="text-muted small">Token ID</div>
                                        <div class="d-flex align-items-center">
                                            <span class="me-2">${contract.token_id || 'Not tokenized yet'}</span>
                                            ${contract.token_id ? `
                                            <button class="btn btn-sm btn-outline-info copy-btn" data-copy="${contract.token_id}">
                                                <i data-feather="copy" class="icon-inline-sm"></i>
                                            </button>
                                            ` : ''}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer border-info">
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-info invest-modal-btn" data-contract-id="${contract.id}" ${contract.status !== 'active' ? 'disabled' : ''}>
                        <i data-feather="dollar-sign" class="icon-inline-sm"></i>
                        Invest
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.appendChild(modal);
    
    // Initialize modal and show it
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    
    // Update feather icons inside modal
    feather.replace();
    
    // Add event listener for copy buttons
    const copyButtons = modal.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(() => {
                // Show success message
                showAlert('Copied to clipboard!', 'success');
                
                // Change button icon temporarily
                const icon = this.querySelector('svg');
                const originalIcon = icon.outerHTML;
                icon.outerHTML = feather.icons['check'].toSvg({ class: 'icon-inline-sm' });
                
                // Revert icon after 1.5 seconds
                setTimeout(() => {
                    const checkIcon = this.querySelector('svg');
                    checkIcon.outerHTML = originalIcon;
                }, 1500);
            });
        });
    });
    
    // Add event listener for invest button
    const investButton = modal.querySelector('.invest-modal-btn');
    if (investButton) {
        investButton.addEventListener('click', function() {
            modalInstance.hide();
            openInvestmentModal(this.getAttribute('data-contract-id'));
        });
    }
    
    // Remove modal from DOM when hidden
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

// Open investment modal
function openInvestmentModal(contractId) {
    // If wallet is not connected, show wallet connection prompt
    if (!window.walletConnected) {
        showAlert('Please connect your wallet to invest.', 'warning');
        return;
    }
    
    // Create modal element
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'investmentModal';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-labelledby', 'investmentModalLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    // Modal HTML template
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content bg-dark text-light border-info">
                <div class="modal-header border-info">
                    <h5 class="modal-title" id="investmentModalLabel">
                        <i data-feather="dollar-sign" class="icon-inline text-info"></i>
                        Invest in Contract
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="investment-form">
                        <div class="mb-3">
                            <label for="tokenAmount" class="form-label">Number of Tokens</label>
                            <div class="input-group">
                                <input type="number" class="form-control bg-dark text-light border-info" id="tokenAmount" min="1" value="1">
                                <span class="input-group-text bg-dark text-light border-info">Tokens</span>
                            </div>
                            <div class="form-text text-muted">Enter the number of tokens you wish to purchase.</div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="investmentAmount" class="form-label">Total Investment</label>
                            <div class="input-group">
                                <span class="input-group-text bg-dark text-light border-info">$</span>
                                <input type="text" class="form-control bg-dark text-light border-info" id="investmentAmount" readonly>
                            </div>
                        </div>
                        
                        <div class="wallet-info d-flex justify-content-between align-items-center p-3 border border-info rounded mb-3">
                            <div>
                                <div class="text-muted small">Connected Wallet</div>
                                <div class="wallet-address">${truncateAddress(window.userWalletAddress)}</div>
                            </div>
                            <i data-feather="check-circle" class="text-success"></i>
                        </div>
                        
                        <div class="transaction-summary p-3 border border-info rounded">
                            <h6 class="text-info mb-3">Transaction Summary</h6>
                            
                            <div class="d-flex justify-content-between mb-2">
                                <span>Token Price:</span>
                                <span class="token-price">$0.00</span>
                            </div>
                            
                            <div class="d-flex justify-content-between mb-2">
                                <span>Number of Tokens:</span>
                                <span class="token-amount">0</span>
                            </div>
                            
                            <div class="d-flex justify-content-between mb-2">
                                <span>Gas Fee:</span>
                                <span class="gas-fee">0.25 ODIS</span>
                            </div>
                            
                            <hr class="border-info">
                            
                            <div class="d-flex justify-content-between fw-bold">
                                <span>Total Amount:</span>
                                <span class="total-amount">$0.00 + 0.25 ODIS</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer border-info">
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-info confirm-investment-btn">
                        <i data-feather="check" class="icon-inline-sm"></i>
                        Confirm Investment
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.appendChild(modal);
    
    // Initialize modal and show it
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    
    // Update feather icons inside modal
    feather.replace();
    
    // Fetch contract details and update form
    fetchApi(`/api/contracts/${contractId}`).then(contract => {
        // Update token price
        const tokenPriceElement = modal.querySelector('.token-price');
        if (tokenPriceElement) {
            tokenPriceElement.textContent = formatCurrency(contract.token_price);
        }
        
        // Add event listener for token amount input
        const tokenAmountInput = modal.querySelector('#tokenAmount');
        const investmentAmountInput = modal.querySelector('#investmentAmount');
        const tokenAmountDisplay = modal.querySelector('.token-amount');
        const totalAmountDisplay = modal.querySelector('.total-amount');
        
        if (tokenAmountInput && investmentAmountInput) {
            // Initial update
            const initialAmount = parseFloat(tokenAmountInput.value) * contract.token_price;
            investmentAmountInput.value = formatCurrency(initialAmount).substring(1); // Remove $ sign
            tokenAmountDisplay.textContent = tokenAmountInput.value;
            totalAmountDisplay.textContent = `${formatCurrency(initialAmount)} + 0.25 ODIS`;
            
            // Update on change
            tokenAmountInput.addEventListener('input', function() {
                const amount = parseFloat(this.value) * contract.token_price;
                investmentAmountInput.value = formatCurrency(amount).substring(1); // Remove $ sign
                tokenAmountDisplay.textContent = this.value;
                totalAmountDisplay.textContent = `${formatCurrency(amount)} + 0.25 ODIS`;
            });
        }
        
        // Add event listener for confirm button
        const confirmButton = modal.querySelector('.confirm-investment-btn');
        if (confirmButton) {
            confirmButton.addEventListener('click', function() {
                const tokenAmount = parseInt(tokenAmountInput.value);
                if (isNaN(tokenAmount) || tokenAmount <= 0) {
                    showAlert('Please enter a valid number of tokens.', 'warning');
                    return;
                }
                
                // Close modal
                modalInstance.hide();
                
                // Process investment
                processInvestment(contractId, tokenAmount, contract.token_price);
            });
        }
    }).catch(error => {
        console.error('Error fetching contract details:', error);
        showAlert('Failed to load contract details. Please try again later.', 'warning');
    });
    
    // Remove modal from DOM when hidden
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

// Process investment transaction
async function processInvestment(contractId, tokenAmount, tokenPrice) {
    try {
        // Show loading state
        const loadingAlert = showAlert('Preparing transaction... Please wait.', 'info');
        
        // Prepare transaction
        const totalAmount = tokenAmount * tokenPrice;
        const investmentData = {
            contract_id: contractId,
            token_amount: tokenAmount,
            total_amount: totalAmount,
            investor_address: window.userWalletAddress
        };
        
        // Send investment request to backend
        const transaction = await fetchApi('/api/investments/prepare', {
            method: 'POST',
            body: JSON.stringify(investmentData)
        });
        
        // Remove loading alert
        document.body.removeChild(loadingAlert);
        
        // Show transaction confirmation modal
        showTransactionConfirmationModal(transaction, investmentData);
    } catch (error) {
        console.error('Error preparing investment transaction:', error);
        showAlert('Failed to prepare investment transaction. Please try again later.', 'danger');
    }
}

// Show transaction confirmation modal
function showTransactionConfirmationModal(transaction, investmentData) {
    // Create modal element
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'transactionConfirmationModal';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-labelledby', 'transactionConfirmationModalLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    // Modal HTML template
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content bg-dark text-light border-info">
                <div class="modal-header border-info">
                    <h5 class="modal-title" id="transactionConfirmationModalLabel">
                        <i data-feather="shield" class="icon-inline text-info"></i>
                        Confirm Transaction
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="transaction-details">
                        <div class="alert alert-info" role="alert">
                            <i data-feather="info" class="icon-inline-sm"></i>
                            Please review the transaction details before signing with your wallet.
                        </div>
                        
                        <div class="transaction-summary p-3 border border-info rounded mb-3">
                            <h6 class="text-info mb-3">Transaction Details</h6>
                            
                            <div class="d-flex justify-content-between mb-2">
                                <span>From Address:</span>
                                <span class="text-break">${truncateAddress(window.userWalletAddress)}</span>
                            </div>
                            
                            <div class="d-flex justify-content-between mb-2">
                                <span>To Address:</span>
                                <span class="text-break">${truncateAddress(transaction.to_address)}</span>
                            </div>
                            
                            <div class="d-flex justify-content-between mb-2">
                                <span>Amount:</span>
                                <span>${formatNumber(transaction.amount)} ${transaction.denom}</span>
                            </div>
                            
                            <div class="d-flex justify-content-between mb-2">
                                <span>Gas Limit:</span>
                                <span>${formatNumber(transaction.gas_limit)}</span>
                            </div>
                            
                            <div class="d-flex justify-content-between mb-2">
                                <span>Gas Price:</span>
                                <span>${transaction.gas_price} ${transaction.gas_denom}</span>
                            </div>
                            
                            <div class="d-flex justify-content-between mb-2">
                                <span>Memo:</span>
                                <span class="text-break">${transaction.memo || 'None'}</span>
                            </div>
                        </div>
                        
                        <div class="wallet-interaction mb-3">
                            <h6 class="text-info mb-2">Wallet Interaction</h6>
                            <p>Click the button below to sign this transaction with your connected Keplr wallet.</p>
                        </div>
                    </div>
                </div>
                <div class="modal-footer border-info">
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-info sign-transaction-btn">
                        <i data-feather="key" class="icon-inline-sm"></i>
                        Sign with Keplr
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.appendChild(modal);
    
    // Initialize modal and show it
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    
    // Update feather icons inside modal
    feather.replace();
    
    // Add event listener for sign button
    const signButton = modal.querySelector('.sign-transaction-btn');
    if (signButton) {
        signButton.addEventListener('click', async function() {
            // Show loading state
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Signing...';
            
            try {
                // Call keplr to sign the transaction
                await signAndBroadcastTransaction(transaction);
                
                // Close modal
                modalInstance.hide();
                
                // Show success message
                showAlert('Transaction signed and broadcast successfully!', 'success');
            } catch (error) {
                console.error('Error signing transaction:', error);
                
                // Reset button
                this.disabled = false;
                this.innerHTML = '<i data-feather="key" class="icon-inline-sm"></i> Sign with Keplr';
                feather.replace();
                
                // Show error message
                showAlert('Failed to sign transaction. Please try again.', 'danger');
            }
        });
    }
    
    // Remove modal from DOM when hidden
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

// Sign and broadcast transaction using Keplr
async function signAndBroadcastTransaction(transaction) {
    return new Promise((resolve, reject) => {
        // Check if Keplr is available
        if (!window.keplr) {
            reject(new Error('Keplr wallet not found'));
            return;
        }
        
        // Call the global signTransaction function from kepler.js
        if (typeof window.signTransaction === 'function') {
            window.signTransaction(transaction)
                .then(resolve)
                .catch(reject);
        } else {
            reject(new Error('Keplr integration not properly initialized'));
        }
    });
}