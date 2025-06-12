/**
 * Enhanced Keplr Wallet Integration for DAODISEO
 * Configured for Odiseo Testnet
 */

// Odiseo testnet configuration
const ODISEO_TESTNET_CONFIG = {
    "chain_name": "odiseo",
    "chain_id": "ithaca-1",
    "network_type": "testnet",
    "website": "https://daodiseo.money",
    "bech32_prefix": "odiseo",
    "daemon_name": "achillesd",
    "node_home": ".achillesd",
    "rpc_url": "https://testnet-rpc.daodiseo.chaintools.tech",
    "api_url": "https://testnet-api.daodiseo.chaintools.tech",
    "denom": "uodis",
    "fixed_min_gas_price": 0.025,
    "low_gas_price": 0.01,
    "average_gas_price": 0.025,
    "high_gas_price": 0.04
};

class DAODISEOWalletManager {
    constructor() {
        this.connected = false;
        this.address = null;
        this.balance = null;
        this.keplr = null;
        
        // Initialize wallet state from session storage
        this.loadWalletState();
        this.initializeEventListeners();
    }
    
    loadWalletState() {
        const savedAddress = sessionStorage.getItem('walletAddress');
        const savedConnected = sessionStorage.getItem('walletConnected') === 'true';
        
        if (savedConnected && savedAddress) {
            this.connected = true;
            this.address = savedAddress;
            this.updateUI();
        }
    }
    
    saveWalletState() {
        sessionStorage.setItem('walletAddress', this.address || '');
        sessionStorage.setItem('walletConnected', this.connected.toString());
    }
    
    initializeEventListeners() {
        // Header wallet connection button
        const headerWalletBtn = document.getElementById('headerConnectKeplr');
        if (headerWalletBtn) {
            headerWalletBtn.addEventListener('click', () => {
                if (this.connected) {
                    this.disconnectWallet();
                } else {
                    this.connectWallet();
                }
            });
        }
        
        // Points system button
        const pointsBtn = document.getElementById('pointsSystemBtn');
        if (pointsBtn) {
            pointsBtn.addEventListener('click', () => this.showPointsModal());
        }
        
        // ODIS trading buttons
        const buyOdisBtn = document.getElementById('buyOdisBtn');
        if (buyOdisBtn) {
            buyOdisBtn.addEventListener('click', () => this.openStreamSwap());
        }
        
        const priceAlertBtn = document.getElementById('setPriceAlertBtn');
        if (priceAlertBtn) {
            priceAlertBtn.addEventListener('click', () => this.setPriceAlert());
        }
        
        // Listen for Keplr events
        window.addEventListener('keplr_keystorechange', () => {
            this.handleKeystoreChange();
        });
    }
    
    async connectWallet() {
        try {
            if (!window.keplr) {
                alert('Please install Keplr extension');
                window.open('https://www.keplr.app/', '_blank');
                return;
            }
            
            this.keplr = window.keplr;
            
            // Suggest chain to Keplr
            try {
                await this.keplr.experimentalSuggestChain({
                    chainId: ODISEO_TESTNET_CONFIG.chain_id,
                    chainName: ODISEO_TESTNET_CONFIG.chain_name,
                    rpc: ODISEO_TESTNET_CONFIG.rpc_url,
                    rest: ODISEO_TESTNET_CONFIG.api_url,
                    bip44: {
                        coinType: 118,
                    },
                    bech32Config: {
                        bech32PrefixAccAddr: ODISEO_TESTNET_CONFIG.bech32_prefix,
                        bech32PrefixAccPub: ODISEO_TESTNET_CONFIG.bech32_prefix + 'pub',
                        bech32PrefixValAddr: ODISEO_TESTNET_CONFIG.bech32_prefix + 'valoper',
                        bech32PrefixValPub: ODISEO_TESTNET_CONFIG.bech32_prefix + 'valoperpub',
                        bech32PrefixConsAddr: ODISEO_TESTNET_CONFIG.bech32_prefix + 'valcons',
                        bech32PrefixConsPub: ODISEO_TESTNET_CONFIG.bech32_prefix + 'valconspub',
                    },
                    currencies: [
                        {
                            coinDenom: 'ODIS',
                            coinMinimalDenom: ODISEO_TESTNET_CONFIG.denom,
                            coinDecimals: 6,
                        }
                    ],
                    feeCurrencies: [
                        {
                            coinDenom: 'ODIS',
                            coinMinimalDenom: ODISEO_TESTNET_CONFIG.denom,
                            coinDecimals: 6,
                            gasPriceStep: {
                                low: ODISEO_TESTNET_CONFIG.low_gas_price,
                                average: ODISEO_TESTNET_CONFIG.average_gas_price,
                                high: ODISEO_TESTNET_CONFIG.high_gas_price,
                            },
                        }
                    ],
                    stakeCurrency: {
                        coinDenom: 'ODIS',
                        coinMinimalDenom: ODISEO_TESTNET_CONFIG.denom,
                        coinDecimals: 6,
                    },
                });
            } catch (error) {
                console.log('Chain already exists or user rejected:', error);
            }
            
            // Enable the chain
            await this.keplr.enable(ODISEO_TESTNET_CONFIG.chain_id);
            
            // Get the offline signer
            const offlineSigner = this.keplr.getOfflineSigner(ODISEO_TESTNET_CONFIG.chain_id);
            const accounts = await offlineSigner.getAccounts();
            
            if (accounts.length > 0) {
                this.address = accounts[0].address;
                this.connected = true;
                
                // Get balance
                await this.updateBalance();
                
                // Save state and update UI
                this.saveWalletState();
                this.updateUI();
                
                // Award connection points
                this.awardPoints(10, 'Wallet Connected');
                
                console.log('Wallet connected:', this.address);
            }
            
        } catch (error) {
            console.error('Failed to connect wallet:', error);
            alert('Failed to connect wallet: ' + error.message);
        }
    }
    
