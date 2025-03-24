// Initialize charts and data
function initializeCharts() {
    const ctx = document.getElementById('contractsChart')?.getContext('2d');
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Pending Signatures', 'Active', 'Completed'],
                datasets: [{
                    data: [0, 0, 0], // Will be updated by updateDashboardStats
                    backgroundColor: [
                        'rgba(255, 193, 7, 0.8)',  // warning yellow for pending
                        'rgba(40, 167, 69, 0.8)',  // success green for active
                        'rgba(23, 162, 184, 0.8)'  // info blue for completed
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        align: 'center'
                    }
                }
            }
        });
    }

    updateDashboardStats();
    updateRecentActivity();
    updateContractsTable();
}

// Update dashboard statistics
function updateDashboardStats() {
    fetch('/api/contracts')
        .then(response => response.json())
        .then(contracts => {
            const stats = {
                total: contracts.length,
                active: 0,
                pendingSignatures: 0,
                completed: 0
            };

            contracts.forEach(contract => {
                switch (contract.status) {
                    case 'completed':
                        stats.completed++;
                        break;
                    case 'pending_signatures':
                        stats.pendingSignatures++;
                        break;
                    case 'active':
                        stats.active++;
                        break;
                }
            });

            // Update chart if it exists
            const chart = Chart.getChart('contractsChart');
            if (chart) {
                chart.data.datasets[0].data = [
                    stats.pendingSignatures,
                    stats.active,
                    stats.completed
                ];
                chart.update();
            }

            // Update stats display
            const elements = {
                totalContracts: document.getElementById('totalContracts'),
                activeContracts: document.getElementById('activeContracts'),
                valueLocked: document.getElementById('valueLocked')
            };

            if (elements.totalContracts) {
                elements.totalContracts.textContent = stats.total;
            }
            if (elements.activeContracts) {
                elements.activeContracts.textContent = stats.active;
            }
            if (elements.valueLocked) {
                const totalValue = contracts.reduce((sum, contract) => {
                    const amount = parseInt(contract.metadata?.network?.amount || '0');
                    return sum + amount;
                }, 0);
                elements.valueLocked.textContent = formatValue(totalValue.toString());
            }
        })
        .catch(console.error);
}

