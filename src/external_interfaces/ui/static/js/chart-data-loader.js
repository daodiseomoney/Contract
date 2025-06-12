// Chart Data Loader with Circuit Breaker Pattern
class ChartDataLoader {
    constructor() {
        this.circuitBreaker = new Map();
        this.loadingStates = new Map();
        this.retryTimeouts = new Map();
    }

    async loadChartData(chartId, endpoint, renderFunction) {
        // Check circuit breaker state
        if (this.isCircuitOpen(endpoint)) {
            this.showCircuitBreakerMessage(chartId);
            return;
        }

        // Prevent duplicate loading
        if (this.loadingStates.get(chartId)) {
            return;
        }

        this.setLoadingState(chartId, true);
        this.showLoadingSpinner(chartId);

        try {
            const data = await window.dataManager.getData(endpoint);
            
            if (data && data.success) {
                this.resetCircuitBreaker(endpoint);
                await renderFunction(data.data || data);
                this.clearLoadingState(chartId);
            } else {
                throw new Error('Invalid response data');
            }
        } catch (error) {
            this.handleLoadError(chartId, endpoint, error, renderFunction);
        }
    }

    isCircuitOpen(endpoint) {
        const breaker = this.circuitBreaker.get(endpoint);
        if (!breaker) return false;
        
        if (breaker.failures >= 3) {
            const timeSinceLastFailure = Date.now() - breaker.lastFailure;
            return timeSinceLastFailure < 30000; // 30 seconds
        }
        return false;
    }

    resetCircuitBreaker(endpoint) {
        this.circuitBreaker.delete(endpoint);
    }

    recordFailure(endpoint) {
        const breaker = this.circuitBreaker.get(endpoint) || { failures: 0, lastFailure: 0 };
        breaker.failures++;
        breaker.lastFailure = Date.now();
        this.circuitBreaker.set(endpoint, breaker);
    }

    handleLoadError(chartId, endpoint, error, renderFunction) {
        this.recordFailure(endpoint);
        this.clearLoadingState(chartId);
        
        console.error(`Chart ${chartId} load error:`, error);
        
        if (error.status === 429) {
            this.showRateLimitError(chartId, endpoint, renderFunction);
        } else {
            this.showGenericError(chartId, endpoint, renderFunction);
        }
    }

    showLoadingSpinner(chartId) {
        const container = document.getElementById(chartId);
        if (container) {
            container.innerHTML = `
                <div class="chart-loading">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Loading chart data...</div>
                </div>
            `;
        }
    }

    showRateLimitError(chartId, endpoint, renderFunction) {
        const container = document.getElementById(chartId);
        if (container) {
            container.innerHTML = `
                <div class="chart-error rate-limit-error">
                    <div class="error-icon">⏱️</div>
                    <div class="error-title">Rate Limited</div>
                    <div class="error-message">Too many requests. Retrying automatically...</div>
                    <div class="retry-countdown" id="${chartId}-countdown">30</div>
                </div>
            `;
            
            this.scheduleRetry(chartId, endpoint, renderFunction, 30000);
        }
    }

    showGenericError(chartId, endpoint, renderFunction) {
        const container = document.getElementById(chartId);
        if (container) {
            container.innerHTML = `
                <div class="chart-error generic-error">
                    <div class="error-icon">⚠️</div>
                    <div class="error-title">Failed to Load</div>
                    <div class="error-message">Unable to fetch chart data</div>
                    <button class="retry-button" onclick="chartLoader.retryLoad('${chartId}', '${endpoint}', arguments[0])">
                        Retry Now
                    </button>
                </div>
            `;
        }
    }

    showCircuitBreakerMessage(chartId) {
        const container = document.getElementById(chartId);
        if (container) {
            container.innerHTML = `
                <div class="chart-error circuit-breaker">
                    <div class="error-icon">🔌</div>
                    <div class="error-title">Service Temporarily Unavailable</div>
                    <div class="error-message">Multiple failures detected. Waiting before retry...</div>
                </div>
            `;
        }
    }

    scheduleRetry(chartId, endpoint, renderFunction, delay) {
        const countdownElement = document.getElementById(`${chartId}-countdown`);
        let remainingTime = Math.floor(delay / 1000);
        
        const countdownTimer = setInterval(() => {
            remainingTime--;
            if (countdownElement) {
                countdownElement.textContent = remainingTime;
            }
            
            if (remainingTime <= 0) {
                clearInterval(countdownTimer);
                this.loadChartData(chartId, endpoint, renderFunction);
            }
        }, 1000);
        
        this.retryTimeouts.set(chartId, countdownTimer);
    }

    retryLoad(chartId, endpoint, renderFunction) {
        // Clear any existing retry timer
        const existingTimer = this.retryTimeouts.get(chartId);
        if (existingTimer) {
            clearInterval(existingTimer);
            this.retryTimeouts.delete(chartId);
        }
        
        this.loadChartData(chartId, endpoint, renderFunction);
    }

    setLoadingState(chartId, loading) {
        this.loadingStates.set(chartId, loading);
    }

    clearLoadingState(chartId) {
        this.loadingStates.delete(chartId);
    }
}

// Global chart loader instance
window.chartLoader = new ChartDataLoader();

// Enhanced chart loading functions
window.loadTokenMetrics = async function() {
    await window.chartLoader.loadChartData(
        'token-metrics-chart',
        '/api/orchestrator/token-metrics',
        function(data) {
            updateTokenDisplay(data.token_price, data.market_cap, data.volume_24h);
        }
    );
};

window.loadStakingMetrics = async function() {
    await window.chartLoader.loadChartData(
        'staking-metrics-chart', 
        '/api/orchestrator/staking-metrics',
        function(data) {
            updateStakingDisplay(data.staking_apy, data.daily_rewards);
        }
    );
};

window.loadNetworkHealth = async function() {
    await window.chartLoader.loadChartData(
        'network-health-chart',
        '/api/rpc/network-status',
        function(data) {
            updateNetworkDisplay(data);
        }
    );
};

// CSS for chart error states
const chartErrorStyles = `
<style>
.chart-loading, .chart-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    padding: 20px;
    text-align: center;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(255, 255, 255, 0.1);
    border-left: 4px solid #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-text {
    color: rgba(255, 255, 255, 0.7);
    font-size: 14px;
}

.chart-error {
    background: rgba(255, 255, 255, 0.03);
    border: 1px dashed rgba(255, 255, 255, 0.1);
    border-radius: 8px;
}

.error-icon {
    font-size: 32px;
    margin-bottom: 12px;
}

.error-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #ff6b6b;
}

.error-message {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 16px;
}

.retry-button {
    padding: 8px 16px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.retry-button:hover {
    background: #0056b3;
}

.retry-countdown {
    font-size: 18px;
    font-weight: bold;
    color: #ffa500;
    margin-top: 8px;
}

.rate-limit-error .error-icon {
    color: #ffa500;
}

.circuit-breaker .error-icon {
    color: #ff6b6b;
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', chartErrorStyles);

console.log('Chart Data Loader with Circuit Breaker initialized');