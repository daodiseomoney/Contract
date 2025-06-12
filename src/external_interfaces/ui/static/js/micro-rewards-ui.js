/**
 * Micro-Rewards UI Components
 * Creates and manages the UI elements for the micro-rewards system
 */

import { MicroRewards } from './blockchain-animations.js';

// Rewards UI Manager
class RewardsUIManager {
  constructor() {
    // Initialize UI
    this.initialized = false;
    this.badgeElement = null;
    this.panelElement = null;
    this.isPanelVisible = false;
    
    // Rewards actions and points
    this.actionPoints = {
      'wallet_connect': 25,
      'contract_sign': 50,
      'transaction_submit': 100,
      'login': 10,
      'view_contract': 5,
      'upload_bim': 30,
      'share_property': 15,
      'join_validator': 75,
      'complete_profile': 20
    };
    
    // Action descriptions for UI
    this.actionDescriptions = {
      'wallet_connect': 'Connect Keplr wallet',
      'contract_sign': 'Sign a smart contract',
      'transaction_submit': 'Submit a blockchain transaction',
      'login': 'Log into the platform',
      'view_contract': 'View a property contract',
      'upload_bim': 'Upload a BIM model',
      'share_property': 'Share a property',
      'join_validator': 'Become a validator',
      'complete_profile': 'Complete your profile'
    };
    
    // Action icons (Feather icons)
    this.actionIcons = {
      'wallet_connect': 'link',
      'contract_sign': 'file-text',
      'transaction_submit': 'check-circle',
      'login': 'log-in',
      'view_contract': 'eye',
      'upload_bim': 'upload',
      'share_property': 'share-2',
      'join_validator': 'shield',
      'complete_profile': 'user-check'
    };
    
    // Define the rewards system achievements
    this.achievements = [
      {
        id: 'first_wallet_connect',
        icon: 'link',
        name: 'Connected Pioneer',
        description: 'Connect your Keplr wallet for the first time',
        condition: (state) => state.actions.walletConnected,
        points: 25
      },
      {
        id: 'first_contract',
        icon: 'file-text',
        name: 'Contract Signer',
        description: 'Sign your first smart contract',
        condition: (state) => state.actions.contractSigned,
        points: 50
      },
      {
        id: 'first_transaction',
        icon: 'send',
        name: 'Blockchain Trader',
        description: 'Submit your first blockchain transaction',
        condition: (state) => state.actions.transactionSubmitted,
        points: 100
      },
      {
        id: 'frequent_visitor',
        icon: 'award',
        name: 'Frequent Visitor',
        description: 'Log in 5 times',
        condition: (state) => state.actions.loginCount >= 5,
        points: 50
      },
      {
        id: 'contract_explorer',
        icon: 'search',
        name: 'Contract Explorer',
        description: 'View 10 different contracts',
        condition: (state) => state.actions.contractViews >= 10,
        points: 75
      }
    ];
    
    // Bind methods
    this.triggerAction = this.triggerAction.bind(this);
    this.toggleRewardsPanel = this.toggleRewardsPanel.bind(this);
    this.updateBadge = this.updateBadge.bind(this);
  }
  
  /**
   * Initialize the rewards UI
   */
  initialize() {
    if (this.initialized) return;
    
<<<<<<< HEAD
    // Check if rewards badge already exists in header (from wallet manager)
    const existingHeaderPoints = document.getElementById('pointsSystemBtn');
    if (existingHeaderPoints) {
      // Use existing header points system instead of creating duplicate
      this.badgeElement = existingHeaderPoints;
      this.initialized = true;
      return;
    }
    
    // Create rewards badge only if none exists
=======
    // Create rewards badge
>>>>>>> fb24633dab07b7e0a60328f87ead6e6396c2f113
    this.createRewardsBadge();
    
    // Create rewards panel
    this.createRewardsPanel();
    
    // Set up event listeners for user actions
    this.setupEventListeners();
    
    this.initialized = true;
  }
  
  /**
   * Create the rewards badge that shows user level and score
   */
  createRewardsBadge() {
    // Get rewards data
    const rewards = window.microRewards.getRewardsSummary();
    
    // Create badge element
    const badge = document.createElement('div');
    badge.className = 'rewards-badge';
    badge.id = 'rewards-badge';
    badge.innerHTML = `
      <div class="level-indicator">${rewards.level}</div>
      <div class="rewards-info">
        <div class="rewards-score">${rewards.score} pts</div>
        <div class="rewards-progress">
          <div class="rewards-progress-bar" style="width: ${rewards.progress}%"></div>
        </div>
      </div>
    `;
    
    // Add click event to toggle rewards panel
    badge.addEventListener('click', this.toggleRewardsPanel);
    
    // Add to DOM
    document.body.appendChild(badge);
    this.badgeElement = badge;
    
    // Apply pulse animation if there are new achievements
    if (this.hasNewAchievements()) {
      badge.classList.add('rewards-pulse');
    }
  }
  
