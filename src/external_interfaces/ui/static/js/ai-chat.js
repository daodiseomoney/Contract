/**
 * AI Chat Interface Module
 * Handles interaction with the LLM interface to query BIM data
 */

class AIChatInterface {
    constructor() {
        this.messagesContainer = null;
        this.inputField = null;
        this.sendButton = null;
        this.messages = [];
        this.bimViewer = null;
        this.isProcessing = false;
    }

    /**
     * Initialize the chat interface
     */
    initialize() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.inputField = document.getElementById('userMessage');
        this.sendButton = document.getElementById('sendMessage');
        
        if (this.inputField && this.sendButton) {
            this.setupEventListeners();
        }
    }

    /**
     * Set up event listeners for the chat interface
     */
    setupEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Send message on Enter key press
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Focus input field on page load
        setTimeout(() => {
            this.inputField.focus();
        }, 500);
    }

    /**
     * Set the BIM viewer reference for interaction
     * @param {BIMViewer} viewer - The BIM viewer instance
     */
    setBimViewer(viewer) {
        this.bimViewer = viewer;
    }

    /**
     * Send a message to the AI
     */
    sendMessage() {
        const message = this.inputField.value.trim();
        if (message === '' || this.isProcessing) return;
        
        // Add user message to the chat
        this.addMessage(message, 'user');
        
        // Clear input field
        this.inputField.value = '';
        
        // Process the message
        this.processMessage(message);
    }

    /**
     * Process a user message
     * @param {string} message - The user's message
     */
    processMessage(message) {
        this.isProcessing = true;
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // In a real implementation, this would call an API endpoint
        // to process the message with an LLM or other AI service
        setTimeout(() => {
            // For demonstration, simulate AI response based on message keywords
            const response = this.generateAIResponse(message);
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Add AI response to the chat
            this.addMessage(response, 'system');
            
            this.isProcessing = false;
        }, 1000);
    }

    /**
     * Generate a simulated AI response based on keywords
     * @param {string} message - The user's message
     * @returns {string} - The AI response
     */
    generateAIResponse(message) {
        const messageLower = message.toLowerCase();
        
        // Handle model selection or component queries
        if (messageLower.includes('select') || messageLower.includes('show me')) {
            if (messageLower.includes('foundation')) {
                if (this.bimViewer) {
                    this.bimViewer.selectElement('foundation');
                }
                return "I've selected the foundation elements in the model. The foundation uses reinforced concrete with a thickness of 500mm and C30/37 strength class.";
            } else if (messageLower.includes('wall') || messageLower.includes('walls')) {
                if (this.bimViewer) {
                    this.bimViewer.selectElement('walls');
                }
                return "I've highlighted the walls in the model. These are external walls made of brick veneer with CMU backup, 300mm thick with an R-19 insulation value.";
            } else if (messageLower.includes('column') || messageLower.includes('columns')) {
                if (this.bimViewer) {
                    this.bimViewer.selectElement('columns');
                }
                return "I've selected the columns. These are structural steel columns with W12x40 profile and a height of 3.5m. They have a 2-hour fire rating.";
            }
        }
        
        // Handle building information queries
        if (messageLower.includes('material') || messageLower.includes('made of')) {
            return "This building uses a variety of materials including:\n- Reinforced concrete for the foundation\n- Structural steel for the columns and beams\n- Brick veneer with CMU backup for external walls\n- Aluminum frames with low-E glass for windows\n\nIs there a specific element you'd like more details about?";
        }
        
        // Handle dimension queries
        if (messageLower.includes('size') || messageLower.includes('dimensions') || messageLower.includes('how big')) {
            return "The building has the following dimensions:\n- Height: 35m (10 stories)\n- Footprint: 30m x 45m\n- Total floor area: approximately 13,500 sq.m\n- Floor-to-floor height: 3.5m";
        }
        
        // Handle energy efficiency queries
        if (messageLower.includes('energy') || messageLower.includes('efficiency') || messageLower.includes('sustainable')) {
            return "This building was designed with energy efficiency in mind:\n- The windows use low-E glass with a U-factor of 0.35 and SHGC of 0.40\n- Walls have R-19 insulation\n- The roof has R-30 insulation\n- The HVAC system uses high-efficiency heat pumps\n- A 50kW solar array is installed on the roof";
        }
        
        // Handle commands to manipulate the view
        if (messageLower.includes('reset') && messageLower.includes('view')) {
            if (this.bimViewer) {
                this.bimViewer.resetView();
            }
            return "I've reset the view to the default position.";
        }
        
        if (messageLower.includes('wireframe')) {
            if (this.bimViewer) {
                this.bimViewer.toggleWireframe();
            }
            return "I've toggled the wireframe mode.";
        }
        
        // Default response for unknown queries
        return "I understand you're asking about " + message.split(' ').slice(0, 3).join(' ') + "..., but I don't have specific information about that. I can help with questions about the building's structure, materials, dimensions, or energy efficiency. You can also ask me to select specific elements like 'show me the columns' or 'select the walls'.";
    }

    /**
     * Add a message to the chat
     * @param {string} content - The message content
     * @param {string} sender - The message sender ('user' or 'system')
     */
    addMessage(content, sender) {
        if (!this.messagesContainer) return;
        
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = `message ${sender}-message`;
        
        // Create message content
        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        
        // Process the message content
        const formattedContent = this.formatMessageContent(content);
        contentEl.innerHTML = formattedContent;
        
        // Add to message element
        messageEl.appendChild(contentEl);
        
        // Add to messages container
        this.messagesContainer.appendChild(messageEl);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Store message in history
        this.messages.push({
            content,
            sender,
            timestamp: new Date()
        });
    }

    /**
     * Format message content with markdown-like syntax
     * @param {string} content - The raw message content
     * @returns {string} - The formatted HTML
     */
    formatMessageContent(content) {
        let formatted = content;
        
        // Convert line breaks to paragraphs
        formatted = formatted.split('\n').map(line => {
            if (line.trim() === '') return '';
            return `<p>${line}</p>`;
        }).join('');
        
        // Convert bullet points
        formatted = formatted.replace(/- (.+)/g, '<p>• $1</p>');
        
        return formatted;
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        if (!this.messagesContainer) return;
        
        // Create typing indicator
        const typingEl = document.createElement('div');
        typingEl.className = 'message system-message typing-indicator';
        typingEl.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
        typingEl.id = 'typingIndicator';
        
        // Add to messages container
        this.messagesContainer.appendChild(typingEl);
        
        // Scroll to bottom
        this.scrollToBottom();
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        const typingEl = document.getElementById('typingIndicator');
        if (typingEl) {
            typingEl.remove();
        }
    }

    /**
     * Scroll the messages container to the bottom
     */
    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }

    /**
     * Clear all messages
     */
    clearMessages() {
        if (this.messagesContainer) {
            // Keep only the initial greeting message
            const initialMessage = this.messagesContainer.querySelector('.message');
            this.messagesContainer.innerHTML = '';
            if (initialMessage) {
                this.messagesContainer.appendChild(initialMessage);
            }
            
            // Reset messages array
            this.messages = [];
        }
    }

    /**
     * Export chat history as a text file
     */
    exportChat() {
        if (this.messages.length === 0) return;
        
        // Format the chat log
        let chatLog = 'BIM AI Assistant Chat Log\n';
        chatLog += `Generated: ${new Date().toLocaleString()}\n\n`;
        
        this.messages.forEach(message => {
            const timestamp = message.timestamp.toLocaleTimeString();
            const sender = message.sender === 'user' ? 'You' : 'AI Assistant';
            chatLog += `[${timestamp}] ${sender}:\n${message.content}\n\n`;
        });
        
        // Create a blob and download link
        const blob = new Blob([chatLog], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `bim-chat-${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
}

// Add some CSS for the typing indicator
document.addEventListener('DOMContentLoaded', () => {
    const style = document.createElement('style');
    style.textContent = `
        .typing-indicator {
            padding: 0.75rem 1rem;
        }
        .typing-dots {
            display: flex;
            align-items: center;
            height: 26px;
        }
        .typing-dots span {
            height: 8px;
            width: 8px;
            margin: 0 2px;
            background-color: rgba(224, 13, 121, 0.7);
            border-radius: 50%;
            display: inline-block;
            animation: typing-dot 1.4s infinite ease-in-out both;
        }
        .typing-dots span:nth-child(1) {
            animation-delay: -0.32s;
        }
        .typing-dots span:nth-child(2) {
            animation-delay: -0.16s;
        }
        @keyframes typing-dot {
            0%, 80%, 100% {
                transform: scale(0);
            }
            40% {
                transform: scale(1);
            }
        }
    `;
    document.head.appendChild(style);
});
