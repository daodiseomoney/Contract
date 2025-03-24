// Kepler wallet integration
class KeplerWallet {
    constructor() {
        this.chainId = 'odiseotestnet_1234-1'; // Updated to match exact chainId expected by the system
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

    // Manually register the Odiseo testnet chain with Keplr
    async suggestOdiseoChain() {
        console.log("Suggesting Odiseo testnet chain to Keplr...");
        try {
            await window.keplr.experimentalSuggestChain({
                chainId: this.chainId,
                chainName: "Odiseo Testnet",
                rpc: "https://odiseo.test.rpc.nodeshub.online",
                rest: "https://odiseo.test.api.nodeshub.online",
                bip44: {
                    coinType: 118 // Standard Cosmos coin type
                },
                bech32Config: {
                    bech32PrefixAccAddr: "odiseo",
                    bech32PrefixAccPub: "odiseopub",
                    bech32PrefixValAddr: "odiseovaloper",
                    bech32PrefixValPub: "odiseovaloperpub",
                    bech32PrefixConsAddr: "odiseovalcons",
                    bech32PrefixConsPub: "odiseovalconspub"
                },
                currencies: [
                    {
                        coinDenom: "ODIS",
                        coinMinimalDenom: "uodis",
                        coinDecimals: 6
                    }
                ],
                feeCurrencies: [
                    {
                        coinDenom: "ODIS",
                        coinMinimalDenom: "uodis",
                        coinDecimals: 6,
                        gasPriceStep: {
                            low: 0.01,
                            average: 0.025,
                            high: 0.04
                        }
                    }
                ],
                stakeCurrency: {
                    coinDenom: "ODIS",
                    coinMinimalDenom: "uodis",
                    coinDecimals: 6
                }
            });
            console.log("Successfully suggested Odiseo testnet to Keplr");
            return true;
        } catch (error) {
            console.error("Failed to suggest Odiseo testnet to Keplr:", error);
            throw error;
        }
    }

    async init() {
        // Wait for Kepler to be injected
        if (!window.keplr) {
            throw new Error('Please install Keplr extension');
        }

        try {
            // First suggest the chain to Keplr
            await this.suggestOdiseoChain();

            // Enable the chain
            await window.keplr.enable(this.chainId);
            console.log("Keplr enabled for chain:", this.chainId);

            // Get the offline signer
            const offlineSigner = await window.keplr.getOfflineSigner(this.chainId);
            console.log("Got offline signer for chain");

            // Get user's address
            const accounts = await offlineSigner.getAccounts();
            console.log("Retrieved accounts:", accounts);
            
            if (accounts && accounts.length > 0) {
                this.address = accounts[0].address;
                this.connected = true;

                // Save connection state
                localStorage.setItem('kepler_address', this.address);
                console.log("Connected with address:", this.address);

                this.updateUI();
                return this.address;
            } else {
                throw new Error("No accounts found in Keplr wallet");
            }
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