// Comprehensive Console Logger for DAODISEO Rate Limiting Analysis
class ConsoleLogger {
    constructor() {
        this.logs = [];
        this.maxLogs = 1000;
        this.startTime = Date.now();
        this.apiCallCount = 0;
        this.errorCount = 0;
        this.rateLimitCount = 0;
        
        this.initializeLogging();
    }

    initializeLogging() {
        // Override console methods to capture logs
        this.originalConsole = {
            log: console.log,
            error: console.error,
            warn: console.warn,
            info: console.info
        };

        // Intercept all console output
        console.log = (...args) => {
            this.captureLog('LOG', args);
            this.originalConsole.log(...args);
        };

        console.error = (...args) => {
            this.captureLog('ERROR', args);
            this.errorCount++;
            this.originalConsole.error(...args);
        };

        console.warn = (...args) => {
            this.captureLog('WARN', args);
            this.originalConsole.warn(...args);
        };

        console.info = (...args) => {
            this.captureLog('INFO', args);
            this.originalConsole.info(...args);
        };

        // Intercept fetch calls to log API requests
        this.interceptFetch();
        
        // Start periodic logging
        this.startPeriodicLogging();
    }

    captureLog(level, args) {
        const timestamp = new Date().toISOString();
        const message = args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
        ).join(' ');

        const logEntry = {
            timestamp,
            level,
            message,
            elapsed: Date.now() - this.startTime
        };

        this.logs.push(logEntry);
        
        // Keep only last maxLogs entries
        if (this.logs.length > this.maxLogs) {
            this.logs = this.logs.slice(-this.maxLogs);
        }

        // Check for rate limiting patterns
        if (message.includes('429') || message.includes('rate limit')) {
            this.rateLimitCount++;
            this.logRateLimitEvent(logEntry);
        }