  /**
   * Create the rewards panel that shows detailed information
   */
  createRewardsPanel() {
    // Get rewards data
    const rewards = window.microRewards.getRewardsSummary();
    
    // Create panel element
    const panel = document.createElement('div');
    panel.className = 'rewards-panel';
    panel.id = 'rewards-panel';
    
    // Create header
    const header = document.createElement('div');
    header.className = 'rewards-panel-header';
    header.innerHTML = `
      <div class="rewards-panel-title">Blockchain Rewards</div>
      <button class="rewards-panel-close" id="rewards-panel-close">×</button>
    `;
    panel.appendChild(header);
    
    // Create level summary
    const summary = document.createElement('div');
    summary.className = 'rewards-summary';
    summary.innerHTML = `
      <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
        <div class="level-indicator" style="width: 40px; height: 40px; font-size: 18px;">
          ${rewards.level}
        </div>
        <div>
          <div style="font-weight: bold; font-size: 16px;">Level ${rewards.level}</div>
          <div style="color: rgba(255,255,255,0.7); font-size: 12px;">
            ${rewards.score} points
            ${rewards.nextLevelAt ? `(${rewards.nextLevelAt - rewards.score} to next level)` : '(Max level)'}
          </div>
        </div>
      </div>
      <div class="rewards-progress" style="height: 8px; margin-bottom: 15px;">
        <div class="rewards-progress-bar" style="width: ${rewards.progress}%"></div>
      </div>
    `;
    panel.appendChild(summary);
    
    // Create achievements section
    const achievementsSection = document.createElement('div');
    achievementsSection.className = 'rewards-achievements';
    achievementsSection.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 10px; color: #00E5FF;">Achievements</div>
      <div style="display: flex; flex-wrap: wrap; gap: 5px;">
        ${this.renderAchievements()}
      </div>
    `;
    panel.appendChild(achievementsSection);
    
    // Create actions section
    const actionsSection = document.createElement('div');
    actionsSection.className = 'rewards-actions';
    actionsSection.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 10px; color: #00E5FF;">Actions & Points</div>
      <div>
        ${this.renderActions()}
      </div>
    `;
    panel.appendChild(actionsSection);
    
    // Add to DOM (hidden initially)
    document.body.appendChild(panel);
    this.panelElement = panel;
    
    // Add event listener to close button
    document.getElementById('rewards-panel-close').addEventListener('click', () => {
      this.toggleRewardsPanel(false);
    });
  }
  
  /**
   * Render the achievements section
   * @returns {string} HTML for achievements
   */
  renderAchievements() {
    const rewards = window.microRewards.getRewardsSummary();
    
    return this.achievements.map(achievement => {
      const isUnlocked = achievement.condition(rewards);
      const statusClass = isUnlocked ? '' : 'locked';
      
      return `
        <div class="achievement-badge ${statusClass}" title="${achievement.name}">
          <i data-feather="${achievement.icon}"></i>
          <div class="tooltip">${achievement.name}: ${achievement.description}</div>
        </div>
      `;
    }).join('');
  }
  
  /**
   * Render the actions section
   * @returns {string} HTML for actions
   */
  renderActions() {
    return Object.entries(this.actionPoints).map(([action, points]) => {
      return `
        <div class="rewards-action-item">
          <div class="rewards-action-name">
            <div class="rewards-action-icon">
              <i data-feather="${this.actionIcons[action]}"></i>
            </div>
            ${this.actionDescriptions[action]}
          </div>
          <div class="rewards-action-value">+${points}</div>
        </div>
      `;
    }).join('');
  }
  
  /**
   * Toggle the rewards panel visibility
   * @param {boolean|Event} show - True to show, false to hide, or event object
   */
  toggleRewardsPanel(show) {
    // Handle case when show is an event
    if (typeof show !== 'boolean') {
      // Toggle current state
      show = !this.isPanelVisible;
    }
    
    if (show) {
      this.panelElement.classList.add('visible');
      this.isPanelVisible = true;
      
      // Remove pulse effect when panel is opened
      if (this.badgeElement.classList.contains('rewards-pulse')) {
        this.badgeElement.classList.remove('rewards-pulse');
      }
      
      // Update feather icons inside panel
      setTimeout(() => {
        if (typeof feather !== 'undefined') {
          feather.replace();
        }
      }, 10);
    } else {
      this.panelElement.classList.remove('visible');
      this.isPanelVisible = false;
    }
  }
  
