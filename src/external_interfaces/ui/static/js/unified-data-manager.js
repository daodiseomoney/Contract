// Unified Data Manager - Prevents duplicate API calls and manages rate limiting
class UnifiedDataManager {
    constructor() {
        this.cache = new Map();
        this.activeRequests = new Map();
        this.requestQueue = [];
        this.isProcessing = false;
        this.rateLimitDelay = 2000; // 2 seconds between requests
        this.maxRetries = 3;
        this.requestTimeout = 10000; // 10 seconds
    }

    async getData(endpoint, options = {}) {
        const cacheKey = `${endpoint}:${JSON.stringify(options)}`;
        
        // Return cached data if available and fresh
        const cached = this.getFromCache(cacheKey);
        if (cached) {
            console.log(`Returning cached data for ${endpoint}`);
            return cached;
        }

        // Check if request is already in progress
        if (this.activeRequests.has(endpoint)) {
            console.log(`Request already in progress for ${endpoint}, waiting...`);
            return this.activeRequests.get(endpoint);
        }

        // Create new request promise
        const requestPromise = this.makeRequest(endpoint, options);
        this.activeRequests.set(endpoint, requestPromise);

        try {
            const result = await requestPromise;
            this.setCache(cacheKey, result);
            return result;
        } finally {
            this.activeRequests.delete(endpoint);
        }
    }

    async makeRequest(endpoint, options = {}) {
        return new Promise((resolve, reject) => {
            this.requestQueue.push({
                endpoint,
                options,
                resolve,
                reject,
                retries: 0
            });

            if (!this.isProcessing) {
                this.processQueue();
            }
        });
    }

    async processQueue() {
        if (this.requestQueue.length === 0) {
            this.isProcessing = false;
            return;
        }

        this.isProcessing = true;
        const request = this.requestQueue.shift();

        try {
            const result = await this.executeRequest(request);
            request.resolve(result);
        } catch (error) {
            if (request.retries < this.maxRetries && error.status === 429) {
                request.retries++;
                console.log(`Retrying ${request.endpoint} (attempt ${request.retries})`);
                this.requestQueue.unshift(request); // Put back at front
                await this.sleep(this.rateLimitDelay * request.retries);
            } else {
                request.reject(error);
            }
        }

        // Wait before processing next request
        await this.sleep(this.rateLimitDelay);
        this.processQueue();
    }

    async executeRequest(request) {
        const { endpoint, options } = request;
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.requestTimeout);

        try {
            const response = await fetch(endpoint, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (response.status === 429) {
                throw { status: 429, message: 'Rate limited' };
            }

            if (!response.ok) {
                throw { status: response.status, message: response.statusText };
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw { status: 408, message: 'Request timeout' };
            }
            throw error;
        }
    }

    setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl: 30000 // 30 seconds
        });
    }

    getFromCache(key) {
        const cached = this.cache.get(key);
        if (!cached) return null;

        if (Date.now() - cached.timestamp > cached.ttl) {
            this.cache.delete(key);
            return null;
        }

        return cached.data;
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    clearCache() {
        this.cache.clear();
    }

    // Health check for endpoints
    async checkEndpointHealth(endpoint) {
        try {
            const response = await fetch(`${endpoint}?health=true`, {
                method: 'HEAD',
                signal: AbortSignal.timeout(5000)
            });
            return response.ok;
        } catch {
            return false;
        }
    }
}

// Error Boundary Component for Charts
class ChartErrorBoundary {
    constructor(containerId, chartName) {
        this.container = document.getElementById(containerId);
        this.chartName = chartName;
        this.hasError = false;
    }

    wrapExecution(fn) {
        try {
            return fn();
        } catch (error) {
            this.handleError(error);
            return null;
        }
    }

    async wrapAsyncExecution(fn) {
        try {
            return await fn();
        } catch (error) {
            this.handleError(error);
            return null;
        }
    }

    handleError(error) {
        console.error(`Error in ${this.chartName}:`, error);
        this.hasError = true;
        this.showErrorState(error);
    }

    showErrorState(error) {
        if (!this.container) return;

        const errorMessage = error.status === 429 
            ? 'Rate limited - retrying in a moment...'
            : error.status === 408
            ? 'Request timeout - check connection'
            : 'Failed to load data';

        this.container.innerHTML = `
            <div class="chart-error-state">
                <div class="error-icon">⚠️</div>
                <div class="error-message">${errorMessage}</div>
                <button class="retry-btn" onclick="this.closest('.chart-error-state').parentElement.dispatchEvent(new Event('retry'))">
                    Retry
                </button>
            </div>
            <style>
                .chart-error-state {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 200px;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px dashed rgba(255, 255, 255, 0.2);
                    border-radius: 8px;
                    color: #ff6b6b;
                }
                .error-icon { font-size: 24px; margin-bottom: 8px; }
                .error-message { margin-bottom: 16px; text-align: center; }
                .retry-btn {
                    padding: 8px 16px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                .retry-btn:hover { background: #0056b3; }
            </style>
        `;
    }

    reset() {
        this.hasError = false;
    }
}

// Global instances
window.dataManager = new UnifiedDataManager();
window.ChartErrorBoundary = ChartErrorBoundary;

// Enhanced chart loader with error boundaries
window.loadChartWithErrorBoundary = async function(containerId, chartName, loadFunction) {
    const errorBoundary = new ChartErrorBoundary(containerId, chartName);
    
    const container = document.getElementById(containerId);
    if (container) {
        container.addEventListener('retry', async () => {
            errorBoundary.reset();
            container.innerHTML = '<div class="loading-spinner">Loading...</div>';
            await errorBoundary.wrapAsyncExecution(loadFunction);
        });
    }

    await errorBoundary.wrapAsyncExecution(loadFunction);
};

console.log('Unified Data Manager initialized');