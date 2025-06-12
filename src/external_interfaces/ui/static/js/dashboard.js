/**
 * Dashboard JavaScript for the Daodiseo Real Estate Tokenization Platform
 * Provides interactive charts and dashboard data
 */

// Initialize dashboard components
document.addEventListener('DOMContentLoaded', () => {
    initDashboardData();
    initDashboardCharts();
<<<<<<< HEAD
    initDashboardStateListeners();
});

// Initialize dashboard state listeners for cross-route synchronization
function initDashboardStateListeners() {
    // Listen for transaction events from other routes
    document.addEventListener('transactionCreated', (event) => {
        const { transactionId, hash, type } = event.detail;
        console.log('Dashboard received transaction event:', { transactionId, hash, type });
        
        // Update portfolio metrics to reflect new transaction
        refreshPortfolioData();
        
        // Add to recent transactions list
        addRecentTransaction({ transactionId, hash, type });
    });
    
    // Listen for file upload events to update asset counts
    document.addEventListener('fileUploaded', (event) => {
        const { fileName, fileHash } = event.detail;
        console.log('Dashboard received file upload event:', { fileName, fileHash });
        
        // Refresh verified assets count
        refreshAssetMetrics();
    });
    
    // Listen for wallet state changes
    document.addEventListener('stateChange:wallet', (event) => {
        const walletState = event.detail.data;
        updateWalletDashboard(walletState);
    });
    
    // Listen for contract state changes
    document.addEventListener('stateChange:contracts', (event) => {
        const contractsState = event.detail.data;
        updateContractMetrics(contractsState);
    });
}

=======
});

>>>>>>> fb24633dab07b7e0a60328f87ead6e6396c2f113
// Initialize dashboard data from API
async function initDashboardData() {
    try {
        // Fetch dashboard statistics from API
        const statsData = await fetchApi('/api/blockchain/stats');
        
        // Update dashboard UI with fetched data
        updateDashboardMetrics(statsData);
        updateHotAsset(statsData.hot_asset);
        
    } catch (error) {
        console.error('Error initializing dashboard data:', error);
        
        // Show error message to user
        showAlert('Failed to load dashboard data. Please try again later.', 'warning');
    }
}

// Update dashboard metrics with values from API
function updateDashboardMetrics(data) {
    // Update token value
    const tokenValueElement = document.querySelector('.token-value');
    if (tokenValueElement) {
        tokenValueElement.textContent = formatCurrency(data.token_value);
    }
    
    // Update staking APY
    const stakingApyElement = document.querySelector('.staking-apy');
    if (stakingApyElement) {
        stakingApyElement.textContent = formatPercentage(data.staking_apy);
    }
    
    // Update total reserves
    const totalReservesElement = document.querySelector('.total-reserves');
    if (totalReservesElement) {
        totalReservesElement.textContent = formatCurrency(data.total_reserves);
    }
    
    // Update daily rewards
    const dailyRewardsElement = document.querySelector('.daily-rewards');
    if (dailyRewardsElement) {
        dailyRewardsElement.textContent = formatNumber(data.daily_rewards);
    }
    
    // Update verified assets
    const verifiedAssetsElement = document.querySelector('.verified-assets');
    if (verifiedAssetsElement) {
        verifiedAssetsElement.textContent = formatCurrency(data.verified_assets);
    }
    
    // Update unverified assets
    const unverifiedAssetsElement = document.querySelector('.unverified-assets');
    if (unverifiedAssetsElement) {
        unverifiedAssetsElement.textContent = formatCurrency(data.unverified_assets);
    }
}

<<<<<<< HEAD
// Refresh portfolio data after cross-route events
async function refreshPortfolioData() {
    try {
        const statsData = await fetchApi('/api/blockchain/stats');
        updateDashboardMetrics(statsData);
    } catch (error) {
        console.warn('Failed to refresh portfolio data:', error);
    }
}

// Refresh asset metrics after file uploads
async function refreshAssetMetrics() {
    try {
        const assetData = await fetchApi('/api/blockchain/asset-distribution');
        updateAssetDistribution(assetData);
    } catch (error) {
        console.warn('Failed to refresh asset metrics:', error);
    }
}

// Add recent transaction to dashboard
function addRecentTransaction(transaction) {
    const recentTransactionsList = document.querySelector('.recent-transactions-list');
    if (!recentTransactionsList) return;
    
    const transactionElement = document.createElement('div');
    transactionElement.className = 'transaction-item d-flex justify-content-between align-items-center py-2 border-bottom';
    transactionElement.innerHTML = `
        <div>
            <div class="fw-medium">${transaction.type.charAt(0).toUpperCase() + transaction.type.slice(1)} Transaction</div>
            <small class="text-muted">ID: ${transaction.transactionId}</small>
        </div>
        <div class="text-end">
            <div class="badge bg-success">Completed</div>
            <small class="d-block text-muted">Just now</small>
        </div>
    `;
    
    // Insert at the top of the list
    recentTransactionsList.insertBefore(transactionElement, recentTransactionsList.firstChild);
    
    // Limit to 5 recent transactions
    const transactionItems = recentTransactionsList.querySelectorAll('.transaction-item');
    if (transactionItems.length > 5) {
        recentTransactionsList.removeChild(transactionItems[transactionItems.length - 1]);
    }
}

// Update wallet dashboard display
function updateWalletDashboard(walletState) {
    const walletAddressElement = document.querySelector('.wallet-address-display');
    const walletBalanceElement = document.querySelector('.wallet-balance-display');
    
    if (walletState.connected && walletState.address) {
        if (walletAddressElement) {
            const shortAddress = walletState.address.slice(0, 8) + '...' + walletState.address.slice(-4);
            walletAddressElement.textContent = shortAddress;
        }
        
        if (walletBalanceElement && walletState.balance) {
            walletBalanceElement.textContent = formatNumber(walletState.balance) + ' ODIS';
        }
    } else {
        if (walletAddressElement) {
            walletAddressElement.textContent = 'Not Connected';
        }
        if (walletBalanceElement) {
            walletBalanceElement.textContent = '0 ODIS';
        }
    }
}