// Update recent activity section with proper formatting
function updateRecentActivity() {
    const activityTable = document.querySelector('#recentTransactions tbody');
    if (!activityTable) return;

    fetch('/api/contracts')
        .then(response => response.json())
        .then(contracts => {
            if (!contracts || contracts.length === 0) {
                activityTable.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center text-muted">No recent transactions</td>
                    </tr>
                `;
                return;
            }

            // Sort by creation date (newest first)
            contracts.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

            // Take most recent 5
            const recentContracts = contracts.slice(0, 5);

            activityTable.innerHTML = recentContracts.map(contract => `
                <tr>
                    <td>${contract.transaction_id}</td>
                    <td>
                        <span class="badge bg-${getStatusBadgeColor(contract.status)}">
                            ${contract.status}
                        </span>
                    </td>
                    <td>${formatValue(contract.metadata?.network?.amount || '0')}</td>
                    <td>${formatDate(contract.created_at)}</td>
                </tr>
            `).join('');
        })
        .catch(error => {
            console.error('Error fetching recent activity:', error);
            activityTable.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-danger">
                        Error loading recent transactions
                    </td>
                </tr>
            `;
        });
}

// Helper function to format values
function formatValue(amount) {
    const value = parseInt(amount) / 1000000; // Convert from uodis to ODIS
    return `$${value.toFixed(2)}`;
}

// Helper function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Update contracts table with expandable details
function updateContractsTable() {
    const contractsTable = document.querySelector('#contractsTable tbody');
    if (!contractsTable) return;

    fetch('/api/contracts')
        .then(response => response.json())
        .then(contracts => {
            if (!contracts || contracts.length === 0) {
                contractsTable.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">No contracts found</td>
                    </tr>
                `;
                return;
            }

            contractsTable.innerHTML = contracts.map(contract => {
                const isNew = sessionStorage.getItem('last_transaction') &&
                    JSON.parse(sessionStorage.getItem('last_transaction')).transaction_id === contract.transaction_id;

                return `
                    <tr class="${isNew ? 'table-info' : ''}">
                        <td class="align-middle">
                            <button class="btn btn-link p-0 text-decoration-none"
                                    onclick="toggleDetails('${contract.transaction_id}')">
                                <i class="bi bi-chevron-down me-1" id="icon-${contract.transaction_id}"></i>
                                ${contract.transaction_id}
                            </button>
                        </td>
                        <td class="align-middle">${contract.metadata?.file_path || 'N/A'}</td>
                        <td class="align-middle">
                            <span class="badge bg-${getStatusBadgeColor(contract.status)}">
                                ${contract.status}
                            </span>
                        </td>
                        <td class="align-middle">${formatBudgetSplits(contract.metadata?.budget_splits)}</td>
                        <td class="align-middle">${formatDate(contract.created_at)}</td>
                        <td class="align-middle">
                            <button class="btn btn-success" onclick="signContract('${contract.transaction_id}')"
                                ${contract.status === 'completed' ? 'disabled' : ''}>
                                <i class="bi bi-pen"></i> Sign
                            </button>
                        </td>
                    </tr>
                    <tr id="details-${contract.transaction_id}" class="d-none">
                        <td colspan="6" class="p-0">
                            <div class="card border-0">
                                <div class="card-body bg-dark">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <h6 class="mb-3">Transaction Details</h6>
                                            <dl class="row mb-0">
                                                <dt class="col-sm-4">Content Hash</dt>
                                                <dd class="col-sm-8">
                                                    <code class="user-select-all">${contract.content_hash}</code>
                                                    <button class="btn btn-sm btn-outline-secondary ms-2"
                                                            onclick="navigator.clipboard.writeText('${contract.content_hash}')">
                                                        <i class="bi bi-clipboard"></i>
                                                    </button>
                                                </dd>

                                                <dt class="col-sm-4">Blockchain Tx</dt>
                                                <dd class="col-sm-8">
                                                    ${contract.blockchain_tx_hash ?
                                                        `<div class="d-flex align-items-center">
                                                            <code class="user-select-all">${contract.blockchain_tx_hash}</code>
                                                            <button class="btn btn-sm btn-outline-secondary ms-2"
                                                                    onclick="navigator.clipboard.writeText('${contract.blockchain_tx_hash}')">
                                                                <i class="bi bi-clipboard"></i>
                                                            </button>
                                                        </div>` :
                                                        '<span class="text-warning"><i class="bi bi-clock-history"></i> Pending...</span>'}
                                                </dd>

                                                <dt class="col-sm-4">Explorer</dt>
                                                <dd class="col-sm-8">
                                                    ${contract.explorer_url ?
                                                        `<a href="${contract.explorer_url}" target="_blank" class="btn btn-sm btn-primary">
                                                            <i class="bi bi-box-arrow-up-right"></i> View on Odiseo Explorer
                                                        </a>` :
                                                        '<span class="text-muted"><i class="bi bi-clock-history"></i> Not available yet</span>'}
                                                </dd>
                                            </dl>
                                        </div>
                                        <div class="col-md-6">
                                            <h6 class="mb-3">Signature Status</h6>
                                            <div class="d-flex flex-column gap-2">
                                                ${Object.entries(contract.signatures).map(([role, status]) => `
                                                    <div class="d-flex align-items-center justify-content-between border-bottom pb-2">
                                                        <div class="d-flex align-items-center">
                                                            <i class="bi bi-person-circle me-2"></i>
                                                            <span class="text-capitalize">${role}</span>
                                                        </div>
                                                        <span class="badge bg-${status === 'signed' ? 'success' : 'warning'}">
                                                            ${status === 'signed' ?
                                                                '<i class="bi bi-check-circle me-1"></i> Signed' :
                                                                '<i class="bi bi-clock me-1"></i> Pending'}
                                                        </span>
                                                    </div>
                                                `).join('')}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');

            // Clear the new transaction flag after showing it
            if (sessionStorage.getItem('last_transaction')) {
                sessionStorage.removeItem('last_transaction');
            }
        })
        .catch(error => {
            console.error('Error fetching contracts:', error);
            showError('Failed to load contracts');
        });
}

// Toggle contract details visibility
function toggleDetails(transactionId) {
    const detailsRow = document.getElementById(`details-${transactionId}`);
    const icon = document.getElementById(`icon-${transactionId}`);

    if (detailsRow.classList.contains('d-none')) {
        detailsRow.classList.remove('d-none');
        icon.classList.replace('bi-chevron-down', 'bi-chevron-up');
    } else {
        detailsRow.classList.add('d-none');
        icon.classList.replace('bi-chevron-up', 'bi-chevron-down');
    }
}

// Helper functions for contract display
function getStatusBadgeColor(status) {
    switch (status) {
        case 'completed':
            return 'success';
        case 'pending_signatures':
            return 'warning';
        case 'active':
            return 'primary';
        default:
            return 'secondary';
    }
}

function formatBudgetSplits(splits) {
    if (!splits) return 'N/A';
    return Object.entries(splits)
        .map(([role, percentage]) => `${role}: ${percentage}%`)
        .join(', ');
}

// Contract interaction functions
async function signContract(transactionId) {
    try {
        if (!window.keplr) {
            showError('Please install Keplr wallet extension');
            return;
        }

        console.log('Starting Keplr signing process...');

        // Get transaction details
        const response = await fetch(`/api/transaction/${transactionId}`);
        const transaction = await response.json();
        console.log('Transaction details:', transaction);

        const chainId = "odiseotestnet_1234-1";
        console.log('Using chain ID:', chainId);

        try {
            // Enable Keplr for the chain
            await window.keplr.enable(chainId);
            console.log('Keplr enabled for chain');

            // Get the offline signer
            const offlineSigner = await window.keplr.getOfflineSigner(chainId);
            console.log('Got offline signer');

            // Get user's address
            const accounts = await offlineSigner.getAccounts();
            const userAddress = accounts[0].address;
            console.log('User address:', userAddress);

            // Query account info from chain
            const accountResponse = await fetch(`/api/account?address=${userAddress}`);
            if (!accountResponse.ok) {
                throw new Error('Failed to fetch account data');
            }
            const accountData = await accountResponse.json();
            console.log('Account data:', accountData);

            // Get next unsigned role
            const nextRole = Object.entries(transaction.signatures)
                .find(([_, status]) => status !== 'signed')?.[0];

            if (!nextRole) {
                showError('No available roles to sign');
                return;
            }

            console.log('Signing as role:', nextRole);

            // Create proper message format according to Keplr docs
            // https://docs.keplr.app/api/guide/sign-a-message
            // Despite Keplr docs suggesting type/value structure for Amino,
            // testing shows it wants direct object format without type/value nesting
            
            const aminoDoc = {
                chain_id: chainId,
                account_number: accountData.account_number,
                sequence: accountData.sequence,
                fee: {
                    amount: [{ denom: "uodis", amount: "2500" }],
                    gas: "100000"
                },
                // Using correct Amino format WITH type/value structure for Keplr
                msgs: [{
                    type: "cosmos-sdk/MsgSend",
                    value: {
                        from_address: userAddress,
                        to_address: "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                        amount: [{ denom: "uodis", amount: "1000" }]
                    }
                }],
                memo: `tx:${transaction.transaction_id}|hash:${transaction.content_hash}|role:${nextRole}`
            };
            
            console.log("Amino signDoc for Keplr:", JSON.stringify(aminoDoc, null, 2));
            
            console.log('Requesting Keplr signature with params:', {
                chainId,
                userAddress,
                signDoc: JSON.stringify(aminoDoc),
                options: { preferNoSetFee: true }
            });
            
            // Add a try-catch specifically around the Keplr signing call
            let signResponse;
            try {
                // Make sure Keplr is available and the network is enabled
                if (!window.keplr) {
                    throw new Error("Keplr wallet not found. Please install Keplr extension and refresh the page.");
                }
                
                try {
                    // Explicitly enable chain
                    await window.keplr.enable(chainId);
                    console.log("Keplr enabled for chain");
                    
                    // Verify we can get an offline signer
                    const offlineSigner = await window.keplr.getOfflineSigner(chainId);
                    console.log("Got offline signer");
                    
                    // Verify accounts are accessible
                    const accounts = await offlineSigner.getAccounts();
                    if (!accounts || accounts.length === 0) {
                        throw new Error("No accounts found in Keplr wallet for this chain");
                    }
                    console.log("Accounts verified:", accounts.length);
                } catch (networkError) {
                    console.error("Keplr network check failed:", networkError);
                    throw new Error(`Network connection error: ${networkError.message}. Please check your Keplr wallet connection.`);
                }
                
                // Validate transaction structure before sending to Keplr
                const requiredFields = ["chain_id", "account_number", "sequence", "fee", "msgs", "memo"];
                for (const field of requiredFields) {
                    if (!aminoDoc[field]) {
                        throw new Error(`Invalid transaction structure: Missing ${field}`);
                    }
                }
                
                console.log('Using signDirect with Keplr (Proto format)');
                
                // We're switching to use signDirect instead of signAmino
                // https://docs.keplr.app/api/sign.html#request-1
                
                // Convert from Amino to Proto format for direct signing
                const protoMsgs = aminoDoc.msgs.map(msg => {
                    return {
                        typeUrl: "/cosmos.bank.v1beta1.MsgSend",
                        value: {
                            fromAddress: msg.value.from_address,
                            toAddress: msg.value.to_address,
                            amount: msg.value.amount
                        }
                    };
                });
                
                // For signDirect we need to encode the transaction
                // This is a simplified version - in production use actual protobuf encoding
                const bodyBytes = btoa(JSON.stringify({
                    messages: protoMsgs,
                    memo: aminoDoc.memo
                }));
                
                const authInfoBytes = btoa(JSON.stringify({
                    fee: {
                        amount: aminoDoc.fee.amount,
                        gasLimit: aminoDoc.fee.gas
                    }
                }));
                
                // Create the direct sign doc
                const directSignDoc = {
                    bodyBytes,
                    authInfoBytes,
                    chainId,
                    accountNumber: parseInt(aminoDoc.account_number)
                };
                
                // Log the exact document we're sending to Keplr
                console.log('Direct sign doc for Keplr:', JSON.stringify(directSignDoc, null, 2));
                
                // Use signDirect instead of signAmino
                const directSignResponse = await window.keplr.signDirect(
                    chainId,
                    userAddress,
                    directSignDoc
                );
                
                // Transform the response to match what our backend expects
                signResponse = {
                    signed: aminoDoc,
                    signature: {
                        pub_key: {
                            type: "tendermint/PubKeySecp256k1",
                            value: btoa(String.fromCharCode.apply(null, directSignResponse.pubKey))
                        },
                        signature: directSignResponse.signature
                    }
                };
                console.log('Got sign response from Keplr:', signResponse);
            } catch (signError) {
                console.error('Keplr signing error:', {
                    message: signError.message,
                    stack: signError.stack,
                    fullError: signError
                });
                throw signError;
            }

            // Send the complete signature response to backend without modifications
            const signResult = await fetch('/api/sign', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    transaction_id: transactionId,
                    role: nextRole,
                    signature: signResponse
                })
            });

            if (!signResult.ok) {
                const errorData = await signResult.json();
                throw new Error(errorData.error || 'Failed to process signature');
            }

            showSuccess('Successfully signed transaction');
            updateContractsTable();
            updateDashboardStats();
            updateRecentActivity();

        } catch (error) {
            console.error('Keplr signing error:', {
                message: error.message,
                stack: error.stack,
                fullError: error
            });
            showError(error.message || 'Failed to sign transaction');
        }
    } catch (error) {
        // Enhanced error logging for contract signing
        const errorContext = {
            message: error.message,
            stack: error.stack,
            fullError: error,
            transactionId: transactionId,
            userRole: role,
            timestamp: new Date().toISOString()
        };
        
        console.error('Contract signing error:', errorContext);
        
        // Try to extract specific Keplr error types
        let userFriendlyMessage = 'Failed to process contract signing';
        if (error.message.includes('User rejected')) {
            userFriendlyMessage = 'You declined the transaction request in Keplr';
        } else if (error.message.includes('wallet not found')) {
            userFriendlyMessage = 'Keplr wallet extension not detected. Please install Keplr and refresh the page.';
        } else if (error.message.includes('Invalid memo')) {
            userFriendlyMessage = 'Transaction failed: Invalid memo format';
        } else if (error.details && error.details.keplrErrorDetails) {
            userFriendlyMessage = error.details.keplrErrorDetails;
        }
        
        showError(userFriendlyMessage);
    }
}

