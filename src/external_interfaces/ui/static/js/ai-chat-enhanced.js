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
        // Clear the container first
        this.chatContainer.innerHTML = '';
        
        // Create header element
        const header = document.createElement('div');
        header.className = 'chat-header';
        
        // Create title
        const title = document.createElement('div');
        title.className = 'chat-title';
        title.textContent = 'BIM AI Assistant';
        header.appendChild(title);
        
        // Create mode toggle container
        const toggleContainer = document.createElement('div');
        toggleContainer.className = 'chat-mode-toggle';
        
        // Create toggle switch
        const toggleLabel = document.createElement('label');
        toggleLabel.className = 'toggle-switch';
        
        const toggleInput = document.createElement('input');
        toggleInput.type = 'checkbox';
        toggleInput.id = 'enhanced-toggle';
        
        const toggleSlider = document.createElement('span');
        toggleSlider.className = 'toggle-slider';
        
        toggleLabel.appendChild(toggleInput);
        toggleLabel.appendChild(toggleSlider);
        toggleContainer.appendChild(toggleLabel);
        
        // Create toggle label
        const labelText = document.createElement('span');
        labelText.className = 'toggle-label';
        labelText.textContent = 'Enhanced AI';
        toggleContainer.appendChild(labelText);
        
        header.appendChild(toggleContainer);
        this.chatContainer.appendChild(header);
        
        // Create messages container
        const messagesContainer = document.createElement('div');
        messagesContainer.className = 'chat-messages';
        this.chatContainer.appendChild(messagesContainer);
        
        // Create input container
        const inputContainer = document.createElement('div');
        inputContainer.className = 'chat-input-container';
        
        // Create input field
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'chat-input';
        input.placeholder = 'Ask about the building...';
        input.id = 'chat-input';
        inputContainer.appendChild(input);
        
        // Create send button
        const sendButton = document.createElement('button');
        sendButton.className = 'chat-send-btn';
        sendButton.id = 'chat-send';
        sendButton.textContent = 'Send';
        inputContainer.appendChild(sendButton);
        
        this.chatContainer.appendChild(inputContainer);
        
        // Store reference to messages container
        this.messagesContainer = messagesContainer;
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
        
        // If this is a filtered message, apply special styling
        if (metadata && metadata.filtered) {
            messageElement.className += ' message-filtered';
            
            // Create warning icon container
            const warningIcon = document.createElement('div');
            warningIcon.className = 'filter-icon';
            
            // Create SVG element
            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute("width", "16");
            svg.setAttribute("height", "16");
            svg.setAttribute("viewBox", "0 0 24 24");
            svg.setAttribute("fill", "none");
            
            // Create paths
            const path1 = document.createElementNS("http://www.w3.org/2000/svg", "path");
            path1.setAttribute("d", "M12 9V14");
            path1.setAttribute("stroke", "currentColor");
            path1.setAttribute("stroke-width", "1.5");
            path1.setAttribute("stroke-linecap", "round");
            path1.setAttribute("stroke-linejoin", "round");
            
            const path2 = document.createElementNS("http://www.w3.org/2000/svg", "path");
            path2.setAttribute("d", "M12 21.41H5.94C2.47 21.41 1.02 18.93 2.7 15.9L5.82 10.28L8.76 5.00999C10.54 1.79999 13.46 1.79999 15.24 5.00999L18.18 10.29L21.3 15.91C22.98 18.94 21.52 21.42 18.06 21.42H12V21.41Z");
            path2.setAttribute("stroke", "currentColor");
            path2.setAttribute("stroke-width", "1.5");
            path2.setAttribute("stroke-linecap", "round");
            path2.setAttribute("stroke-linejoin", "round");
            
            const path3 = document.createElementNS("http://www.w3.org/2000/svg", "path");
            path3.setAttribute("d", "M11.995 17H12.005");
            path3.setAttribute("stroke", "currentColor");
            path3.setAttribute("stroke-width", "2");
            path3.setAttribute("stroke-linecap", "round");
            path3.setAttribute("stroke-linejoin", "round");
            
            // Append paths to SVG
            svg.appendChild(path1);
            svg.appendChild(path2);
            svg.appendChild(path3);
            
            // Append SVG to icon container
            warningIcon.appendChild(svg);
            
            // Append icon to message
            messageElement.appendChild(warningIcon);
        }
        
        // Add the message text
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = message;
        messageElement.appendChild(messageText);
        
        // Add metadata if available
        if (metadata) {
            const metaElement = document.createElement('div');
            metaElement.className = 'message-meta';
            
            // Add stakeholder tag if available (and not a filtered message)
            if (!metadata.filtered && metadata.stakeholder && metadata.stakeholder_name) {
                const stakeholderTag = document.createElement('span');
                stakeholderTag.className = `stakeholder-tag stakeholder-${metadata.stakeholder}`;
                stakeholderTag.textContent = metadata.stakeholder_name;
                metaElement.appendChild(stakeholderTag);
            }
            
            // Add enhanced tag if in enhanced mode
            if (metadata.enhanced_mode) {
                const enhancedTag = document.createElement('span');
                enhancedTag.className = 'enhanced-tag';
                
                // Create SVG element
                const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                svg.setAttribute("width", "14");
                svg.setAttribute("height", "14");
                svg.setAttribute("viewBox", "0 0 24 24");
                svg.setAttribute("fill", "none");
                
                // Create paths
                const path1 = document.createElementNS("http://www.w3.org/2000/svg", "path");
                path1.setAttribute("d", "M21 12.59V17C21 20 19.5 22 16 22H8C4.5 22 3 20 3 17V7C3 4 4.5 2 8 2H16C19.5 2 21 4 21 7V8.14");
                path1.setAttribute("stroke", "currentColor");
                path1.setAttribute("stroke-width", "1.5");
                path1.setAttribute("stroke-linecap", "round");
                path1.setAttribute("stroke-linejoin", "round");
                
                const path2 = document.createElementNS("http://www.w3.org/2000/svg", "path");
                path2.setAttribute("d", "M8 2V22");
                path2.setAttribute("stroke", "currentColor");
                path2.setAttribute("stroke-width", "1.5");
                path2.setAttribute("stroke-linecap", "round");
                path2.setAttribute("stroke-linejoin", "round");
                
                const path3 = document.createElementNS("http://www.w3.org/2000/svg", "path");
                path3.setAttribute("d", "M14.75 15L17.5 12L14.75 9");
                path3.setAttribute("stroke", "currentColor");
                path3.setAttribute("stroke-width", "1.5");
                path3.setAttribute("stroke-linecap", "round");
                path3.setAttribute("stroke-linejoin", "round");
                
                const path4 = document.createElementNS("http://www.w3.org/2000/svg", "path");
                path4.setAttribute("d", "M17.5 12H11");
                path4.setAttribute("stroke", "currentColor");
                path4.setAttribute("stroke-width", "1.5");
                path4.setAttribute("stroke-linecap", "round");
                path4.setAttribute("stroke-linejoin", "round");
                
                // Append paths to SVG
                svg.appendChild(path1);
                svg.appendChild(path2);
                svg.appendChild(path3);
                svg.appendChild(path4);
                
                // Append SVG to tag
                enhancedTag.appendChild(svg);
                
                // Add text node with a space
                enhancedTag.appendChild(document.createTextNode(" Enhanced"));
                
                // Add to metadata element
                metaElement.appendChild(enhancedTag);
            }
            
            // Add filter tag if this was a filtered message
            if (metadata.filtered) {
                const filteredTag = document.createElement('span');
                filteredTag.className = 'filtered-tag';
                filteredTag.textContent = 'Content Filtered';
                metaElement.appendChild(filteredTag);
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
