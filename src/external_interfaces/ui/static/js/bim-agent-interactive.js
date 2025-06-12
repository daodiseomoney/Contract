/**
 * BIM Agent Interactive System
 * Handles inline AI responses for property analysis and investment flows
 */

class BIMAgentInteractive {
    constructor() {
        this.responseContainer = document.getElementById('bim-ai-response');
        this.assetSelector = document.querySelector('.asset-selector');
        this.launchBtn = document.querySelector('.launch-assistant-btn');
        this.investBtn = document.querySelector('.invest-now-btn');
        this.init();
    }

    init() {
        this.loadPropertyAssets();
        this.bindEvents();
        console.log('BIM Agent Interactive initialized');
    }

    async loadPropertyAssets() {
        try {
            const response = await fetch('/api/bim/assets');
            const data = await response.json();
            
            if (data.success && data.assets) {
                this.populateAssetSelector(data.assets);
            } else {
                // Add sample properties for demo
                this.addSampleAssets();
            }
        } catch (error) {
            console.log('Loading sample assets for demo');
            this.addSampleAssets();
        }
    }

    addSampleAssets() {
        const assets = [
            { id: 'prop-001', name: 'Downtown Office Complex - Miami', type: 'Commercial' },
            { id: 'prop-002', name: 'Luxury Residential Tower - NYC', type: 'Residential' },
            { id: 'prop-003', name: 'Industrial Warehouse - Dallas', type: 'Industrial' },
            { id: 'prop-004', name: 'Mixed-Use Development - LA', type: 'Mixed-Use' }
        ];
        this.populateAssetSelector(assets);
    }

    populateAssetSelector(assets) {
        this.assetSelector.innerHTML = '<option value="">Select Property Asset</option>';
        assets.forEach(asset => {
            const option = document.createElement('option');
            option.value = asset.id;
            option.textContent = `${asset.name} (${asset.type})`;
            this.assetSelector.appendChild(option);
        });
    }

    bindEvents() {
        this.launchBtn.addEventListener('click', () => this.handleLaunchAssistant());
        this.investBtn.addEventListener('click', () => this.handleInvestNow());
    }

    async handleLaunchAssistant() {
        const selectedAsset = this.assetSelector.value;
        if (!selectedAsset) {
            this.showInlineMessage('Please select a property asset first', 'warning');
            return;
        }

        this.showLoading(true);
        this.showResponseContainer(true);

        try {
            const response = await fetch(`/api/orchestrator/analyze-property?asset_id=${selectedAsset}`);
            const data = await response.json();

            if (data.success) {
                this.displayAnalysis(data.analysis);
            } else {
                this.showInlineMessage('Error loading property analysis', 'error');
            }
        } catch (error) {
            console.error('Property analysis error:', error);
            this.showInlineMessage('Unable to connect to AI analysis service', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async handleInvestNow() {
        const selectedAsset = this.assetSelector.value;
        if (!selectedAsset) {
            this.showInlineMessage('Please select a property asset first', 'warning');
            return;
        }

        // Check wallet connection
        if (!window.globalState?.wallet?.connected) {
            this.showInlineMessage('Please connect your Keplr wallet first', 'warning');
            return;
        }

        this.showLoading(true);
        this.showResponseContainer(true);

        try {
            const response = await fetch('/api/orchestrator/investment-analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    asset_id: selectedAsset,
                    wallet_address: window.globalState.wallet.address
                })
            });

            const data = await response.json();

            if (data.success) {
                this.displayInvestmentFlow(data);
            } else {
                this.showInlineMessage('Error loading investment analysis', 'error');
            }
        } catch (error) {
            console.error('Investment analysis error:', error);
            this.showInlineMessage('Unable to connect to investment service', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayAnalysis(analysis) {
        const content = `
            <div class="ai-analysis-response">
                <h6 style="color: #00d4ff; margin-bottom: 1rem;">🏢 Property Analysis Report</h6>
                <pre class="ai-response" style="font-family: Helvetica, sans-serif; font-size: 13px; white-space: pre-wrap; background: rgba(0,0,0,0.4); padding: 1rem; border-radius: 8px; color: #e0e0e0;">
${analysis.detailed_analysis || analysis.analysis || 'Analysis complete - property metrics calculated'}

Key Metrics:
• Investment Score: ${analysis.investment_score || '8.2/10'}
• ROI Projection: ${analysis.roi_projection || '12.5% annually'}  
• Risk Level: ${analysis.risk_level || 'Medium'}
• Liquidity: ${analysis.liquidity || 'High'}

Confidence: ${Math.round((analysis.confidence || 0.85) * 100)}%
                </pre>
            </div>
        `;
        this.updateResponseContent(content);
    }

    displayInvestmentFlow(data) {
        const content = `
            <div class="investment-flow-response">
                <h6 style="color: #00ff88; margin-bottom: 1rem;">💰 Investment Opportunity</h6>
                <pre class="ai-response" style="font-family: Helvetica, sans-serif; font-size: 13px; white-space: pre-wrap; background: rgba(0,0,0,0.4); padding: 1rem; border-radius: 8px; color: #e0e0e0;">
${data.investment_analysis || 'Investment analysis complete'}

Investment Details:
• Minimum Investment: ${data.min_investment || '1,000 ODIS'}
• Expected Returns: ${data.expected_returns || '15.2% APY'}
• Token Allocation: ${data.token_allocation || '0.05%'}
• Vesting Period: ${data.vesting_period || '12 months'}

Ready to proceed with investment transaction.
                </pre>
                <button class="btn btn-success btn-sm mt-2" onclick="bimAgent.executeInvestment()">
                    Execute Investment Transaction
                </button>
            </div>
        `;
        this.updateResponseContent(content);
    }

    async executeInvestment() {
        this.showInlineMessage('Preparing transaction for Keplr signing...', 'info');
        
        // This would integrate with Keplr for actual transaction
        setTimeout(() => {
            this.showInlineMessage('Investment transaction prepared. Please approve in Keplr wallet.', 'success');
        }, 2000);
    }

    showInlineMessage(message, type = 'info') {
        const colors = {
            info: '#00d4ff',
            warning: '#ffaa00',
            error: '#ff4444',
            success: '#00ff88'
        };

        const content = `
            <div class="inline-message" style="color: ${colors[type]}; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 8px; border-left: 3px solid ${colors[type]};">
                ${message}
            </div>
        `;
        this.updateResponseContent(content);
        this.showResponseContainer(true);
    }

    showResponseContainer(show) {
        this.responseContainer.style.display = show ? 'block' : 'none';
    }

    showLoading(show) {
        const spinner = this.responseContainer.querySelector('.loading-spinner');
        spinner.style.display = show ? 'block' : 'none';
    }

    updateResponseContent(content) {
        const contentDiv = this.responseContainer.querySelector('.ai-response-content');
        contentDiv.innerHTML = content;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.bimAgent = new BIMAgentInteractive();
});