// Enhanced API retry system with exponential backoff
class APIRetryManager {
    constructor() {
        this.requestQueue = new Map();
        this.retryCount = new Map();
        this.isThrottled = false;
        this.cache = new Map();
        this.cacheTTL = 15000; // 15 seconds
    }

    async fetchApi(url, options = {}, retries = 3, delay = 500) {
        // Check cache first
        const cacheKey = `${url}${JSON.stringify(options)}`;
        const cached = this.getFromCache(cacheKey);
        if (cached) return cached;

        // Check if we're already throttled
        if (this.isThrottled) {
            await this.waitForThrottle();
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (response.status === 429) {
                console.warn(`Rate limited on ${url}, retrying in ${delay}ms`);
                this.isThrottled = true;
                
                if (retries > 0) {
                    await new Promise(resolve => setTimeout(resolve, delay));
                    this.isThrottled = false;
                    return this.fetchApi(url, options, retries - 1, delay * 2);
                } else {
                    throw new Error('Rate limit exceeded after all retries');
                }
            }

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.setCache(cacheKey, data);
            this.retryCount.delete(url);
            return data;

        } catch (error) {
            console.error(`API fetch error for ${url}:`, error);
            
            if (retries > 0 && error.name !== 'TypeError') {
                await new Promise(resolve => setTimeout(resolve, delay));
                return this.fetchApi(url, options, retries - 1, delay * 1.5);
            }
            
            throw error;
        }
    }

    setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    getFromCache(key) {
        const cached = this.cache.get(key);
        if (!cached) return null;
        
        if (Date.now() - cached.timestamp > this.cacheTTL) {
            this.cache.delete(key);
            return null;
        }
        
        return cached.data;
    }

    async waitForThrottle() {
        return new Promise(resolve => {
            const checkThrottle = () => {
                if (!this.isThrottled) {
                    resolve();
                } else {
                    setTimeout(checkThrottle, 100);
                }
            };
            checkThrottle();
        });
    }

    clearCache() {
        this.cache.clear();
    }
}

// Global API manager instance
window.apiManager = new APIRetryManager();

// Enhanced dashboard data loader with queue management
class DashboardDataLoader {
    constructor() {
        this.loadQueue = [];
        this.isLoading = false;
        this.loadedSections = new Set();
    }

    async queueLoad(section, url, handler) {
        if (this.loadedSections.has(section)) return;
        
        this.loadQueue.push({ section, url, handler });
        
        if (!this.isLoading) {
            this.processQueue();
        }
    }

    async processQueue() {
        if (this.loadQueue.length === 0) return;
        
        this.isLoading = true;
        
        while (this.loadQueue.length > 0) {
            const { section, url, handler } = this.loadQueue.shift();
            
            try {
                console.log(`Loading ${section} data...`);
                const data = await window.apiManager.fetchApi(url);
                handler(data);
                this.loadedSections.add(section);
                
                // Small delay between requests to avoid overwhelming
                await new Promise(resolve => setTimeout(resolve, 200));
                
            } catch (error) {
                console.error(`Failed to load ${section}:`, error);
                this.showErrorState(section, error);
            }
        }
        
        this.isLoading = false;
    }

    showErrorState(section, error) {
        const element = document.querySelector(`[data-section="${section}"]`);
        if (element) {
            element.innerHTML = `
                <div class="error-state p-4 text-center">
                    <p class="text-red-400 mb-2">Failed to load ${section}</p>
                    <button onclick="dashboardLoader.retryLoad('${section}')" 
                            class="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
                        Retry
                    </button>
                </div>
            `;
        }
    }

    retryLoad(section) {
        this.loadedSections.delete(section);
        // Re-trigger the appropriate load function based on section
        if (section === 'token-metrics') {
            this.loadTokenMetrics();
        } else if (section === 'staking-metrics') {
            this.loadStakingMetrics();
        } else if (section === 'network-status') {
            this.loadNetworkStatus();
        }
    }

    async loadTokenMetrics() {
        await this.queueLoad('token-metrics', '/api/orchestrator/token-metrics', (data) => {
            if (data.success) {
                updateTokenDisplay(data.token_price, data.market_cap, data.volume_24h);
            }
        });
    }

    async loadStakingMetrics() {
        await this.queueLoad('staking-metrics', '/api/orchestrator/staking-metrics', (data) => {
            if (data.success) {
                updateStakingDisplay(data.staking_apy, data.daily_rewards);
            }
        });
    }

    async loadNetworkStatus() {
        await this.queueLoad('network-status', '/api/rpc/network-status', (data) => {
            if (data.success) {
                updateNetworkDisplay(data.data);
            }
        });
    }
}

// Global dashboard loader
window.dashboardLoader = new DashboardDataLoader();

// On-demand loading functions
function loadValidatorInsights() {
    const button = event.target;
    button.textContent = 'Loading...';
    button.disabled = true;
    
    window.apiManager.fetchApi('/api/orchestrator/network-analysis')
        .then(data => {
            if (data.success) {
                displayValidatorInsights(data);
            }
        })
        .catch(error => {
            console.error('Failed to load validator insights:', error);
        })
        .finally(() => {
            button.textContent = 'Load Validator Insights';
            button.disabled = false;
        });
}

function displayValidatorInsights(data) {
    const container = document.querySelector('#validator-insights');
    if (container) {
        container.innerHTML = `
            <div class="ai-analysis-result p-4 bg-gray-800 rounded-lg">
                <h4 class="text-lg font-semibold mb-2">AI Validator Analysis</h4>
                <p class="text-gray-300 mb-2">${data.analysis}</p>
                <div class="flex justify-between text-sm text-gray-400">
                    <span>Security Score: ${data.security_score}</span>
                    <span>Confidence: ${Math.round(data.confidence * 100)}%</span>
                </div>
            </div>
        `;
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Enhanced API retry system initialized');
    
    // Start loading critical data with delays
    setTimeout(() => window.dashboardLoader.loadNetworkStatus(), 100);
    setTimeout(() => window.dashboardLoader.loadTokenMetrics(), 500);
    setTimeout(() => window.dashboardLoader.loadStakingMetrics(), 1000);
});