    async updateBalance() {
        try {
            const response = await fetch(`${ODISEO_TESTNET_CONFIG.api_url}/cosmos/bank/v1beta1/balances/${this.address}`);
            const data = await response.json();
            
            const odisBalance = data.balances.find(b => b.denom === ODISEO_TESTNET_CONFIG.denom);
            this.balance = odisBalance ? parseInt(odisBalance.amount) / 1000000 : 0;
            
        } catch (error) {
            console.error('Failed to fetch balance:', error);
            this.balance = 0;
        }
    }
    
    updateUI() {
        const headerBtn = document.getElementById('headerConnectKeplr');
        
        if (this.connected && this.address) {
            // Update header wallet button - show address and disconnect option
            const shortAddress = this.address.substring(0, 6) + '...' + this.address.substring(this.address.length - 4);
            headerBtn.innerHTML = `
                <i data-feather="check-circle" class="icon-inline-sm"></i>
                ${shortAddress}
            `;
            headerBtn.className = 'btn btn-success btn-sm';
            headerBtn.title = `${this.address} - Click to disconnect`;
            
        } else {
            headerBtn.innerHTML = `
                <i data-feather="link" class="icon-inline-sm"></i>
                Connect Keplr
            `;
            headerBtn.className = 'btn btn-outline-info btn-sm';
            headerBtn.title = 'Connect your Keplr wallet';
        }
        
        // Update feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    awardPoints(amount, reason) {
        const currentPoints = parseInt(localStorage.getItem('userPoints') || '0');
        const newPoints = currentPoints + amount;
        localStorage.setItem('userPoints', newPoints.toString());
        
        // Update points display
        const pointsDisplay = document.getElementById('userPoints');
        if (pointsDisplay) {
            pointsDisplay.textContent = `${newPoints} pts`;
        }
        
        // Show points notification
        this.showPointsNotification(amount, reason);
    }
    