        // Check for API failures
        if (message.includes('Failed to load') || message.includes('API error')) {
            this.logApiFailure(logEntry);
        }
    }

    interceptFetch() {
        const originalFetch = window.fetch;
        
        window.fetch = async (...args) => {
            const url = args[0];
            const options = args[1] || {};
            
            this.apiCallCount++;
            const callId = this.apiCallCount;
            
            console.log(`[API-${callId}] Starting request to: ${url}`);
            
            const startTime = Date.now();
            
            try {
                const response = await originalFetch(...args);
                const duration = Date.now() - startTime;
                
                if (response.status === 429) {
                    console.error(`[API-${callId}] Rate limited (429) - ${url} - Duration: ${duration}ms`);
                    this.rateLimitCount++;
                } else if (!response.ok) {
                    console.error(`[API-${callId}] HTTP ${response.status} - ${url} - Duration: ${duration}ms`);
                } else {
                    console.log(`[API-${callId}] Success ${response.status} - ${url} - Duration: ${duration}ms`);
                }
                
                return response;
            } catch (error) {
                const duration = Date.now() - startTime;
                console.error(`[API-${callId}] Network error - ${url} - Duration: ${duration}ms - Error:`, error);
                throw error;
            }
        };
    }

    logRateLimitEvent(logEntry) {
        console.log(`[RATE-LIMIT-ALERT] Count: ${this.rateLimitCount} | ${logEntry.message}`);
        
        // Log detailed rate limiting analysis
        const recentRateLimits = this.logs
            .filter(log => log.message.includes('429') || log.message.includes('rate limit'))
            .slice(-10);
            
        console.log('[RATE-LIMIT-PATTERN]', {
            total_rate_limits: this.rateLimitCount,
            recent_events: recentRateLimits.length,
            pattern_analysis: this.analyzeRateLimitPattern(recentRateLimits)
        });
    }

    logApiFailure(logEntry) {
        console.log(`[API-FAILURE] Total errors: ${this.errorCount} | ${logEntry.message}`);
        
        // Log failure patterns
        const recentFailures = this.logs
            .filter(log => log.level === 'ERROR')
            .slice(-5);
            
        console.log('[FAILURE-PATTERN]', {
            total_errors: this.errorCount,
            recent_failures: recentFailures.map(f => f.message),
            failure_rate: (this.errorCount / this.apiCallCount * 100).toFixed(2) + '%'
        });
    }

    analyzeRateLimitPattern(rateLimitEvents) {
        if (rateLimitEvents.length < 2) return 'Insufficient data';
        
        const intervals = [];
        for (let i = 1; i < rateLimitEvents.length; i++) {
            const interval = rateLimitEvents[i].elapsed - rateLimitEvents[i-1].elapsed;
            intervals.push(interval);
        }
        
        const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
        
        return {
            average_interval_ms: Math.round(avgInterval),
            frequency: intervals.length > 0 ? `${(60000 / avgInterval).toFixed(1)} per minute` : 'N/A',
            pattern: avgInterval < 5000 ? 'HIGH_FREQUENCY' : avgInterval < 30000 ? 'MODERATE' : 'LOW_FREQUENCY'
        };
    }

    startPeriodicLogging() {
        // Log system status every 30 seconds
        setInterval(() => {
            const uptime = Date.now() - this.startTime;
            const uptimeMinutes = Math.floor(uptime / 60000);
            const uptimeSeconds = Math.floor((uptime % 60000) / 1000);
            
            console.log(`[SYSTEM-STATUS] Uptime: ${uptimeMinutes}m ${uptimeSeconds}s | API Calls: ${this.apiCallCount} | Errors: ${this.errorCount} | Rate Limits: ${this.rateLimitCount}`);
            
            // Log memory usage if available
            if (performance.memory) {
                const memory = performance.memory;
                console.log(`[MEMORY-STATUS] Used: ${Math.round(memory.usedJSHeapSize / 1024 / 1024)}MB | Limit: ${Math.round(memory.jsHeapSizeLimit / 1024 / 1024)}MB`);
            }
            
            // Log recent activity summary
            const recentLogs = this.logs.filter(log => 
                Date.now() - new Date(log.timestamp).getTime() < 30000
            );
            
            const recentErrors = recentLogs.filter(log => log.level === 'ERROR').length;
            const recentWarnings = recentLogs.filter(log => log.level === 'WARN').length;
            
            if (recentErrors > 0 || recentWarnings > 0) {
                console.log(`[RECENT-ACTIVITY] Last 30s: ${recentLogs.length} logs, ${recentErrors} errors, ${recentWarnings} warnings`);
            }
            
        }, 30000);
    }

    exportLogs() {
        const exportData = {
            metadata: {
                export_time: new Date().toISOString(),
                session_start: new Date(this.startTime).toISOString(),
                total_logs: this.logs.length,
                api_calls: this.apiCallCount,
                errors: this.errorCount,
                rate_limits: this.rateLimitCount
            },
            logs: this.logs
        };
        
        console.log('[EXPORT-LOGS]', JSON.stringify(exportData, null, 2));
        return exportData;
    }

    getStats() {
        const stats = {
            uptime_ms: Date.now() - this.startTime,
            total_logs: this.logs.length,
            api_calls: this.apiCallCount,
            errors: this.errorCount,
            rate_limits: this.rateLimitCount,
            error_rate: this.apiCallCount > 0 ? (this.errorCount / this.apiCallCount * 100).toFixed(2) + '%' : '0%',
            rate_limit_rate: this.apiCallCount > 0 ? (this.rateLimitCount / this.apiCallCount * 100).toFixed(2) + '%' : '0%'
        };
        
        console.log('[LOGGER-STATS]', stats);
        return stats;
    }

    // Method to save all logs to console in structured format
    saveAllToConsole() {
        console.log('='.repeat(80));
        console.log('[DAODISEO-CONSOLE-EXPORT] Starting complete log export...');
        console.log('='.repeat(80));
        
        // Export metadata
        this.getStats();
        
        // Export all logs in chunks to avoid overwhelming console
        const chunkSize = 50;
        for (let i = 0; i < this.logs.length; i += chunkSize) {
            const chunk = this.logs.slice(i, i + chunkSize);
            console.log(`[LOG-CHUNK-${Math.floor(i / chunkSize) + 1}]`, chunk);
        }
        
        // Export rate limiting analysis
        const rateLimitLogs = this.logs.filter(log => 
            log.message.includes('429') || log.message.includes('rate limit')
        );
        
        if (rateLimitLogs.length > 0) {
            console.log('[RATE-LIMIT-ANALYSIS]', {
                total_events: rateLimitLogs.length,
                events: rateLimitLogs,
                pattern: this.analyzeRateLimitPattern(rateLimitLogs)
            });
        }
        
        // Export error analysis
        const errorLogs = this.logs.filter(log => log.level === 'ERROR');
        if (errorLogs.length > 0) {
            console.log('[ERROR-ANALYSIS]', {
                total_errors: errorLogs.length,
                errors: errorLogs
            });
        }
        
        console.log('='.repeat(80));
        console.log('[DAODISEO-CONSOLE-EXPORT] Export complete');
        console.log('='.repeat(80));
    }
}

// Initialize global logger
window.consoleLogger = new ConsoleLogger();

// Add global methods for easy access
window.exportLogs = () => window.consoleLogger.exportLogs();
window.getLoggerStats = () => window.consoleLogger.getStats();
window.saveAllToConsole = () => window.consoleLogger.saveAllToConsole();

// Log initialization
console.log('[CONSOLE-LOGGER] Enhanced logging system initialized');
console.log('[CONSOLE-LOGGER] Available commands: exportLogs(), getLoggerStats(), saveAllToConsole()');

// Auto-save to console every 5 minutes
setInterval(() => {
    console.log('[AUTO-SAVE] Saving logs to console...');
    window.consoleLogger.saveAllToConsole();
}, 300000);