// File upload handling
async function handleUpload(e) {
    e.preventDefault();

    // Ensure wallet is connected
    if (!window.keplerWallet?.isConnected()) {
        alert('Please connect your wallet first');
        return;
    }

    const formData = new FormData(e.target);
    const statusDiv = document.getElementById('uploadStatus');
    const contractPreview = document.getElementById('contractPreview');

    try {
        if (statusDiv) {
            statusDiv.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-arrow-repeat spin"></i> Uploading file...
                </div>
            `;
        }

        // First upload the file and get tokenization response in one request
        const uploadResponse = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            throw new Error(`Upload failed: ${uploadResponse.status}`);
        }

        const uploadResult = await uploadResponse.json();
        if (uploadResult.error) throw new Error(uploadResult.error);

        handleUploadSuccess(uploadResult);

    } catch (error) {
        // Enhanced error logging for uploads
        const errorContext = {
            message: error.message,
            stack: error.stack,
            fullError: error,
            responseStatus: uploadResponse?.status,
            responseStatusText: uploadResponse?.statusText,
            timestamp: new Date().toISOString(),
            formDataKeys: [...formData.keys()],
            hasFile: formData.has('file'),
            fileName: formData.get('file')?.name
        };
        
        console.error('Upload error:', errorContext);
        
        // Try to get more information from the response
        let errorMessage = error.message || 'An error occurred during upload';
        let additionalDetails = '';
        
        if (uploadResponse && !uploadResponse.ok) {
            // Clone and read the response if possible
            try {
                // This is async, but we'll log it for debugging
                uploadResponse.clone().text().then(text => {
                    console.error('Error response body:', text);
                    try {
                        const jsonResponse = JSON.parse(text);
                        console.error('Parsed error response:', jsonResponse);
                        
                        // Extract more specific error information if available
                        if (jsonResponse.error) {
                            additionalDetails = `Details: ${jsonResponse.error}`;
                        }
                    } catch (e) {
                        console.error('Error parsing response JSON:', e);
                    }
                }).catch(e => console.error('Error reading response body:', e));
            } catch (e) {
                console.error('Error accessing response body:', e);
            }
        }
        
        if (statusDiv) {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i> ${errorMessage}
                    ${additionalDetails ? `<div class="mt-2 small">${additionalDetails}</div>` : ''}
                </div>
            `;
        }
    }
}

