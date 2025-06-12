/**
 * Global State Management for DAODISEO Platform
 * Centralized state store to ensure consistency across all routes
 */

class DaodiseoGlobalState {
    constructor() {
        this.state = {
            wallet: {
                connected: false,
                address: null,
                balance: null,
                chainId: 'ithaca-1'
            },
            transaction: {
                currentId: null,
                status: null,
                hash: null,
                type: null
            },
            upload: {
                files: [],
                currentFile: null,
                validationResults: null,
                uploadStatus: null
            },
            contracts: {
                active: [],
                pending: [],
                signed: [],
                currentContract: null
            },
            ui: {
                currentRoute: null,
                loading: false,
                notifications: []
            }
        };
        
        this.listeners = new Map();
        this.init();
    }

    init() {
        // Load persisted state from sessionStorage
        this.loadPersistedState();
        
        // Set up event listeners for cross-route communication
        this.setupEventListeners();
        
        // Detect current route
        this.detectCurrentRoute();
        
        console.log('Global state initialized:', this.state);
    }

    loadPersistedState() {
        try {
            // Load wallet state
            const walletConnected = sessionStorage.getItem('walletConnected') === 'true';
            const walletAddress = sessionStorage.getItem('userWalletAddress');
            
            if (walletConnected && walletAddress) {
                this.setState('wallet', {
                    connected: true,
                    address: walletAddress
                });
            }

            // Load transaction state
            const currentTransactionId = sessionStorage.getItem('currentTransactionId');
            if (currentTransactionId) {
                this.setState('transaction', {
                    currentId: currentTransactionId
                });
            }

            // Load upload state
            const currentFileHash = sessionStorage.getItem('currentFileHash');
            const uploadStatus = sessionStorage.getItem('uploadStatus');
            if (currentFileHash) {
                this.setState('upload', {
                    currentFile: { hash: currentFileHash },
                    uploadStatus: uploadStatus
                });
            }

        } catch (error) {
            console.warn('Failed to load persisted state:', error);
        }
    }

    persistState() {
        try {
            // Persist wallet state
            sessionStorage.setItem('walletConnected', this.state.wallet.connected.toString());
            if (this.state.wallet.address) {
                sessionStorage.setItem('userWalletAddress', this.state.wallet.address);
            }

            // Persist transaction state
            if (this.state.transaction.currentId) {
                sessionStorage.setItem('currentTransactionId', this.state.transaction.currentId);
            }

            // Persist upload state
            if (this.state.upload.currentFile?.hash) {
                sessionStorage.setItem('currentFileHash', this.state.upload.currentFile.hash);
            }
            if (this.state.upload.uploadStatus) {
                sessionStorage.setItem('uploadStatus', this.state.upload.uploadStatus);
            }

        } catch (error) {
            console.warn('Failed to persist state:', error);
        }
    }

    setState(section, updates) {
        const previousState = { ...this.state[section] };
        this.state[section] = { ...this.state[section], ...updates };
        
        // Persist critical state changes
        this.persistState();
        
        // Notify listeners
        this.notifyListeners(section, this.state[section], previousState);
        
        // Dispatch custom events for cross-route communication
        this.dispatchStateEvent(section, this.state[section]);
    }

    getState(section = null) {
        return section ? this.state[section] : this.state;
    }

    subscribe(section, callback) {
        if (!this.listeners.has(section)) {
            this.listeners.set(section, new Set());
        }
        this.listeners.get(section).add(callback);
        
        // Return unsubscribe function
        return () => {
            this.listeners.get(section)?.delete(callback);
        };
    }

    notifyListeners(section, newState, previousState) {
        const sectionListeners = this.listeners.get(section);
        if (sectionListeners) {
            sectionListeners.forEach(callback => {
                try {
                    callback(newState, previousState);
                } catch (error) {
                    console.error('Error in state listener:', error);
                }
            });
        }
    }

    dispatchStateEvent(section, data) {
        const event = new CustomEvent(`stateChange:${section}`, {
            detail: { section, data }
        });
        document.dispatchEvent(event);
    }

    setupEventListeners() {
        // Listen for wallet connection events
        document.addEventListener('keplrConnected', (event) => {
            this.setState('wallet', {
                connected: true,
                address: event.detail?.address
            });
        });

        document.addEventListener('keplrDisconnected', () => {
            this.setState('wallet', {
                connected: false,
                address: null,
                balance: null
            });
            this.clearPersistedState();
        });

        // Listen for transaction events
        document.addEventListener('transactionCreated', (event) => {
            this.setState('transaction', {
                currentId: event.detail?.transactionId,
                status: 'created',
                type: event.detail?.type
            });
        });

        document.addEventListener('transactionSigned', (event) => {
            this.setState('transaction', {
                status: 'signed',
                hash: event.detail?.hash
            });
        });

        // Listen for upload events
        document.addEventListener('fileUploaded', (event) => {
            const fileData = {
                name: event.detail?.fileName,
                hash: event.detail?.fileHash,
                size: event.detail?.fileSize,
                type: event.detail?.fileType
            };
            
            this.setState('upload', {
                currentFile: fileData,
                uploadStatus: 'completed'
            });
        });

        // Listen for route changes
        window.addEventListener('popstate', () => {
            this.detectCurrentRoute();
        });
    }

    detectCurrentRoute() {
        const path = window.location.pathname;
        let route = 'dashboard'; // default
        
        if (path.includes('/upload')) route = 'upload';
        else if (path.includes('/contracts')) route = 'contracts';
        else if (path.includes('/viewer')) route = 'viewer';
        
        this.setState('ui', { currentRoute: route });
    }

    clearPersistedState() {
        try {
            // Clear all DAODISEO-related sessionStorage
            sessionStorage.removeItem('walletConnected');
            sessionStorage.removeItem('userWalletAddress');
            sessionStorage.removeItem('currentTransactionId');
            sessionStorage.removeItem('currentFileHash');
            sessionStorage.removeItem('uploadStatus');
            
            // Also clear legacy localStorage items
            localStorage.removeItem('walletConnected');
            localStorage.removeItem('userWalletAddress');
            localStorage.removeItem('kepler_address');
            
        } catch (error) {
            console.warn('Failed to clear persisted state:', error);
        }
    }

    // Utility methods for common state operations
    isWalletConnected() {
        return this.state.wallet.connected && this.state.wallet.address;
    }

    getCurrentTransaction() {
        return this.state.transaction.currentId;
    }

    getCurrentFile() {
        return this.state.upload.currentFile;
    }

    addNotification(message, type = 'info') {
        const notification = {
            id: Date.now(),
            message,
            type,
            timestamp: new Date().toISOString()
        };
        
        const notifications = [...this.state.ui.notifications, notification];
        this.setState('ui', { notifications });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            this.removeNotification(notification.id);
        }, 5000);
        
        return notification.id;
    }

    removeNotification(id) {
        const notifications = this.state.ui.notifications.filter(n => n.id !== id);
        this.setState('ui', { notifications });
    }

    // Debug method to view current state
    debug() {
        console.log('DAODISEO Global State:', JSON.stringify(this.state, null, 2));
        console.log('Active listeners:', Array.from(this.listeners.keys()));
    }
}

// Create global instance
window.DaodiseoState = new DaodiseoGlobalState();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DaodiseoGlobalState;
}