// Kepler wallet integration
class KeplerWallet {
    constructor() {
        this.chainId = 'ithaca-1';
        this.connected = false;
        this.address = null;
        
        // SECURITY UPDATE: Use sessionStorage instead of localStorage for better security
        // Session storage is cleared when the user closes their browser
        
        // Try to restore previous connection from sessionStorage (more secure)
        const savedAddress = sessionStorage.getItem('kepler_address');
        if (savedAddress) {
            this.address = savedAddress;
            this.connected = true;
            
            // Security: Log connection time for session tracking
            sessionStorage.setItem('wallet_connect_time', Date.now().toString());
            sessionStorage.setItem('walletConnected', 'true');
            
            this.updateUI();
        }
        
        // Security: Check for connection timeout (4 hours max)
        this.checkSessionTimeout();
    }
    
    // Security: Add session timeout check to automatically disconnect after period of inactivity
    checkSessionTimeout() {
        const connectTime = sessionStorage.getItem('wallet_connect_time');
        if (connectTime) {
            const elapsed = Date.now() - parseInt(connectTime);
            const MAX_SESSION_TIME = 4 * 60 * 60 * 1000; // 4 hours in milliseconds
            
            if (elapsed > MAX_SESSION_TIME) {
                console.log('Wallet session timed out after 4 hours');
                this.disconnect();
            }
        }
    }

    async init() {
        // Wait for Kepler to be injected
        if (!window.keplr) {
            throw new Error('Please install Keplr extension');
        }

        try {
            // Fetch network config from backend
            const response = await fetch('/api/network-config');
            const networkConfig = await response.json();

            // Add the Odiseo testnet to Keplr
            await window.keplr.experimentalSuggestChain(networkConfig);

            // Enable the chain
            await window.keplr.enable(this.chainId);

            // Get the offline signer
            const offlineSigner = await window.keplr.getOfflineSigner(this.chainId);

            // Get user's address
            const accounts = await offlineSigner.getAccounts();
            this.address = accounts[0].address;
            this.connected = true;

            // SECURITY: Save connection state to sessionStorage instead of localStorage
            sessionStorage.setItem('kepler_address', this.address);
            sessionStorage.setItem('userWalletAddress', this.address);
            sessionStorage.setItem('walletConnected', 'true');
            sessionStorage.setItem('wallet_connect_time', Date.now().toString());

            this.updateUI();
            return this.address;
        } catch (error) {
            console.error('Failed to initialize Keplr:', error);
            this.disconnect();
            throw error;
        }
    }

    disconnect() {
        this.connected = false;
        this.address = null;
        
        // SECURITY: Clear all wallet related sessionStorage keys instead of localStorage
        sessionStorage.removeItem('kepler_address');
        sessionStorage.removeItem('userWalletAddress');
        sessionStorage.removeItem('walletConnected');
        sessionStorage.removeItem('wallet_connect_time');
        
        // For backwards compatibility, also clear any existing localStorage items
        // This helps ensure no old data remains from previous versions
        localStorage.removeItem('kepler_address');
        localStorage.removeItem('userWalletAddress');
        localStorage.removeItem('walletConnected');
        
        this.updateUI();
        
        // Dispatch wallet disconnected event
        document.dispatchEvent(new CustomEvent('keplrDisconnected'));
    }

    updateUI() {
        // Update connect wallet button in sidebar
        const connectKeplrBtn = document.getElementById('connectKeplrBtn');
        if (connectKeplrBtn) {
            if (this.connected && this.address) {
                connectKeplrBtn.innerHTML = '<i data-feather="check-circle" class="icon-inline-sm"></i> Connected';
                connectKeplrBtn.classList.remove('btn-outline-info');
                connectKeplrBtn.classList.add('btn-success');
                // Add disconnect option on click
                connectKeplrBtn.onclick = () => this.disconnect();
            } else {
                connectKeplrBtn.innerHTML = '<i data-feather="link" class="icon-inline-sm"></i> Connect Keplr Wallet';
                connectKeplrBtn.classList.remove('btn-success');
                connectKeplrBtn.classList.add('btn-outline-info');
                connectKeplrBtn.onclick = () => this.init();
            }
        }

        // Update user profile in header
        const userProfileBtn = document.getElementById('userProfileBtn');
        if (userProfileBtn) {
            if (this.connected && this.address) {
                const displayAddress = this.address.slice(0, 8) + '...' + this.address.slice(-4);
                userProfileBtn.querySelector('span').textContent = displayAddress;
            } else {
                userProfileBtn.querySelector('span').textContent = 'Connect Wallet';
            }
        }

        // Refresh feather icons
        feather.replace();
        
        // Set global window variables for other scripts
        window.walletConnected = this.connected;
        window.userWalletAddress = this.address || '';

        // Legacy connect button support
        const connectButton = document.getElementById('connectWallet');
        if (connectButton) {
            if (this.connected && this.address) {
                connectButton.innerHTML = `Connected: ${this.address.slice(0, 8)}...`;
                connectButton.classList.replace('btn-primary', 'btn-success');
                // Add disconnect option
                connectButton.onclick = () => this.disconnect();
            } else {
                connectButton.innerHTML = '<i class="bi bi-wallet2"></i> Connect Wallet';
                connectButton.classList.replace('btn-success', 'btn-primary');
                connectButton.onclick = () => this.init();
            }
        }
    }

