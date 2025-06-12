/**
 * Wallet State Synchronization Across Routes
 * Ensures Keplr wallet connection persists between dashboard, upload, and viewer routes
 */

class WalletStateSync {
    constructor() {
        this.walletState = {
            connected: false,
            address: null,
            balance: null,
            chainId: 'ithaca-1'
        };
        this.init();
    }

    init() {
        this.loadStoredState();
        this.setupKeplrListeners();
        this.updateUIElements();
        this.bindWalletButtons();
    }

    loadStoredState() {
        const stored = localStorage.getItem('daodiseo_wallet_state');
        if (stored) {
            try {
                this.walletState = { ...this.walletState, ...JSON.parse(stored) };
            } catch (e) {
                console.warn('Invalid stored wallet state');
            }
        }
    }

    saveState() {
        localStorage.setItem('daodiseo_wallet_state', JSON.stringify(this.walletState));
        
        // Update global state
        if (window.globalState) {
            window.globalState.wallet = { ...this.walletState };
        }
    }

    async setupKeplrListeners() {
        if (!window.keplr) {
            // Wait for Keplr to load
            setTimeout(() => this.setupKeplrListeners(), 1000);
            return;
        }

        // Listen for account changes
        window.addEventListener('keplr_keystorechange', () => {
            this.checkConnectionStatus();
        });

        // Auto-connect if previously connected
        if (this.walletState.connected) {
            await this.reconnectWallet();
        }
    }

    async reconnectWallet() {
        try {
            if (!window.keplr) return false;

            const chainId = this.walletState.chainId;
            await window.keplr.enable(chainId);
            
            const offlineSigner = window.getOfflineSigner(chainId);
            const accounts = await offlineSigner.getAccounts();
            
            if (accounts.length > 0) {
                this.walletState.connected = true;
                this.walletState.address = accounts[0].address;
                await this.updateBalance();
                this.saveState();
                this.updateUIElements();
                return true;
            }
        } catch (error) {
            console.warn('Failed to reconnect wallet:', error);
            this.disconnectWallet();
        }
        return false;
    }

    async connectWallet() {
        try {
            if (!window.keplr) {
                alert('Keplr wallet extension not found. Please install Keplr.');
                return false;
            }

            const chainId = this.walletState.chainId;
            
            // Suggest chain if not added
            try {
                await window.keplr.experimentalSuggestChain({
                    chainId: chainId,
                    chainName: 'Daodiseo Testnet',
                    rpc: 'https://testnet-rpc.daodiseo.chaintools.tech',
                    rest: 'https://testnet-api.daodiseo.chaintools.tech',
                    bip44: {
                        coinType: 118,
                    },
                    bech32Config: {
                        bech32PrefixAccAddr: 'ithaca',
                        bech32PrefixAccPub: 'ithacapub',
                        bech32PrefixValAddr: 'ithacavaloper',
                        bech32PrefixValPub: 'ithacavaloperpub',
                        bech32PrefixConsAddr: 'ithacavalcons',
                        bech32PrefixConsPub: 'ithacavalconspub',
                    },
                    currencies: [{
                        coinDenom: 'DODI',
                        coinMinimalDenom: 'udodi',
                        coinDecimals: 6,
                    }],
                    feeCurrencies: [{
                        coinDenom: 'DODI',
                        coinMinimalDenom: 'udodi',
                        coinDecimals: 6,
                    }],
                    stakeCurrency: {
                        coinDenom: 'DODI',
                        coinMinimalDenom: 'udodi',
                        coinDecimals: 6,
                    },
                });
            } catch (error) {
                console.log('Chain suggestion failed, continuing...');
            }

            await window.keplr.enable(chainId);
            
            const offlineSigner = window.getOfflineSigner(chainId);
            const accounts = await offlineSigner.getAccounts();
            
            if (accounts.length > 0) {
                this.walletState.connected = true;
                this.walletState.address = accounts[0].address;
                await this.updateBalance();
                this.saveState();
                this.updateUIElements();
                return true;
            }
        } catch (error) {
            console.error('Failed to connect wallet:', error);
            alert('Failed to connect to Keplr wallet. Please try again.');
        }
        return false;
    }

    disconnectWallet() {
        this.walletState = {
            connected: false,
            address: null,
            balance: null,
            chainId: 'ithaca-1'
        };
        this.saveState();
        this.updateUIElements();
    }