  /**
   * Setup event listeners for user actions
   */
  setupEventListeners() {
    // Listen for Keplr wallet connection
    document.addEventListener('keplrConnected', (e) => {
      this.triggerAction('wallet_connect', {
        animationContainer: 'app-container'
      });
    });
    
    // Listen for contract signing
    document.addEventListener('contractSigned', (e) => {
      this.triggerAction('contract_sign', {
        animationContainer: 'app-container'
      });
    });
    
    // Listen for transaction submissions
    document.addEventListener('transactionSubmitted', (e) => {
      this.triggerAction('transaction_submit', {
        animationContainer: 'app-container'
      });
    });
    
    // Listen for page views
    document.addEventListener('DOMContentLoaded', () => {
      // Check if user is viewing a contract page
      if (window.location.pathname.includes('/contracts')) {
        this.triggerAction('view_contract', {
          animationContainer: 'main-content'
        });
      }
      
      // Check if this is a login
      if (localStorage.getItem('walletConnected') === 'true') {
        this.triggerAction('login', {
          animationContainer: null
        });
      }
    });
  }
  
  /**
   * Trigger a rewards action
   * @param {string} action - The action type
   * @param {Object} options - Options for the action
   */
  triggerAction(action, options = {}) {
    // Check if action exists
    if (!this.actionPoints[action]) return;
    
    // Award points for the action
    const points = this.actionPoints[action];
    const result = window.microRewards.awardPoints(action, points, {
      animationContainer: options.animationContainer || null,
      onComplete: () => {
        // Update badge with new information
        this.updateBadge();
        
        // Apply pulse effect if new achievements
        if (this.hasNewAchievements()) {
          this.badgeElement.classList.add('rewards-pulse');
        }
        
        // Call options callback if provided
        if (options.onComplete) options.onComplete(result);
      }
    });
    
    return result;
  }
  
  /**
   * Update the rewards badge with latest information
   */
  updateBadge() {
    if (!this.badgeElement) return;
    
    // Get updated rewards data
    const rewards = window.microRewards.getRewardsSummary();
    
    // Update badge content
    this.badgeElement.innerHTML = `
      <div class="level-indicator">${rewards.level}</div>
      <div class="rewards-info">
        <div class="rewards-score">${rewards.score} pts</div>
        <div class="rewards-progress">
          <div class="rewards-progress-bar" style="width: ${rewards.progress}%"></div>
        </div>
      </div>
    `;
    
    // Update panel if it exists
    if (this.panelElement) {
      // Update level info
      const summary = this.panelElement.querySelector('.rewards-summary');
      if (summary) {
        summary.innerHTML = `
          <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <div class="level-indicator" style="width: 40px; height: 40px; font-size: 18px;">
              ${rewards.level}
            </div>
            <div>
              <div style="font-weight: bold; font-size: 16px;">Level ${rewards.level}</div>
              <div style="color: rgba(255,255,255,0.7); font-size: 12px;">
                ${rewards.score} points
                ${rewards.nextLevelAt ? `(${rewards.nextLevelAt - rewards.score} to next level)` : '(Max level)'}
              </div>
            </div>
          </div>
          <div class="rewards-progress" style="height: 8px; margin-bottom: 15px;">
            <div class="rewards-progress-bar" style="width: ${rewards.progress}%"></div>
          </div>
        `;
      }
      
      // Update achievements
      const achievementsContainer = this.panelElement.querySelector('.rewards-achievements div:nth-child(2)');
      if (achievementsContainer) {
        achievementsContainer.innerHTML = this.renderAchievements();
      }
      
      // Update feather icons
      if (typeof feather !== 'undefined') {
        feather.replace();
      }
    }
  }
  
  /**
   * Check if there are new achievements
   * @returns {boolean} True if there are new achievements
   */
  hasNewAchievements() {
    const rewards = window.microRewards.getRewardsSummary();
    const lastAchievements = JSON.parse(localStorage.getItem('last_achievements') || '[]');
    
    // Calculate current achievements
    const currentAchievements = this.achievements
      .filter(a => a.condition(rewards))
      .map(a => a.id);
    
    // Find new achievements
    const newAchievements = currentAchievements.filter(id => !lastAchievements.includes(id));
    
    // Save current achievements
    localStorage.setItem('last_achievements', JSON.stringify(currentAchievements));
    
    return newAchievements.length > 0;
  }
}

// Create global instance
window.rewardsUI = new RewardsUIManager();

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  window.rewardsUI.initialize();
});

// Export functions and classes
export { RewardsUIManager };