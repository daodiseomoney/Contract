/**
 * Dashboard.js - Handle dashboard data display and interaction
 * This file connects the dashboard UI with backend data
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard components
    initializeDashboardStats();
    initializeAssetDistributionChart();
    initializeStakeholderChart();
    loadRecentTransactions();
    initializeMiniViewer();
    loadValidators();
});

/**
 * Initialize dashboard stats from backend API
 */
function initializeDashboardStats() {
    // Fetch dashboard stats from API
    fetch('/api/blockchain/stats')
        .then(response => {
            if (!response.ok) {
                return fallbackToCachedStats();
            }
            return response.json();
        })
        .then(stats => {
            updateDashboardStats(stats);
        })
        .catch(error => {
            console.error('Error fetching dashboard stats:', error);
            fallbackToCachedStats();
        });
}

/**
 * Update dashboard stats with data from API
 * @param {Object} stats - Dashboard statistics
 */
function updateDashboardStats(stats) {
    // Update token value
    const tokenValueElement = document.querySelector('.card-value');
    if (tokenValueElement && stats.token_value) {
        tokenValueElement.textContent = formatNumber(stats.token_value);
    }

    // Update reserves
    const reservesElement = document.querySelectorAll('.card-value')[1];
    if (reservesElement && stats.total_reserves) {
        reservesElement.textContent = `$${formatNumber(stats.total_reserves)}`;
    }

    // Update staking APY
    const stakingApyElement = document.querySelectorAll('.card-value')[2];
    if (stakingApyElement && stats.staking_apy) {
        stakingApyElement.textContent = `${stats.staking_apy}%`;
    }

    // Update daily rewards
    const dailyRewardsElement = document.querySelectorAll('.card-value')[3];
    if (dailyRewardsElement && stats.daily_rewards) {
        dailyRewardsElement.textContent = stats.daily_rewards;
    }

    // Update asset distribution verified/unverified values
    const verifiedAssetsElement = document.querySelector('.fw-bold.text-success');
    if (verifiedAssetsElement && stats.verified_assets) {
        verifiedAssetsElement.textContent = `$${formatNumber(stats.verified_assets)}`;
    }

    const unverifiedAssetsElement = document.querySelector('.fw-bold.text-warning');
    if (unverifiedAssetsElement && stats.unverified_assets) {
        unverifiedAssetsElement.textContent = `$${formatNumber(stats.unverified_assets)}`;
    }

    // Update hot asset data
    updateHotAssetData(stats.hot_asset || {});
}

/**
 * Update hot asset data in the UI
 * @param {Object} hotAsset - Hot asset data
 */
function updateHotAssetData(hotAsset) {
    // Update model name
    const modelNameElement = document.querySelector('.model-name');
    if (modelNameElement && hotAsset.name) {
        modelNameElement.textContent = hotAsset.name;
    }

    // Update progress bar
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar && hotAsset.funded_percentage) {
        progressBar.style.width = `${hotAsset.funded_percentage}%`;
        progressBar.setAttribute('aria-valuenow', hotAsset.funded_percentage);
    }

    // Update funded amount and target
    const fundedElement = document.querySelector('.progress + .d-flex small:first-child');
    if (fundedElement && hotAsset.funded_amount) {
        fundedElement.textContent = `Funded: $${formatNumber(hotAsset.funded_amount)}`;
    }

    const targetElement = document.querySelector('.progress + .d-flex small:last-child');
    if (targetElement && hotAsset.target_amount) {
        targetElement.textContent = `Target: $${formatNumber(hotAsset.target_amount)}`;
    }
}

/**
 * Fallback to cached stats if API call fails
 * @returns {Object} - Cached stats object
 */
function fallbackToCachedStats() {
    console.log('Using fallback dashboard stats');
    return {
        token_value: '15,811.04',
        total_reserves: '38126.50',
        staking_apy: '9.5',
        daily_rewards: '0.318',
        verified_assets: '24250000',
        unverified_assets: '13876500',
        hot_asset: {
            name: 'Idaka Project',
            funded_percentage: 65,
            funded_amount: '1625000',
            target_amount: '2500000'
        }
    };
}