    async updateBalance() {
        if (!this.walletState.connected || !this.walletState.address) return;

        try {
            // Try to get balance from RPC
            const response = await fetch(`/api/rpc/balance/${this.walletState.address}`);
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.walletState.balance = data.balance;
                    this.saveState();
                }
            }
        } catch (error) {
            console.warn('Failed to update balance:', error);
        }
    }

    async checkConnectionStatus() {
        if (!window.keplr) return;

        try {
            const chainId = this.walletState.chainId;
            const key = await window.keplr.getKey(chainId);
            
            if (key && key.bech32Address !== this.walletState.address) {
                this.walletState.address = key.bech32Address;
                await this.updateBalance();
                this.saveState();
                this.updateUIElements();
            }
        } catch (error) {
            // Connection lost
            this.disconnectWallet();
        }
    }

    updateUIElements() {
        // Update wallet connection buttons
        const connectButtons = document.querySelectorAll('.connect-wallet-btn, [onclick*="connectKeplr"]');
        const disconnectButtons = document.querySelectorAll('.disconnect-wallet-btn');
        const walletAddresses = document.querySelectorAll('.wallet-address');
        const walletBalances = document.querySelectorAll('.wallet-balance');
        
        if (this.walletState.connected) {
            connectButtons.forEach(btn => {
                btn.style.display = 'none';
            });
            
            disconnectButtons.forEach(btn => {
                btn.style.display = 'inline-block';
                btn.textContent = 'Disconnect Wallet';
            });
            
            walletAddresses.forEach(addr => {
                addr.textContent = this.formatAddress(this.walletState.address);
                addr.style.display = 'inline';
            });
            
            walletBalances.forEach(balance => {
                if (this.walletState.balance) {
                    balance.textContent = `${this.walletState.balance} DODI`;
                    balance.style.display = 'inline';
                }
            });
            
            // Update upload page specific elements
            this.updateUploadPageUI();
            
        } else {
            connectButtons.forEach(btn => {
                btn.style.display = 'inline-block';
                btn.textContent = 'Connect Keplr';
            });
            
            disconnectButtons.forEach(btn => {
                btn.style.display = 'none';
            });
            
            walletAddresses.forEach(addr => {
                addr.style.display = 'none';
            });
            
            walletBalances.forEach(balance => {
                balance.style.display = 'none';
            });
        }
    }

    updateUploadPageUI() {
        // Update upload page to show wallet is connected
        const uploadMessages = document.querySelectorAll('.wallet-required-message');
        const uploadForms = document.querySelectorAll('.upload-form, .ifc-upload-form');
        
        if (this.walletState.connected) {
            uploadMessages.forEach(msg => {
                msg.style.display = 'none';
            });
            
            uploadForms.forEach(form => {
                form.style.display = 'block';
                const connectNotice = form.querySelector('.connect-wallet-notice');
                if (connectNotice) {
                    connectNotice.style.display = 'none';
                }
            });
            
            // Add connected wallet info to upload forms
            this.addWalletInfoToUpload();
            
        } else {
            uploadMessages.forEach(msg => {
                msg.style.display = 'block';
                msg.innerHTML = `
                    <div class="alert alert-warning">
                        <h5>Wallet Connection Required</h5>
                        <p>Please connect your Keplr wallet to upload IFC files.</p>
                        <button class="btn btn-primary connect-wallet-btn" onclick="walletSync.connectWallet()">
                            Connect Keplr Wallet
                        </button>
                    </div>
                `;
            });
        }
    }

    addWalletInfoToUpload() {
        const uploadForms = document.querySelectorAll('.upload-form, .ifc-upload-form');
        uploadForms.forEach(form => {
            let walletInfo = form.querySelector('.wallet-connection-info');
            if (!walletInfo) {
                walletInfo = document.createElement('div');
                walletInfo.className = 'wallet-connection-info alert alert-success';
                form.insertBefore(walletInfo, form.firstChild);
            }
            
            walletInfo.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>Wallet Connected:</strong> ${this.formatAddress(this.walletState.address)}
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="walletSync.disconnectWallet()">
                        Disconnect
                    </button>
                </div>
            `;
        });
    }

    bindWalletButtons() {
        // Bind all wallet connect buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.connect-wallet-btn, [onclick*="connectKeplr"]')) {
                e.preventDefault();
                this.connectWallet();
            }
            
            if (e.target.matches('.disconnect-wallet-btn')) {
                e.preventDefault();
                this.disconnectWallet();
            }
        });
    }

    formatAddress(address) {
        if (!address) return '';
        return `${address.slice(0, 8)}...${address.slice(-6)}`;
    }

    // Public API for other components
    isConnected() {
        return this.walletState.connected;
    }

    getAddress() {
        return this.walletState.address;
    }

    getBalance() {
        return this.walletState.balance;
    }
}

// Initialize wallet state sync
let walletSync;
document.addEventListener('DOMContentLoaded', () => {
    walletSync = new WalletStateSync();
    window.walletSync = walletSync;
    
    // Make connect function globally available
    window.connectKeplrWallet = () => walletSync.connectWallet();
});

// Also initialize if DOM is already loaded
if (document.readyState !== 'loading') {
    walletSync = new WalletStateSync();
    window.walletSync = walletSync;
    window.connectKeplrWallet = () => walletSync.connectWallet();
}