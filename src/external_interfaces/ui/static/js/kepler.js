// Kepler wallet integration
class KeplerWallet {
    constructor() {
        this.chainId = 'odiseotestnet_1234-1';
        this.connected = false;
        this.address = null;

        // Try to restore previous connection - use both the legacy and new localStorage keys
        const savedAddress = localStorage.getItem('kepler_address') || localStorage.getItem('userWalletAddress');
        if (savedAddress) {
            this.address = savedAddress;
            this.connected = true;
            
            // Make sure we keep both storage keys in sync
            localStorage.setItem('kepler_address', savedAddress);
            localStorage.setItem('userWalletAddress', savedAddress);
            localStorage.setItem('walletConnected', 'true');
            
            this.updateUI();
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

            // Save connection state to both keys for compatibility
            localStorage.setItem('kepler_address', this.address);
            localStorage.setItem('userWalletAddress', this.address);
            localStorage.setItem('walletConnected', 'true');

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
        
        // Clear all wallet related localStorage keys
        localStorage.removeItem('kepler_address');
        localStorage.removeItem('userWalletAddress');
        localStorage.setItem('walletConnected', 'false');
        
        this.updateUI();
    }

    updateUI() {
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
        
        // Store wallet connected status in localStorage for UI components
        localStorage.setItem('walletConnected', 'true');
        localStorage.setItem('userWalletAddress', address);
        
        console.log('Keplr wallet connected:', address);
        
        // Trigger wallet connected event for micro-rewards
        document.dispatchEvent(new CustomEvent('keplrConnected', {
            detail: { address: address }
        }));
        
        return address;
    } catch (error) {
        console.error('Failed to connect Keplr wallet:', error);
        alert('Error connecting Keplr wallet: ' + error.message);
        localStorage.setItem('walletConnected', 'false');
        localStorage.removeItem('userWalletAddress');
        return null;
    }
}

// Global function for disconnecting Keplr wallet
function disconnectKeplrWallet() {
    window.keplerWallet.disconnect();
    localStorage.setItem('walletConnected', 'false');
    localStorage.removeItem('userWalletAddress');
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