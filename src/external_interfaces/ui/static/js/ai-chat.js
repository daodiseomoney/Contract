/**
 * AI Chat Component for BIM AI Management Dashboard
 * Connects to backend BIM Agent API for stakeholder-aware building analysis
 */

const aiChat = {
    // DOM Elements
    elements: {
        chatContainer: null,
        chatMessages: null,
        chatInput: null,
        chatSendBtn: null,
    },
    
    // Chat state
    state: {
        messages: [],
        loading: false,
        initialized: false,
    },
    
    // Maps stakeholder groups to CSS classes
    stakeholderClasses: {
        'Tenant/Buyer': 'stakeholder-tenant-buyer',
        'Broker': 'stakeholder-broker',
        'Landlord': 'stakeholder-landlord',
        'Property Manager': 'stakeholder-property-manager',
        'Appraiser': 'stakeholder-appraiser',
        'Mortgage Broker': 'stakeholder-mortgage-broker',
        'Investor': 'stakeholder-investor',
    },
    
    /**
     * Initialize the chat component
     * @param {string} containerId - The ID of the chat container element
     */
    init(containerId) {
        // Check for agent availability
        this.checkAgentStatus();
        
        // Get DOM elements
        this.elements.chatContainer = document.getElementById(containerId);
        
        if (!this.elements.chatContainer) {
            console.error('Chat container not found');
            return;
        }
        
        // Create chat UI
        this.createChatUI();
        
        // Set up event listeners
        this.setupEventListeners();
        
        this.state.initialized = true;
        console.log('AI Chat initialized');
    },
    
    /**
     * Create the chat UI elements
     */
    createChatUI() {
        this.elements.chatContainer.innerHTML = `
            <div class="chat-messages"></div>
            <div class="chat-input-container">
                <input type="text" class="chat-input" placeholder="Ask about this building...">
                <button class="chat-send-btn">
                    <i data-feather="send"></i>
                </button>
            </div>
        `;
        
        // Initialize Feather icons
        feather.replace();
        
        // Get references to the newly created elements
        this.elements.chatMessages = this.elements.chatContainer.querySelector('.chat-messages');
        this.elements.chatInput = this.elements.chatContainer.querySelector('.chat-input');
        this.elements.chatSendBtn = this.elements.chatContainer.querySelector('.chat-send-btn');
        
        // Add welcome message
        this.addMessage({
            text: "Hello! I'm your BIM AI assistant. I can analyze building data and answer questions about this project. What would you like to know?",
            isUser: false,
        });
    },
    
    /**
     * Set up event listeners for the chat interface
     */
    setupEventListeners() {
        // Send button click
        this.elements.chatSendBtn.addEventListener('click', () => {
            this.handleUserMessage();
        });
        
        // Enter key press
        this.elements.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleUserMessage();
            }
        });
    },
    
    /**
     * Handle user message input
     */
    handleUserMessage() {
        const message = this.elements.chatInput.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        this.addMessage({
            text: message,
            isUser: true,
        });
        
        // Clear input
        this.elements.chatInput.value = '';
        
        // Show loading indicator
        this.setLoading(true);
        
        // Send message to API
        this.sendMessageToAPI(message);
    },
    
    /**
     * Send message to BIM agent API
     * @param {string} message - The user's message
     */
    async sendMessageToAPI(message) {
        try {
            const response = await fetch('/api/bim-agent/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: message }),
            });
            
            if (!response.ok) {
                throw new Error('API request failed');
            }
            
            const data = await response.json();
            
            // Process the API response
            this.handleAPIResponse(data);
        } catch (error) {
            console.error('Error sending message to API:', error);
            
            // Show error message
            this.addMessage({
                text: "Sorry, I couldn't process your request. Please try again later.",
                isUser: false,
                error: true,
            });
        } finally {
            this.setLoading(false);
        }
    },
    
    /**
     * Handle API response
     * @param {object} data - The API response data
     */
    handleAPIResponse(data) {
        // Add AI response to chat
        this.addMessage({
            text: data.response,
            isUser: false,
            stakeholderGroup: data.stakeholderGroup,
            metadata: data.metadata,
        });
    },
    
    /**
     * Add a message to the chat
     * @param {object} messageData - The message data
     * @param {string} messageData.text - The message text
     * @param {boolean} messageData.isUser - Whether the message is from the user
     * @param {string} [messageData.stakeholderGroup] - The identified stakeholder group
     * @param {object} [messageData.metadata] - Additional message metadata
     * @param {boolean} [messageData.error] - Whether the message is an error
     */
    addMessage(messageData) {
        // Create message element
        const messageElement = document.createElement('div');
        messageElement.className = `message ${messageData.isUser ? 'message-user' : 'message-ai'}`;
        
        // Add message text
        messageElement.textContent = messageData.text;
        
        // Add stakeholder tag if present
        if (!messageData.isUser && messageData.stakeholderGroup) {
            const stakeholderTag = document.createElement('div');
            stakeholderTag.className = `stakeholder-tag ${this.stakeholderClasses[messageData.stakeholderGroup] || ''}`;
            stakeholderTag.textContent = messageData.stakeholderGroup;
            
            // Create message meta container
            const messageMetaContainer = document.createElement('div');
            messageMetaContainer.className = 'message-meta';
            messageMetaContainer.appendChild(document.createTextNode('Perspective: '));
            messageMetaContainer.appendChild(stakeholderTag);
            
            messageElement.appendChild(messageMetaContainer);
        }
        
        // Add to messages and DOM
        this.state.messages.push(messageData);
        this.elements.chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        this.scrollToBottom();
    },
    
    /**
     * Scroll chat to the bottom
     */
    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    },
    
    /**
     * Set loading state
     * @param {boolean} isLoading - Whether the chat is loading
     */
    setLoading(isLoading) {
        this.state.loading = isLoading;
        
        if (isLoading) {
            // Add loading indicator
            const loadingElement = document.createElement('div');
            loadingElement.className = 'message message-ai loading';
            loadingElement.textContent = 'Thinking...';
            loadingElement.id = 'chat-loading-indicator';
            this.elements.chatMessages.appendChild(loadingElement);
            this.scrollToBottom();
        } else {
            // Remove loading indicator
            const loadingElement = document.getElementById('chat-loading-indicator');
            if (loadingElement) {
                loadingElement.remove();
            }
        }
    },
    
    /**
     * Check if the BIM agent API is available
     */
    async checkAgentStatus() {
        try {
            const response = await fetch('/api/bim-agent/status');
            const data = await response.json();
            
            if (!data.available) {
                console.warn('BIM Agent not available:', data.message);
            }
        } catch (error) {
            console.error('Error checking BIM agent status:', error);
        }
    }
};