// Handle successful upload
async function handleUploadSuccess(result) {
    if (result.transaction) {
        // Store transaction ID in session storage
        sessionStorage.setItem('last_transaction', JSON.stringify(result.transaction));

        // Update all displays immediately before redirect
        updateDashboardStats();
        updateRecentActivity();
        updateContractsTable();

        // Redirect to contracts page after short delay
        setTimeout(() => window.location.href = '/contracts', 1500);
    }
}

// Budget split field management
function addBudgetSplit() {
    const container = document.getElementById('budgetSplits');
    if (!container) return;

    const newSplit = document.createElement('div');
    newSplit.className = 'input-group mb-2';
    newSplit.innerHTML = `
        <span class="input-group-text"><i class="bi bi-person"></i></span>
        <input type="text" class="form-control" placeholder="Role" name="roles[]" required>
        <input type="number" class="form-control" placeholder="%" name="percentages[]" min="0" max="100" required>
        <button type="button" class="btn btn-outline-danger" onclick="this.parentElement.remove()">
            <i class="bi bi-trash"></i>
        </button>
    `;
    container.appendChild(newSplit);
}

// Utility functions for alerts
function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        <i class="bi bi-exclamation-triangle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container')?.prepend(alert);
}

function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.innerHTML = `
        <i class="bi bi-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container')?.prepend(alert);
}


// Add the base64 conversion utility function
function uint8ToBase64(u8Arr) {
    let binary = '';
    for (let i = 0; i < u8Arr.length; i++) {
        binary += String.fromCharCode(u8Arr[i]);
    }
    return window.btoa(binary);
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Handle file upload form
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUpload);
    }

    // Initialize contracts display if on contracts page
    if (document.getElementById('contractsChart')) {
        initializeCharts();
        // Refresh data every 30 seconds
        setInterval(updateDashboardStats, 30000);
        setInterval(updateRecentActivity, 30000);
        setInterval(updateContractsTable, 30000);
    }
});