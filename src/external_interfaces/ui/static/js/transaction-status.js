class TransactionTracker {
    constructor(transactionId) {
        this.transactionId = transactionId;
        this.steps = ['upload', 'tokenize', 'signatures', 'blockchain'];
        this.currentStep = 0;
        this.polling = null;
    }

    async start() {
        this.updateTimeline('upload', 'active');
        await this.pollTransactionStatus();
        this.startPolling();
    }

    startPolling() {
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
            const response = await fetch(`/api/transaction/${this.transactionId}`);
            const transaction = await response.json();
            
            if (response.ok) {
                this.updateStatus(transaction);
            } else {
                this.handleError(transaction.error);
            }
        } catch (error) {
            console.error('Error polling transaction status:', error);
            this.handleError(error.message);
        }
    }

    updateStatus(transaction) {
        // Update timeline based on transaction status
        const signedCount = Object.values(transaction.signatures)
            .filter(s => s === 'signed').length;
        const totalSigners = Object.keys(transaction.signatures).length;

        // Update step statuses
        this.updateTimeline('upload', 'completed');
        
        if (transaction.content_hash) {
            this.updateTimeline('tokenize', 'completed');
        }

        if (signedCount > 0) {
            this.updateTimeline('signatures', 'active');
            this.updateStepInfo('signatures', `${signedCount}/${totalSigners} signatures`);
        }
        
        if (signedCount === totalSigners) {
            this.updateTimeline('signatures', 'completed');
        }

        if (transaction.blockchain_tx_hash) {
            this.updateTimeline('blockchain', 'completed');
            this.updateStepInfo('blockchain', 
                `<a href="${transaction.explorer_url}" target="_blank">View on Explorer</a>`);
            this.stopPolling();
        }

        // Update transaction details
        this.updateTransactionDetails(transaction);
    }

    updateTimeline(step, status) {
        const stepElement = document.querySelector(`.timeline-step[data-step="${step}"]`);
        if (stepElement) {
            // Remove previous status classes
            stepElement.classList.remove('active', 'completed', 'error');
            stepElement.classList.add(status);
        }
    }

    updateStepInfo(step, info) {
        const infoElement = document.querySelector(`.timeline-step[data-step="${step}"] .step-info`);
        if (infoElement) {
            infoElement.innerHTML = info;
        }
    }

    updateTransactionDetails(transaction) {
        const detailsElement = document.querySelector('.transaction-details');
        if (detailsElement) {
            detailsElement.innerHTML = `
                <dl class="row">
                    <dt class="col-sm-3">Transaction ID</dt>
                    <dd class="col-sm-9">${transaction.transaction_id}</dd>
                    
                    <dt class="col-sm-3">Status</dt>
                    <dd class="col-sm-9">${transaction.status}</dd>
                    
                    <dt class="col-sm-3">File</dt>
                    <dd class="col-sm-9">${transaction.metadata.file_path}</dd>
                    
                    <dt class="col-sm-3">Budget Splits</dt>
                    <dd class="col-sm-9">
                        ${Object.entries(transaction.metadata.budget_splits)
                            .map(([role, percentage]) => `${role}: ${percentage}%`)
                            .join('<br>')}
                    </dd>
                    
                    <dt class="col-sm-3">Created At</dt>
                    <dd class="col-sm-9">${new Date(transaction.created_at).toLocaleString()}</dd>
                    
                    ${transaction.blockchain_tx_hash ? `
                        <dt class="col-sm-3">Explorer</dt>
                        <dd class="col-sm-9">
                            <a href="${transaction.explorer_url}" target="_blank">
                                View on Blockchain Explorer
                            </a>
                        </dd>
                    ` : ''}
                </dl>
            `;
        }
    }

    handleError(error) {
        this.updateTimeline(this.steps[this.currentStep], 'error');
        this.updateStepInfo(this.steps[this.currentStep], error);
        this.stopPolling();
    }
}

// Initialize tracker when transaction ID is available
document.addEventListener('DOMContentLoaded', () => {
    // Get transaction ID from URL parameter
    const params = new URLSearchParams(window.location.search);
    const transactionId = params.get('id');
    
    if (transactionId) {
        const tracker = new TransactionTracker(transactionId);
        tracker.start();
    } else {
        document.querySelector('.transaction-details').innerHTML = 
            '<div class="alert alert-warning">No transaction ID provided</div>';
    }
});