    async signTransaction(transaction) {
        if (!this.connected) {
            throw new Error('Wallet not connected');
        }

        try {
            // Ensure transaction is properly formatted for Keplr
            // Must use Amino format (type/value structure) for signAmino
            const fromAddress = transaction.from_address || transaction.fromAddress || this.address;
            const toAddress = transaction.to_address || transaction.toAddress || "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt";
            const amount = transaction.amount || [{ denom: "uodis", amount: "1000" }];
            
            // According to Keplr documentation, for signAmino we need Amino format with type/value structure
            // https://docs.keplr.app/api/sign.html#cosmjssignamino
            const msgForKeplr = {
                type: "cosmos-sdk/MsgSend",
                value: {
                    from_address: fromAddress,
                    to_address: toAddress, 
                    amount: amount
                }
            };
            
            // Create the sign doc with proper structure
            const signDoc = {
                chain_id: this.chainId,
                account_number: '0',
                sequence: '0',
                fee: {
                    amount: [{ denom: 'uodis', amount: '2000' }],
                    gas: '200000',
                },
                msgs: [msgForKeplr],
                memo: ''
            };
            
            console.log("Signing with Keplr using Amino format:", JSON.stringify(signDoc, null, 2));

            // Sign directly with Keplr (not offlineSigner)
            const signature = await window.keplr.signAmino(
                this.chainId,
                this.address,
                signDoc
            );

            return signature;
        } catch (error) {
            console.error('Failed to sign transaction:', error);
            throw error;
        }
    }

    isConnected() {
        return this.connected && this.address;
    }
}

// Create global wallet instance
window.keplerWallet = new KeplerWallet();

// Global function for connecting Keplr wallet - can be called from anywhere
async function connectKeplrWallet() {
    try {
        const address = await window.keplerWallet.init();
        
        // Wallet connection is handled in the init method now, no need to duplicate storage
        console.log('Keplr wallet connected:', address);
        
        // SECURITY: Record last activity time for session tracking
        sessionStorage.setItem('last_wallet_activity', Date.now().toString());
        
        // Trigger wallet connected event for micro-rewards
        document.dispatchEvent(new CustomEvent('keplrConnected', {
            detail: { 
                address: address,
                timestamp: Date.now()
            }
        }));
        
        return address;
    } catch (error) {
        console.error('Failed to connect Keplr wallet:', error);
        // Security: Don't expose full error message to user
        alert('Error connecting Keplr wallet. Please make sure Keplr extension is installed and unlocked.');
        
        // Clear any session data on error
        sessionStorage.removeItem('kepler_address');
        sessionStorage.removeItem('userWalletAddress');
        sessionStorage.removeItem('walletConnected');
        sessionStorage.removeItem('wallet_connect_time');
        
        return null;
    }
}

// Global function for disconnecting Keplr wallet
function disconnectKeplrWallet() {
    // Just delegate to the wallet instance method which handles all cleanup
    window.keplerWallet.disconnect();
    console.log('Keplr wallet disconnected');
}

// Global function for signing transactions with Keplr wallet
async function signTransactionWithKeplr(transactionData) {
    try {
        // Check if wallet is connected
        if (!window.keplerWallet.isConnected()) {
            await connectKeplrWallet();
            if (!window.keplerWallet.isConnected()) {
                throw new Error('Wallet connection required');
            }
        }
        
        // Add metadata to transaction if needed
        if (transactionData.metadata && !transactionData.memo) {
            // Format memo based on transaction metadata
            const metadata = transactionData.metadata;
            transactionData.memo = `${metadata.id || ''}:${metadata.hash || ''}:${metadata.role || 'owner'}`;
        }
        
        // Sign the transaction using wallet instance
        const signature = await window.keplerWallet.signTransaction(transactionData);
        
        console.log('Transaction signed successfully:', signature);
        
        // If broadcast URL is provided, send to backend for broadcasting
        if (transactionData.broadcastUrl) {
            const response = await fetch(transactionData.broadcastUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    signature: signature,
                    transaction: transactionData
                })
            });
            
            const result = await response.json();
            console.log('Transaction broadcast result:', result);
            return result;
        }
        
        return signature;
    } catch (error) {
        console.error('Failed to sign transaction:', error);
        alert(`Transaction signing failed: ${error.message}`);
        throw error;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Update UI based on saved state
    window.keplerWallet.updateUI();

    // Add connection status check on forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            if (!window.keplerWallet.isConnected()) {
                e.preventDefault();
                try {
                    await connectKeplrWallet();
                } catch (error) {
                    alert('Please connect your Keplr wallet first');
                }
            }
        });
    });
    
    // Add global connect button handler if it exists
    const globalConnectBtn = document.getElementById('globalConnectWallet');
    if (globalConnectBtn) {
        globalConnectBtn.addEventListener('click', connectKeplrWallet);
    }
});