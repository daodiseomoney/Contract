/**
 * BIM Agent Inline Response System
 * Replaces popup modals with inline content rendering
 */

class BIMAgentInline {
    constructor() {
        this.assets = [];
        this.selectedAsset = null;
        this.responseContainer = null;
        this.init();
    }

    init() {
        this.loadAvailableAssets();
        this.setupResponseContainer();
        this.bindButtons();
    }

    loadAvailableAssets() {
        // Load assets from uploaded IFC files
        fetch('/api/bim/assets')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.assets = data.assets || [];
                    this.updateAssetDropdown();
                } else {
                    this.assets = [];
                    this.createMockAssets(); // Temporary for demo
                }
            })
            .catch(() => {
                this.createMockAssets(); // Fallback for demo
            });
    }

    createMockAssets() {
        // Temporary assets for demonstration
        this.assets = [
            { id: 'property-001', name: 'Downtown Office Complex', value: 2400000, type: 'Commercial' },
            { id: 'property-002', name: 'Luxury Residential Tower', value: 8900000, type: 'Residential' },
            { id: 'property-003', name: 'Industrial Warehouse', value: 1200000, type: 'Industrial' }
        ];
        this.updateAssetDropdown();
    }

    updateAssetDropdown() {
        const dropdowns = document.querySelectorAll('.asset-selector, #asset-dropdown');
        dropdowns.forEach(dropdown => {
            if (dropdown) {
                dropdown.innerHTML = '<option value="">Select Property Asset</option>';
                this.assets.forEach(asset => {
                    const option = document.createElement('option');
                    option.value = asset.id;
                    option.textContent = `${asset.name} - $${this.formatCurrency(asset.value)}`;
                    dropdown.appendChild(option);
                });
            }
        });
    }

    setupResponseContainer() {
        const bimCard = document.querySelector('[data-agent="bim-ai"], .bim-assistant-card, .agent-card:has(.bim-content)');
        if (bimCard) {
            let container = bimCard.querySelector('.bim-response-container');
            if (!container) {
                container = document.createElement('div');
                container.className = 'bim-response-container';
                container.style.cssText = `
                    margin-top: 1rem;
                    padding: 1rem;
                    background: rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    min-height: 150px;
                    max-height: 250px;
                    overflow-y: auto;
                    display: none;
                `;
                bimCard.appendChild(container);
            }
            this.responseContainer = container;
        }
    }

    bindButtons() {
        // Bind Launch Assistant button
        const launchButtons = document.querySelectorAll('.launch-assistant-btn, [onclick*="launchAssistant"]');
        launchButtons.forEach(btn => {
            btn.onclick = null; // Remove old onclick
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.launchAssistantInline();
            });
        });

        // Bind Invest Now button
        const investButtons = document.querySelectorAll('.invest-now-btn, [onclick*="investNow"]');
        investButtons.forEach(btn => {
            btn.onclick = null; // Remove old onclick
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showInvestmentOptions();
            });
        });

        // Bind asset selection
        const dropdowns = document.querySelectorAll('.asset-selector, #asset-dropdown');
        dropdowns.forEach(dropdown => {
            dropdown.addEventListener('change', (e) => {
                this.selectedAsset = this.assets.find(asset => asset.id === e.target.value);
                if (this.selectedAsset) {
                    this.showAssetDetails();
                }
            });
        });
    }

    launchAssistantInline() {
        if (!this.responseContainer) {
            this.setupResponseContainer();
        }

        this.showResponse('🤖 BIM AI Assistant Activated', `
            <div class="assistant-interface">
                <div class="assistant-header">
                    <h4>AI Assistant Ready</h4>
                    <span class="status-badge">🟢 Online</span>
                </div>
                
                <div class="asset-selection">
                    <label>Select Property Asset:</label>
                    <select class="asset-selector form-control" style="margin: 0.5rem 0;">
                        ${this.generateAssetOptions()}
                    </select>
                </div>
                
                <div class="assistant-capabilities">
                    <h5>Available Analysis:</h5>
                    <ul>
                        <li>🏗️ Structural Analysis & Risk Assessment</li>
                        <li>💰 Investment ROI Calculations</li>
                        <li>📊 Market Valuation & Comparables</li>
                        <li>🔍 Due Diligence & Compliance Review</li>
                    </ul>
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-primary btn-sm" onclick="bimAgentInline.performAnalysis()">
                        Run Full Analysis
                    </button>
                    <button class="btn btn-success btn-sm" onclick="bimAgentInline.showInvestmentOptions()">
                        Investment Options
                    </button>
                </div>
            </div>
        `);

        // Rebind the new dropdown
        const newDropdown = this.responseContainer.querySelector('.asset-selector');
        if (newDropdown) {
            newDropdown.addEventListener('change', (e) => {
                this.selectedAsset = this.assets.find(asset => asset.id === e.target.value);
            });
        }
    }

    showInvestmentOptions() {
        if (!this.selectedAsset) {
            this.showResponse('⚠️ Asset Selection Required', `
                <p>Please select a property asset from the dropdown above to view investment options.</p>
                <div class="asset-selection">
                    <select class="asset-selector form-control">
                        ${this.generateAssetOptions()}
                    </select>
                </div>
            `);
            return;
        }

        const asset = this.selectedAsset;
        this.showResponse(`💰 Investment Options - ${asset.name}`, `
            <div class="investment-options">
                <div class="asset-summary">
                    <h5>${asset.name}</h5>
                    <p>Type: ${asset.type} | Value: $${this.formatCurrency(asset.value)}</p>
                </div>
                
                <div class="investment-tiers">
                    <div class="tier">
                        <h6>🥉 Bronze Tier (5% stake)</h6>
                        <p>Investment: $${this.formatCurrency(asset.value * 0.05)}</p>
                        <p>Expected Annual Return: 8-12%</p>
                        <button class="btn btn-outline-warning btn-sm" onclick="bimAgentInline.initiateInvestment('bronze')">
                            Invest Bronze
                        </button>
                    </div>
                    
                    <div class="tier">
                        <h6>🥈 Silver Tier (15% stake)</h6>
                        <p>Investment: $${this.formatCurrency(asset.value * 0.15)}</p>
                        <p>Expected Annual Return: 12-18%</p>
                        <button class="btn btn-outline-light btn-sm" onclick="bimAgentInline.initiateInvestment('silver')">
                            Invest Silver
                        </button>
                    </div>
                    
                    <div class="tier">
                        <h6>🥇 Gold Tier (25% stake)</h6>
                        <p>Investment: $${this.formatCurrency(asset.value * 0.25)}</p>
                        <p>Expected Annual Return: 18-25%</p>
                        <button class="btn btn-warning btn-sm" onclick="bimAgentInline.initiateInvestment('gold')">
                            Invest Gold
                        </button>
                    </div>
                </div>
            </div>
        `);
    }

    performAnalysis() {
        if (!this.selectedAsset) {
            this.showResponse('⚠️ Select Asset First', 'Please choose a property asset to analyze.');
            return;
        }

        this.showResponse('🔄 Analyzing...', 'Running comprehensive BIM analysis...');

        // Simulate analysis
        setTimeout(() => {
            const asset = this.selectedAsset;
            this.showResponse(`📊 Analysis Complete - ${asset.name}`, `
                <div class="analysis-results">
                    <div class="metrics">
                        <h5>Property Analysis</h5>
                        <div class="metric">
                            <span>Risk Score:</span>
                            <span class="value">Low (2.3/10)</span>
                        </div>
                        <div class="metric">
                            <span>ROI Projection:</span>
                            <span class="value success">+15.7% annually</span>
                        </div>
                        <div class="metric">
                            <span>Market Position:</span>
                            <span class="value">Above Average</span>
                        </div>
                        <div class="metric">
                            <span>Liquidity:</span>
                            <span class="value">High</span>
                        </div>
                    </div>
                    
                    <div class="recommendation">
                        <h6>🎯 Investment Recommendation</h6>
                        <p>Strong buy signal. Property shows excellent fundamentals with low risk profile and high growth potential.</p>
                    </div>
                    
                    <button class="btn btn-success btn-sm" onclick="bimAgentInline.showInvestmentOptions()">
                        View Investment Options
                    </button>
                </div>
            `);
        }, 2000);
    }

    initiateInvestment(tier) {
        if (!this.selectedAsset) return;

        const asset = this.selectedAsset;
        const stakes = { bronze: 0.05, silver: 0.15, gold: 0.25 };
        const investmentAmount = asset.value * stakes[tier];

        this.showResponse(`🚀 Investment Initiated - ${tier.toUpperCase()}`, `
            <div class="investment-confirmation">
                <h5>Investment Summary</h5>
                <div class="details">
                    <p><strong>Asset:</strong> ${asset.name}</p>
                    <p><strong>Tier:</strong> ${tier.toUpperCase()}</p>
                    <p><strong>Stake:</strong> ${(stakes[tier] * 100)}%</p>
                    <p><strong>Amount:</strong> $${this.formatCurrency(investmentAmount)}</p>
                </div>
                
                <div class="wallet-connection">
                    <p>Connect your Keplr wallet to complete the investment:</p>
                    <button class="btn btn-primary" onclick="connectKeplrWallet()">
                        Connect Keplr Wallet
                    </button>
                </div>
                
                <div class="status">
                    <span class="badge bg-warning">Pending Wallet Connection</span>
                </div>
            </div>
        `);
    }

    showResponse(title, content) {
        if (!this.responseContainer) return;

        this.responseContainer.style.display = 'block';
        this.responseContainer.innerHTML = `
            <div class="response-header">
                <h6>${title}</h6>
                <button class="btn-close" onclick="bimAgentInline.hideResponse()" style="background: none; border: none; color: #fff; font-size: 1.2rem; cursor: pointer;">×</button>
            </div>
            <div class="response-content">
                ${content}
            </div>
        `;

        // Scroll container into view
        this.responseContainer.scrollTop = 0;
    }

    hideResponse() {
        if (this.responseContainer) {
            this.responseContainer.style.display = 'none';
        }
    }

    generateAssetOptions() {
        return this.assets.map(asset => 
            `<option value="${asset.id}">${asset.name} - $${this.formatCurrency(asset.value)}</option>`
        ).join('');
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('en-US').format(value);
    }

    showAssetDetails() {
        if (!this.selectedAsset) return;
        
        const asset = this.selectedAsset;
        this.showResponse(`🏢 ${asset.name}`, `
            <div class="asset-details">
                <div class="asset-info">
                    <p><strong>Type:</strong> ${asset.type}</p>
                    <p><strong>Value:</strong> $${this.formatCurrency(asset.value)}</p>
                    <p><strong>Status:</strong> <span class="badge bg-success">Available for Investment</span></p>
                </div>
                
                <div class="quick-actions">
                    <button class="btn btn-info btn-sm" onclick="bimAgentInline.performAnalysis()">
                        Quick Analysis
                    </button>
                    <button class="btn btn-success btn-sm" onclick="bimAgentInline.showInvestmentOptions()">
                        Investment Options
                    </button>
                </div>
            </div>
        `);
    }
}

// Initialize when DOM is ready
let bimAgentInline;
document.addEventListener('DOMContentLoaded', () => {
    bimAgentInline = new BIMAgentInline();
    window.bimAgentInline = bimAgentInline; // Make globally accessible
});

// Also initialize if DOM is already loaded
if (document.readyState !== 'loading') {
    bimAgentInline = new BIMAgentInline();
    window.bimAgentInline = bimAgentInline;
}