// Update contract metrics in dashboard
function updateContractMetrics(contractsState) {
    const activeContractsElement = document.querySelector('.active-contracts-count');
    const pendingContractsElement = document.querySelector('.pending-contracts-count');
    
    if (activeContractsElement) {
        activeContractsElement.textContent = contractsState.active?.length || 0;
    }
    
    if (pendingContractsElement) {
        pendingContractsElement.textContent = contractsState.pending?.length || 0;
    }
}

// Update asset distribution chart
function updateAssetDistribution(assetData) {
    const assetChart = document.querySelector('#assetDistributionChart');
    if (assetChart && window.assetDistributionChart) {
        // Update chart data if chart instance exists
        window.assetDistributionChart.data.datasets[0].data = assetData.values;
        window.assetDistributionChart.data.labels = assetData.labels;
        window.assetDistributionChart.update();
    }
}

=======
>>>>>>> fb24633dab07b7e0a60328f87ead6e6396c2f113
// Update hot asset display
function updateHotAsset(hotAsset) {
    const hotAssetNameElement = document.querySelector('.hot-asset-name');
    if (hotAssetNameElement) {
        hotAssetNameElement.textContent = hotAsset.name;
    }
    
    const fundingProgressElement = document.querySelector('.funding-progress-bar');
    if (fundingProgressElement) {
        fundingProgressElement.style.width = `${hotAsset.funded_percentage}%`;
        fundingProgressElement.setAttribute('aria-valuenow', hotAsset.funded_percentage);
    }
    
    const fundingPercentageElement = document.querySelector('.funding-percentage');
    if (fundingPercentageElement) {
        fundingPercentageElement.textContent = `${hotAsset.funded_percentage}%`;
    }
    
    const fundingAmountElement = document.querySelector('.funding-amount');
    if (fundingAmountElement) {
        fundingAmountElement.textContent = 
            `${formatCurrency(hotAsset.funded_amount)} / ${formatCurrency(hotAsset.target_amount)}`;
    }
}

// Initialize dashboard charts
async function initDashboardCharts() {
    try {
        // Fetch data for charts
        const assetDistribution = await fetchApi('/api/blockchain/asset-distribution');
        const stakeholderDistribution = await fetchApi('/api/blockchain/stakeholder-distribution');
        
        // Initialize asset distribution chart
        initAssetDistributionChart(assetDistribution);
        
        // Initialize stakeholder distribution chart
        initStakeholderDistributionChart(stakeholderDistribution);
        
        // Initialize transaction history chart (with mock data for now)
        initTransactionHistoryChart();
        
    } catch (error) {
        console.error('Error initializing dashboard charts:', error);
        showAlert('Failed to load chart data. Please try again later.', 'warning');
    }
}

// Initialize asset distribution doughnut chart
function initAssetDistributionChart(data) {
    const chartElement = document.getElementById('assetDistributionChart');
    if (!chartElement) return;
    
    const ctx = chartElement.getContext('2d');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Verified Assets', 'Unverified Assets'],
            datasets: [{
                data: [data.verified, data.unverified],
                backgroundColor: ['rgba(32, 201, 151, 0.8)', 'rgba(108, 117, 125, 0.8)'],
                borderColor: ['#20c997', '#6c757d'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed}%`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// Initialize stakeholder distribution doughnut chart
function initStakeholderDistributionChart(data) {
    const chartElement = document.getElementById('stakeholderDistributionChart');
    if (!chartElement) return;
    
    const ctx = chartElement.getContext('2d');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Investors', 'Validators', 'Developers', 'Community'],
            datasets: [{
                data: [
                    data.investors, 
                    data.validators, 
                    data.developers, 
                    data.community
                ],
                backgroundColor: [
                    'rgba(0, 123, 255, 0.8)', 
                    'rgba(32, 201, 151, 0.8)', 
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(220, 53, 69, 0.8)'
                ],
                borderColor: [
                    '#007bff', 
                    '#20c997', 
                    '#ffc107',
                    '#dc3545'
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
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed}%`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// Initialize transaction history chart
function initTransactionHistoryChart() {
    const chartElement = document.getElementById('transactionHistoryChart');
    if (!chartElement) return;
    
    const ctx = chartElement.getContext('2d');
    
    // Get last 7 days for labels
    const labels = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    
    // Fetch transaction data from API (to be implemented)
    // For now, use placeholder data
    const transactionData = [12, 19, 8, 15, 12, 8, 25];
    const volumeData = [75000, 102000, 56000, 81000, 77000, 45000, 183000];
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Transactions',
                    data: transactionData,
                    borderColor: 'rgba(13, 202, 240, 1)',
                    backgroundColor: 'rgba(13, 202, 240, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Volume (ODIS)',
                    data: volumeData,
                    borderColor: 'rgba(25, 135, 84, 1)',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.4,
                    fill: false,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                y: {
                    position: 'left',
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    },
                    title: {
                        display: true,
                        text: 'Transactions',
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                y1: {
                    position: 'right',
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        callback: function(value) {
                            if (value >= 1000) {
                                return value / 1000 + 'k';
                            }
                            return value;
                        }
                    },
                    title: {
                        display: true,
                        text: 'Volume (ODIS)',
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.datasetIndex === 1) {
                                label += formatNumber(context.raw) + ' ODIS';
                            } else {
                                label += context.raw;
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}