/**
 * Initialize asset distribution chart
 */
function initializeAssetDistributionChart() {
    const chartElement = document.getElementById('asset-distribution-chart');
    if (!chartElement) return;

    fetch('/api/blockchain/asset-distribution')
        .then(response => {
            if (!response.ok) {
                return {
                    verified: 65,
                    unverified: 35
                };
            }
            return response.json();
        })
        .then(data => {
            createAssetDistributionChart(chartElement, data);
        })
        .catch(error => {
            console.error('Error fetching asset distribution data:', error);
            createAssetDistributionChart(chartElement, {
                verified: 65,
                unverified: 35
            });
        });
}

/**
 * Create asset distribution chart
 * @param {HTMLElement} element - Chart canvas element
 * @param {Object} data - Chart data
 */
function createAssetDistributionChart(element, data) {
    const ctx = element.getContext('2d');
    
    // Create chart
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Verified Assets', 'Unverified Assets'],
            datasets: [{
                data: [data.verified, data.unverified],
                backgroundColor: ['#4bc0c0', '#ffcd56'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutoutPercentage: 70,
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
 * Initialize stakeholder distribution chart
 */
function initializeStakeholderChart() {
    const chartElement = document.getElementById('stakeholder-chart');
    if (!chartElement) return;

    fetch('/api/blockchain/stakeholder-distribution')
        .then(response => {
            if (!response.ok) {
                return {
                    investors: 45,
                    validators: 25,
                    developers: 20,
                    community: 10
                };
            }
            return response.json();
        })
        .then(data => {
            createStakeholderChart(chartElement, data);
        })
        .catch(error => {
            console.error('Error fetching stakeholder distribution data:', error);
            createStakeholderChart(chartElement, {
                investors: 45,
                validators: 25,
                developers: 20,
                community: 10
            });
        });
}

/**
 * Create stakeholder distribution chart
 * @param {HTMLElement} element - Chart canvas element
 * @param {Object} data - Chart data
 */
function createStakeholderChart(element, data) {
    const ctx = element.getContext('2d');
    
    // Create chart
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data).map(key => key.charAt(0).toUpperCase() + key.slice(1)),
            datasets: [{
                data: Object.values(data),
                backgroundColor: ['#36a2eb', '#ff6384', '#4bc0c0', '#ffcd56'],
                borderWidth: 0
            }]
        },
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
 * Load recent transactions from API
 */
function loadRecentTransactions() {
    const transactionList = document.querySelector('.transaction-list');
    if (!transactionList) return;

    fetch('/api/transactions')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(transactions => {
            // Keep only the first 4 transactions for the dashboard
            const recentTransactions = transactions.slice(0, 4);
            
            // Clear existing transactions
            transactionList.innerHTML = '';
            
            // Add transactions to the list
            recentTransactions.forEach(transaction => {
                const txElement = createTransactionElement(transaction);
                transactionList.appendChild(txElement);
            });
            
            // Initialize feather icons
            if (window.feather) {
                feather.replace(transactionList.querySelectorAll('[data-feather]'));
            }
        })
        .catch(error => {
            console.error('Error fetching transactions:', error);
        });
}

/**
 * Create a transaction element
 * @param {Object} transaction - Transaction data
 * @returns {HTMLElement} - Transaction element
 */
function createTransactionElement(transaction) {
    // Determine icon and class based on transaction type
    let iconName = 'circle';
    let iconClass = 'info';
    let valueClass = '';
    
    switch(transaction.type.toLowerCase()) {
        case 'property tokenization':
            iconName = 'check-circle';
            iconClass = 'success';
            valueClass = 'success';
            break;
        case 'token transfer':
            iconName = 'refresh-cw';
            iconClass = 'warning';
            valueClass = transaction.value.startsWith('+') ? 'success' : 'warning';
            break;
        case 'contract signature':
        case 'document upload':
            iconName = 'file-text';
            iconClass = 'info';
            break;
        case 'multi-sig approval':
            iconName = 'users';
            iconClass = 'secondary';
            break;
    }
    
    // Create transaction element
    const txElement = document.createElement('div');
    txElement.className = 'transaction-item';
    
    // Format timestamp to relative time
    const timeAgo = formatTimeAgo(transaction.timestamp);
    
    txElement.innerHTML = `
        <div class="transaction-icon ${iconClass}">
            <i data-feather="${iconName}"></i>
        </div>
        <div class="transaction-details">
            <div class="transaction-title">${transaction.type} <span class="badge bg-${transaction.status === 'confirmed' ? 'success' : 'warning'}">${transaction.status === 'confirmed' ? 'VERIFIED' : 'PENDING'}</span></div>
            <div class="transaction-meta">
                <span class="transaction-address">${transaction.hash ? transaction.hash.substring(0, 8) + '...' + transaction.hash.substring(transaction.hash.length - 4) : 'N/A'}</span>
                <span class="transaction-time">${timeAgo}</span>
            </div>
        </div>
        <div class="transaction-value ${valueClass}">${transaction.value || '0 ODIS'}</div>
    `;
    
    return txElement;
}

/**
 * Load validators from API
 */
function loadValidators() {
    const validatorList = document.querySelector('.validator-list');
    if (!validatorList) return;

    fetch('/api/blockchain/validators')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(validators => {
            // Keep only the first 3 validators for the dashboard
            const activeValidators = validators.slice(0, 3);
            
            // Clear existing validators
            validatorList.innerHTML = '';
            
            // Add validators to the list
            activeValidators.forEach((validator, index) => {
                const validatorElement = createValidatorElement(validator, index);
                validatorList.appendChild(validatorElement);
            });
        })
        .catch(error => {
            console.error('Error fetching validators:', error);
        });
}

/**
 * Create a validator element
 * @param {Object} validator - Validator data
 * @param {number} index - Validator index
 * @returns {HTMLElement} - Validator element
 */
function createValidatorElement(validator, index) {
    // Determine color class based on index
    const colorClasses = ['info', 'secondary', 'success'];
    const colorClass = colorClasses[index % colorClasses.length];
    
    // Create validator element
    const validatorElement = document.createElement('div');
    validatorElement.className = 'd-flex align-items-center mb-3';
    validatorElement.innerHTML = `
        <div class="token-circle ${colorClass}">V</div>
        <div class="flex-grow-1">
            <div class="fw-bold">${validator.name || `Validator Node ${index + 1}`}</div>
            <div class="small text-muted">${validator.pending_proposals || 0} proposals pending</div>
        </div>
    `;
    
    return validatorElement;
}

/**
 * Initialize mini BIM viewer
 */
function initializeMiniViewer() {
    const miniViewerContainer = document.getElementById('mini-viewer-container');
    if (!miniViewerContainer) return;

    // Add sample model or fetch from API
    miniViewerContainer.innerHTML = `
        <model-viewer
            src="${'/static/models/sample_building.glb' || '/api/bim/hot-asset-model'}"
            alt="Hot Asset Building Model"
            auto-rotate
            camera-controls
            shadow-intensity="1"
            environment-image="/static/img/neutral.hdr"
            exposure="0.8"
            style="width: 100%; height: 300px;"
        ></model-viewer>
    `;
}

/**
 * Format number with commas
 * @param {number|string} num - Number to format
 * @returns {string} - Formatted number
 */
function formatNumber(num) {
    if (typeof num === 'string') {
        // If it's already a string with commas, return as is
        if (num.includes(',')) return num;
        
        // Otherwise parse it
        num = parseFloat(num);
    }
    
    // Format number with commas
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Format time ago from timestamp
 * @param {string} timestamp - ISO timestamp
 * @returns {string} - Formatted time ago
 */
function formatTimeAgo(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.round(diffMs / 1000);
    const diffMin = Math.round(diffSec / 60);
    const diffHour = Math.round(diffMin / 60);
    const diffDay = Math.round(diffHour / 24);
    
    if (diffSec < 60) {
        return `${diffSec} seconds ago`;
    } else if (diffMin < 60) {
        return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
    } else if (diffHour < 24) {
        return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
    } else if (diffDay < 7) {
        return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
    } else {
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
}