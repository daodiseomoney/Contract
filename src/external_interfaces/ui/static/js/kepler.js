// Kepler wallet integration
class KeplerWallet {
    constructor() {
        this.chainId = 'odiseo_1234-1';
        this.connected = false;
        this.address = null;
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

            return this.address;
        } catch (error) {
            console.error('Failed to initialize Keplr:', error);
            throw error;
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
            const offlineSigner = window.keplr.getOfflineSigner(this.chainId);
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
}

// Create global wallet instance
window.keplerWallet = new KeplerWallet();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const connectButton = document.getElementById('connectWallet');
    if (connectButton) {
        connectButton.addEventListener('click', async () => {
            try {
                const address = await window.keplerWallet.init();
                connectButton.innerHTML = `Connected: ${address.slice(0, 8)}...`;
                connectButton.classList.replace('btn-primary', 'btn-success');
            } catch (error) {
                console.error('Failed to connect wallet:', error);
                alert(error.message);
            }
        });
    }
});
