/**
 * Enhanced AI Chat Interface
 * Features OpenAI Agents integration, stakeholder detection, and BIM data
 */

const aiChat = {
    containerId: null,
    chatContainer: null,
    messagesContainer: null,
    isEnhancedMode: false,
    chatHistory: [],
    stakeholder: null,
    
    // Initialize the chat interface
    init: function(containerId) {
        this.containerId = containerId;
        this.chatContainer = document.getElementById(containerId);
        
        if (!this.chatContainer) {
            console.error(`Chat container with ID ${containerId} not found`);
            return;
        }
        
        this.render();
        this.bindEvents();
        this.checkEnhancedStatus();
        
        // Add system welcome message
        this.addSystemMessage("Welcome to the BIM AI Assistant. How can I help you today?");
    },
    
    // Render the chat interface
    render: function() {
        this.chatContainer.innerHTML = `
            <div class="chat-header">
                <div class="chat-title">BIM AI Assistant</div>
                <div class="chat-mode-toggle">
                    <label class="toggle-switch">
                        <input type="checkbox" id="enhanced-toggle">
                        <span class="toggle-slider"></span>
                    </label>
                    <span class="toggle-label">Enhanced AI</span>
                </div>
            </div>
            <div class="chat-messages"></div>
            <div class="chat-input-container">
                <input type="text" class="chat-input" placeholder="Ask about the building..." id="chat-input">
                <button class="chat-send-btn" id="chat-send">Send</button>
            </div>
        `;
        
        this.messagesContainer = this.chatContainer.querySelector('.chat-messages');
    },
    
    // Bind event listeners
    bindEvents: function() {
        const inputElement = document.getElementById('chat-input');
        const sendButton = document.getElementById('chat-send');
        const enhancedToggle = document.getElementById('enhanced-toggle');
        
        // Send message on button click
        sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Send message on Enter key
        inputElement.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // Toggle enhanced mode
        enhancedToggle.addEventListener('change', () => {
            this.toggleEnhancedMode(enhancedToggle.checked);
        });
    },
    
    // Check enhanced mode status
    checkEnhancedStatus: function() {
        fetch('/api/bim-agent/enhanced-status')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.isEnhancedMode = data.enhanced_mode;
                    document.getElementById('enhanced-toggle').checked = this.isEnhancedMode;
                }
            })
            .catch(error => {
                console.error('Error checking enhanced status:', error);
            });
    },
    
    // Toggle enhanced mode
    toggleEnhancedMode: function(enabled) {
        fetch('/api/bim-agent/toggle-enhanced', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                enabled: enabled
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.isEnhancedMode = data.enhanced_mode;
                document.getElementById('enhanced-toggle').checked = this.isEnhancedMode;
                
                // Add system message about mode change
                const modeMsg = this.isEnhancedMode ? 
                    "Enhanced AI mode activated. I now have deeper building knowledge and stakeholder awareness." : 
                    "Switched to standard AI mode.";
                this.addSystemMessage(modeMsg);
            } else {
                // If failed, revert the toggle
                document.getElementById('enhanced-toggle').checked = this.isEnhancedMode;
                
                // Add error message
                this.addErrorMessage(data.message || "Failed to toggle enhanced mode");
            }
        })
        .catch(error => {
            console.error('Error toggling enhanced mode:', error);
            document.getElementById('enhanced-toggle').checked = this.isEnhancedMode;
            this.addErrorMessage("An error occurred while toggling enhanced mode");
        });
    },
    
    // Send a message
    sendMessage: function() {
        const inputElement = document.getElementById('chat-input');
        const message = inputElement.value.trim();
        
        if (!message) return;
        
        // Add user message to UI
        this.addUserMessage(message);
        
        // Clear input
        inputElement.value = '';
        
        // Send message to server
        fetch('/api/bim-agent/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add AI response to UI
                this.addAIMessage(data.response, data.metadata);
                
                // Update stakeholder if detected
                if (data.metadata && data.metadata.stakeholder) {
                    this.stakeholder = data.metadata.stakeholder;
                }
            } else {
                // Add error message
                this.addErrorMessage(data.message || "Failed to process message");
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            this.addErrorMessage("An error occurred while sending your message");
        });
    },
    
    // Add a user message to the chat
    addUserMessage: function(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message message-user';
        messageElement.textContent = message;
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
        
        // Add to chat history
        this.chatHistory.push({
            role: 'user',
            content: message
        });
    },
    
    // Add an AI message to the chat
    addAIMessage: function(message, metadata = {}) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message message-ai';
        messageElement.textContent = message;
        
        // Add metadata if available
        if (metadata) {
            const metaElement = document.createElement('div');
            metaElement.className = 'message-meta';
            
            // Add stakeholder tag if available
            if (metadata.stakeholder && metadata.stakeholder_name) {
                const stakeholderTag = document.createElement('span');
                stakeholderTag.className = `stakeholder-tag stakeholder-${metadata.stakeholder}`;
                stakeholderTag.textContent = metadata.stakeholder_name;
                metaElement.appendChild(stakeholderTag);
            }
            
            // Add enhanced tag if in enhanced mode
            if (metadata.enhanced_mode) {
                const enhancedTag = document.createElement('span');
                enhancedTag.className = 'enhanced-tag';
                enhancedTag.innerHTML = `
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M21 12.59V17C21 20 19.5 22 16 22H8C4.5 22 3 20 3 17V7C3 4 4.5 2 8 2H16C19.5 2 21 4 21 7V8.14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>
                        <path d="M8 2V22" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>
                        <path d="M14.75 15L17.5 12L14.75 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>
                        <path d="M17.5 12H11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>
                    </svg>
                    Enhanced
                `;
                metaElement.appendChild(enhancedTag);
            }
            
            messageElement.appendChild(metaElement);
        }
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
        
        // Add to chat history
        this.chatHistory.push({
            role: 'assistant',
            content: message
        });
    },
    
    // Add a system message to the chat
    addSystemMessage: function(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message message-ai message-system';
        messageElement.textContent = message;
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    },
    
    // Add an error message to the chat
    addErrorMessage: function(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message message-ai message-error';
        messageElement.textContent = message;
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    },
    
    // Scroll to the bottom of the chat
    scrollToBottom: function() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
};