    showPointsNotification(amount, reason) {
        const notification = document.createElement('div');
        notification.className = 'points-notification';
        notification.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                <strong>+${amount} points!</strong> ${reason}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    
    showPointsModal() {
        const currentPoints = localStorage.getItem('userPoints') || '0';
        
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content bg-dark text-light border-warning">
                    <div class="modal-header border-warning">
                        <h5 class="modal-title">
                            <i data-feather="star" class="icon-inline text-warning"></i>
                            Your Points
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <div class="points-display mb-4">
                            <div class="display-1 text-warning">${currentPoints}</div>
                            <div class="text-muted">Total Points</div>
                        </div>
                        <div class="points-actions">
                            <h6>Earn More Points:</h6>
                            <ul class="list-unstyled">
                                <li>• Upload BIM file: +5 pts</li>
                                <li>• Complete transaction: +15 pts</li>
                                <li>• Daily login: +2 pts</li>
                                <li>• Connect wallet: +10 pts</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const pointsModal = new bootstrap.Modal(modal);
        pointsModal.show();
        
        feather.replace();
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
    
    openStreamSwap() {
        // Open StreamSwap in new tab for ODIS trading
        const streamSwapUrl = 'https://app.streamswap.io/swap?from=&to=uodis';
        window.open(streamSwapUrl, '_blank');
        
        // Award points for trading action
        this.awardPoints(5, 'Opened Trading Interface');
    }
    
    setPriceAlert() {
        const alertInput = document.getElementById('priceAlertInput');
        const alertPrice = parseFloat(alertInput.value);
        
        if (isNaN(alertPrice) || alertPrice <= 0) {
            alert('Please enter a valid price');
            return;
        }
        
        // Store price alert
        const alerts = JSON.parse(localStorage.getItem('priceAlerts') || '[]');
        alerts.push({
            price: alertPrice,
            timestamp: new Date().toISOString(),
            active: true
        });
        localStorage.setItem('priceAlerts', JSON.stringify(alerts));
        
        alert(`Price alert set for $$${alertPrice.toFixed(4)}`);
        alertInput.value = '';
        
        // Award points
        this.awardPoints(3, 'Price Alert Set');
    }
    
    disconnectWallet() {
        // Disconnect wallet and clear all stored data
        this.connected = false;
        this.address = null;
        this.balance = null;
        this.keplr = null;
        
        // Clear session storage
        sessionStorage.removeItem('walletAddress');
        sessionStorage.removeItem('walletConnected');
        
        // Update UI to show disconnected state
        this.updateUI();
        
        console.log('Wallet disconnected');
        
        // Show disconnection notification
        this.showDisconnectNotification();
    }
    
    showDisconnectNotification() {
        const notification = document.createElement('div');
        notification.className = 'disconnect-notification';
        notification.innerHTML = `
            <div class="alert alert-info alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                <strong>Wallet Disconnected</strong> You have been logged out safely.
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    handleKeystoreChange() {
        // Handle wallet account changes
        this.connected = false;
        this.address = null;
        this.balance = null;
        
        sessionStorage.removeItem('walletAddress');
        sessionStorage.removeItem('walletConnected');
        
        this.updateUI();
    }
}

// Initialize wallet manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.walletManager = new DAODISEOWalletManager();
    
    // Update points display on load
    const currentPoints = localStorage.getItem('userPoints') || '0';
    const pointsDisplay = document.getElementById('userPoints');
    if (pointsDisplay) {
        pointsDisplay.textContent = `${currentPoints} pts`;
    }
    
    // Load real validators data
    loadActiveValidators();
    
    // Remove duplicate rewards button from micro-rewards if it exists
    removeDuplicateRewardsButton();
});

// Function to load real validator data from blockchain service
async function loadActiveValidators() {
    try {
        const response = await fetch('/api/blockchain/stats');
        const data = await response.json();
        
        const validatorsContainer = document.getElementById('validatorsContainer');
        if (!validatorsContainer) return;
        
        if (data.validators && data.validators.length > 0) {
            const validatorsHtml = data.validators.slice(0, 3).map((validator, index) => {
                const moniker = validator.description?.moniker || `Validator ${index + 1}`;
                const votingPower = validator.voting_power ? parseInt(validator.voting_power) : 0;
                const status = validator.status === 'BOND_STATUS_BONDED' ? 'Active' : 'Inactive';
                const isJailed = validator.jailed ? ' (Jailed)' : '';
                
                // Create a simple display format matching the original style
                return `
                    <div class="d-flex align-items-center mb-3">
                        <div class="token-circle ${status === 'Active' ? 'info' : 'secondary'}">V</div>
                        <div class="flex-grow-1">
                            <div class="fw-bold">${moniker}${isJailed}</div>
                            <div class="small text-muted">${votingPower}M voting power</div>
                        </div>
                    </div>
                `;
            }).join('');
            
            validatorsContainer.innerHTML = validatorsHtml;
        } else {
            validatorsContainer.innerHTML = `
                <div class="text-center py-3">
                    <small class="text-muted">No validators found</small>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading validators:', error);
        const validatorsContainer = document.getElementById('validatorsContainer');
        if (validatorsContainer) {
            validatorsContainer.innerHTML = `
                <div class="text-center py-3">
                    <small class="text-danger">Failed to load validators</small>
                </div>
            `;
        }
    }
}

// Function to remove duplicate rewards button
function removeDuplicateRewardsButton() {
    // Remove any micro-rewards badge that might be duplicated
    const rewardsBadges = document.querySelectorAll('.micro-rewards-badge');
    if (rewardsBadges.length > 1) {
        // Keep only the first one (header one) and remove others
        for (let i = 1; i < rewardsBadges.length; i++) {
            rewardsBadges[i].remove();
        }
    }
    
    // Also remove any rewards panels that might be duplicated
    const rewardsPanels = document.querySelectorAll('.micro-rewards-panel');
    if (rewardsPanels.length > 1) {
        // Keep only the first one and remove others
        for (let i = 1; i < rewardsPanels.length; i++) {
            rewardsPanels[i].remove();
        }
    }
}