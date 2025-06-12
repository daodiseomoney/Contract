/*
 * DAODISEO Dashboard - Unified Core Module
 * Consolidates all dashboard functionality into a single optimized file
 * Replaces: dashboard.js, dashboard-enhanced.js, dashboard-fixed.js, dashboard-final-fix.js, etc.
 */

class DashboardCore {
    constructor() {
        this.apiRetryCount = 3;
        this.apiRetryDelay = 1000;
        this.updateInterval = 30000; // 30 seconds
        this.charts = {};
        this.eventBus = new EventTarget();
        this.init();
    }

    init() {
        console.log('[Dashboard] Initializing unified dashboard core');
        this.setupEventListeners();
        this.initializeCharts();
        this.loadDashboardData();
        this.startPeriodicUpdates();
    }

    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.bindWalletEvents();
            this.bindUIEvents();
        });
    }

    bindWalletEvents() {
        const walletBtn = document.getElementById('wallet-connect-btn');
        if (walletBtn) {
            walletBtn.addEventListener('click', () => this.connectWallet());
        }
    }

    bindUIEvents() {
        // Refresh button
        const refreshBtn = document.querySelector('.refresh-dashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshDashboard());
        }
    }

    async connectWallet() {
        try {
            if (!window.keplr) {
                alert('Please install Keplr wallet extension');
                return;
            }

            const chainId = 'ithaca-1';
            await window.keplr.enable(chainId);
            
            const offlineSigner = window.getOfflineSigner(chainId);
            const accounts = await offlineSigner.getAccounts();
            
            if (accounts.length > 0) {
                const address = accounts[0].address;
                await this.saveWalletConnection(address);
                this.updateWalletUI(address);
            }
        } catch (error) {
            console.error('[Dashboard] Wallet connection failed:', error);
        }
    }

    async saveWalletConnection(address) {
        try {
            const response = await fetch('/api/connect-wallet', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ address })
            });
            return await response.json();
        } catch (error) {
            console.error('[Dashboard] Failed to save wallet connection:', error);
        }
    }

    updateWalletUI(address) {
        const walletBtn = document.getElementById('wallet-connect-btn');
        const walletAddress = document.querySelector('.wallet-address');
        
        if (walletBtn) {
            walletBtn.textContent = `${address.slice(0, 8)}...${address.slice(-6)}`;
            walletBtn.classList.add('connected');
        }
        
        if (walletAddress) {
            walletAddress.textContent = address;
        }
    }

    async loadDashboardData() {
        console.log('[Dashboard] Loading dashboard data');
        
        try {
            const [tokenMetrics, stakingMetrics, networkHealth] = await Promise.all([
                this.fetchWithRetry('/api/orchestrator/token-metrics'),
                this.fetchWithRetry('/api/orchestrator/staking-metrics'),
                this.fetchWithRetry('/api/orchestrator/network-health')
            ]);

            this.updateTokenMetrics(tokenMetrics);
            this.updateStakingMetrics(stakingMetrics);
            this.updateNetworkHealth(networkHealth);
            this.updateCharts();
            
        } catch (error) {
            console.error('[Dashboard] Failed to load dashboard data:', error);
            this.showErrorState();
        }
    }

    async fetchWithRetry(url, retries = this.apiRetryCount) {
        for (let i = 0; i < retries; i++) {
            try {
                const response = await fetch(url);
                if (response.ok) {
                    return await response.json();
                }
                throw new Error(`HTTP ${response.status}`);
            } catch (error) {
                if (i === retries - 1) throw error;
                await new Promise(resolve => setTimeout(resolve, this.apiRetryDelay));
            }
        }
    }

    updateTokenMetrics(data) {
        if (!data?.success) return;
        
        const metrics = data.data;
        this.updateElement('.token-value', `$${metrics.price?.toLocaleString() || '0'}`);
        this.updateElement('.market-cap', `$${metrics.market_cap?.toLocaleString() || '0'}`);
        this.updateElement('.volume-24h', `$${metrics.volume_24h?.toLocaleString() || '0'}`);
        this.updateElement('.circulating-supply', metrics.circulating_supply?.toLocaleString() || '0');
    }

    updateStakingMetrics(data) {
        if (!data?.success) return;
        
        const metrics = data.data;
        this.updateElement('.staking-apy', `${metrics.apy || '0'}%`);
        this.updateElement('.total-staked', metrics.total_staked?.toLocaleString() || '0');
        this.updateElement('.validators-count', metrics.active_validators || '0');
        this.updateElement('.bonded-ratio', `${metrics.bonded_ratio || '0'}%`);
    }

    updateNetworkHealth(data) {
        if (!data?.success) return;
        
        const health = data.data;
        this.updateElement('.block-height', health.latest_block_height?.toLocaleString() || '0');
        this.updateElement('.block-time', `${health.avg_block_time || '0'}s`);
        this.updateElement('.peer-count', health.peer_count || '0');
        
        // Update network status indicator
        const statusElement = document.querySelector('.network-status');
        if (statusElement) {
            statusElement.className = `network-status ${health.status || 'unknown'}`;
            statusElement.textContent = health.status || 'Unknown';
        }
    }

    updateElement(selector, value) {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = value;
        }
    }

    initializeCharts() {
        this.initTokenChart();
        this.initStakingChart();
        this.initNetworkChart();
    }

    initTokenChart() {
        const ctx = document.getElementById('tokenChart');
        if (!ctx) return;

        this.charts.token = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'ODIS Price',
                    data: [],
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: false }
                }
            }
        });
    }

    initStakingChart() {
        const ctx = document.getElementById('stakingChart');
        if (!ctx) return;

        this.charts.staking = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Staked', 'Unstaked'],
                datasets: [{
                    data: [65, 35],
                    backgroundColor: ['#10B981', '#EF4444']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    initNetworkChart() {
        const ctx = document.getElementById('networkChart');
        if (!ctx) return;

        this.charts.network = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Validators', 'Delegators', 'Proposals'],
                datasets: [{
                    label: 'Network Activity',
                    data: [25, 1250, 8],
                    backgroundColor: ['#8B5CF6', '#F59E0B', '#06B6D4']
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    updateCharts() {
        // Update chart data with real-time information
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.update) {
                chart.update();
            }
        });
    }

    startPeriodicUpdates() {
        setInterval(() => {
            this.loadDashboardData();
        }, this.updateInterval);
    }

    refreshDashboard() {
        console.log('[Dashboard] Manual refresh triggered');
        this.loadDashboardData();
    }

    showErrorState() {
        console.warn('[Dashboard] Showing error state');
        const errorElements = document.querySelectorAll('.data-loading');
        errorElements.forEach(el => {
            el.textContent = 'Error loading data';
            el.classList.add('error');
        });
    }
}

// Global dashboard instance
window.DashboardCore = DashboardCore;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.dashboardCore = new DashboardCore();
    });
} else {
    window.dashboardCore = new DashboardCore();
}