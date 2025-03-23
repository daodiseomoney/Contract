// Kepler wallet integration
class KeplerWallet {
    constructor() {
        this.chainId = 'odiseo_1234-1';
        this.connected = false;
        this.address = null;

        // Try to restore previous connection
        const savedAddress = localStorage.getItem('kepler_address');
        if (savedAddress) {
            this.address = savedAddress;
            this.connected = true;
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

            // Save connection state
            localStorage.setItem('kepler_address', this.address);

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
        localStorage.removeItem('kepler_address');
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
            const signDoc = {
                chain_id: this.chainId,
                account_number: '0',
                sequence: '0',
                fee: {
                    amount: [{ amount: '2000', denom: 'uodis' }],
                    gas: '200000',
                },
                msgs: [transaction],
                memo: ''
            };

            // Sign the transaction
            const offlineSigner = await window.keplr.getOfflineSigner(this.chainId);
            const signature = await offlineSigner.signAmino(
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
                    await window.keplerWallet.init();
                } catch (error) {
                    alert('Please connect your Kepler wallet first');
                }
            }
        });
    });
});