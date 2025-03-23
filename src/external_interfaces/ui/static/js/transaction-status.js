class TransactionTracker {
    constructor(transactionId) {
        this.transactionId = transactionId;
        this.steps = ['upload', 'tokenize', 'signatures', 'blockchain'];
        this.currentStep = 0;
        this.polling = null;
        this.retryCount = 0;
        this.maxRetries = 30; // 90 seconds total with 3s interval
    }

    async start() {
        this.showLoadingState();
        await this.pollTransactionStatus();
        this.startPolling();
    }

    showLoadingState() {
        document.querySelector('.loading-state').style.display = 'block';
        document.querySelector('.error-state').style.display = 'none';
        document.querySelector('.pending-state').style.display = 'none';
        document.querySelector('.confirmed-state').style.display = 'none';
    }

    startPolling() {
        if (this.polling) {
            clearInterval(this.polling);
        }
        this.polling = setInterval(() => this.pollTransactionStatus(), 3000);
    }

    stopPolling() {
        if (this.polling) {
            clearInterval(this.polling);
            this.polling = null;
        }
    }

    async pollTransactionStatus() {
        try {
            if (this.retryCount >= this.maxRetries) {
                this.handleError("Transaction timeout. Please check the explorer for updates.");
                this.stopPolling();
                return;
            }

            const response = await fetch(`/api/transaction/${this.transactionId}`);
            const transaction = await response.json();

            if (!response.ok) {
                throw new Error(transaction.error || 'Failed to fetch transaction status');
            }

            this.updateStatus(transaction);
            this.retryCount++;

        } catch (error) {
            console.error('Error polling transaction status:', error);
            this.handleError(error.message);
        }
    }

    updateStatus(transaction) {
        // Hide loading state
        document.querySelector('.loading-state').style.display = 'none';

        if (transaction.error) {
            this.handleError(transaction.error);
            return;
        }

        const signedCount = Object.values(transaction.signatures || {})
            .filter(s => s === 'signed').length;
        const totalSigners = Object.keys(transaction.signatures || {}).length;

        if (!transaction.blockchain_tx_hash) {
            // Show pending state
            document.querySelector('.pending-state').style.display = 'block';
            document.querySelector('.confirmed-state').style.display = 'none';

            // Update signature progress if available
            if (totalSigners > 0) {
                const signatureStatus = document.querySelector('.pending-state .signature-status');
                if (signatureStatus) {
                    signatureStatus.textContent = `Signatures: ${signedCount}/${totalSigners}`;
                }
            }
        } else {
            // Show confirmed state
            document.querySelector('.pending-state').style.display = 'none';
            document.querySelector('.confirmed-state').style.display = 'block';

            // Update confirmed transaction details
            document.querySelector('.confirmed-state .tx-hash').textContent = transaction.blockchain_tx_hash;
            document.querySelector('.confirmed-state .created-at').textContent = new Date(transaction.created_at).toLocaleString();
            document.querySelector('.confirmed-state .role').textContent = transaction.metadata?.role || 'N/A';

            // Update explorer link
            const explorerLink = document.querySelector('.confirmed-state .explorer-link');
            if (explorerLink && transaction.explorer_url) {
                explorerLink.href = transaction.explorer_url;
            }

            this.stopPolling();
        }
    }

    handleError(error) {
        document.querySelector('.loading-state').style.display = 'none';
        document.querySelector('.pending-state').style.display = 'none';
        document.querySelector('.confirmed-state').style.display = 'none';

        const errorState = document.querySelector('.error-state');
        errorState.style.display = 'block';
        errorState.querySelector('.error-message').textContent = error;
    }
}

// Initialize tracker when transaction ID is available
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const transactionId = params.get('id');

    if (transactionId) {
        const tracker = new TransactionTracker(transactionId);
        tracker.start();
    } else {
        const container = document.querySelector('.transaction-status');
        if (container) {
            container.innerHTML = '<div class="alert alert-warning">No transaction ID provided</div>';
        }
    }
});