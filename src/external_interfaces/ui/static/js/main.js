/**
 * Main JavaScript file for the Real Estate Tokenization Platform
 */

/**
 * Security utility to sanitize HTML and prevent XSS attacks
 * @param {string} str - The string to sanitize
 * @returns {string} - Sanitized HTML-safe string
 */
function sanitizeHTML(str) {
    if (!str) return '';
    
    // Create a temporary DOM element
    const temp = document.createElement('div');
    
    // Set the element's text content which automatically encodes HTML entities
    temp.textContent = str;
    
    // Return the safe HTML string
    return temp.innerHTML;
}

/**
 * Creates DOM elements safely by sanitizing all text content
 * @param {string} tag - HTML tag name
 * @param {Object} attributes - Element attributes
 * @param {string|Array} content - Text content or child elements
 * @returns {HTMLElement} - Safely created DOM element
 */
function createSafeElement(tag, attributes = {}, content = '') {
    const element = document.createElement(tag);
    
    // Set attributes safely
    Object.keys(attributes).forEach(key => {
        if (key.startsWith('on')) {
            // Skip event handlers in attributes to prevent injection
            console.warn('Event handlers should not be passed as attributes');
        } else {
            element.setAttribute(key, attributes[key]);
        }
    });
    
    // Add content
    if (typeof content === 'string') {
        // Text content is safe to set directly
        element.textContent = content;
    } else if (Array.isArray(content)) {
        // Add child elements
        content.forEach(child => {
            if (child instanceof HTMLElement) {
                element.appendChild(child);
            }
        });
    }
    
    return element;
}

// Initialize components on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Initialize Keplr wallet functionality if on a page that uses it
    if (document.getElementById('keplrButton')) {
        initializeKeplrWallet();
    }
    
    // Initialize BIM viewer if on the viewer page
    if (document.getElementById('bimViewer')) {
        initializeBIMViewer();
    }
    
    // Initialize AI chat if on a page with chat interface
    if (document.getElementById('chatInterface')) {
        initializeAIChat();
    }
    
    // Initialize file upload functionality if on upload page
    if (document.getElementById('fileUploadForm')) {
        initializeFileUpload();
    }
});

/**
 * Initialize Bootstrap components
 */
function initializeBootstrapComponents() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add active class to current nav item
    highlightCurrentNavItem();
}

/**
 * Highlight the current navigation item based on URL
 */
function highlightCurrentNavItem() {
    const currentPath = window.location.pathname;
    
    document.querySelectorAll('.nav-link').forEach(navLink => {
        const href = navLink.getAttribute('href');
        
        if (href === currentPath || 
           (currentPath.includes(href) && href !== '/')) {
            navLink.classList.add('active');
        }
    });
}

/**
 * Initialize the BIM viewer component
 */
function initializeBIMViewer() {
    try {
        console.log('Initializing BIM Viewer');
        
        // Create BIM viewer instance
        const bimViewer = new BIMViewer();
        
        // Get the model viewer element
        const modelViewerElement = document.querySelector('model-viewer');
        
        // Initialize viewer with the container
        bimViewer.initialize(modelViewerElement);
        
        // Load the model (default or from URL parameter)
        const urlParams = new URLSearchParams(window.location.search);
        const modelUrl = urlParams.get('model') || '/static/models/sample_building.glb';
        bimViewer.loadModel(modelUrl);
        
        // Initialize event listeners for viewer controls
        initializeViewerControls(bimViewer);
        
        // Make viewer available globally for console debugging
        window.bimViewer = bimViewer;
        
        // Initialize AI Chat if present
        if (window.aiChat) {
            window.aiChat.setBimViewer(bimViewer);
        }
    } catch (error) {
        console.error('Error initializing BIM viewer:', error);
    }
}

/**
 * Initialize controls for the BIM viewer
 * @param {BIMViewer} bimViewer - The BIM viewer instance
 */
function initializeViewerControls(bimViewer) {
    // Reset view button
    const resetViewButton = document.getElementById('resetView');
    if (resetViewButton) {
        resetViewButton.addEventListener('click', () => {
            bimViewer.resetView();
        });
    }
    
    // Screenshot button
    const screenshotButton = document.getElementById('takeScreenshot');
    if (screenshotButton) {
        screenshotButton.addEventListener('click', () => {
            bimViewer.takeScreenshot();
        });
    }
    
    // Wireframe toggle button
    const wireframeButton = document.getElementById('toggleWireframe');
    if (wireframeButton) {
        wireframeButton.addEventListener('click', () => {
            bimViewer.toggleWireframe();
        });
    }
}

/**
 * Initialize the AI chat interface
 */
function initializeAIChat() {
    try {
        console.log('Initializing AI Chat Interface');
        
        // Create AI chat instance
        const aiChat = new AIChatInterface();
        
        // Initialize the chat interface
        aiChat.initialize();
        
        // Add initial greeting message
        aiChat.addMessage("Hello! I'm your BIM Assistant. Ask me about the building model, and I can help you understand its details or navigate to specific elements.", 'system');
        
        // Initialize event listeners for chat controls
        initializeChatControls(aiChat);
        
        // Make chat available globally for console debugging and other components
        window.aiChat = aiChat;
        
        // Connect to BIM viewer if available
        if (window.bimViewer) {
            aiChat.setBimViewer(window.bimViewer);
        }
    } catch (error) {
        console.error('Error initializing AI chat:', error);
    }
}

/**
 * Initialize controls for the AI chat interface
 * @param {AIChatInterface} aiChat - The AI chat interface instance
 */
function initializeChatControls(aiChat) {
    // Clear chat button
    const clearChatButton = document.getElementById('clearChat');
    if (clearChatButton) {
        clearChatButton.addEventListener('click', () => {
            aiChat.clearMessages();
            aiChat.addMessage("Chat cleared. How can I help you with the building model?", 'system');
        });
    }
    
    // Export chat button
    const exportChatButton = document.getElementById('exportChat');
    if (exportChatButton) {
        exportChatButton.addEventListener('click', () => {
            aiChat.exportChat();
        });
    }
}

/**
 * Initialize file upload functionality
 */
function initializeFileUpload() {
    const fileUploadForm = document.getElementById('fileUploadForm');
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.getElementById('uploadButton');
    const previewContainer = document.getElementById('filePreview');
    const progressBar = document.querySelector('.progress-bar');
    
    // Show filename when a file is selected
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const fileName = this.files[0].name;
                const fileInfo = document.getElementById('fileInfo');
                if (fileInfo) {
                    fileInfo.textContent = fileName;
                }
                
                // Show preview for image files
                if (this.files[0].type.match('image.*')) {
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        if (previewContainer) {
                            // Clear any existing content
                            previewContainer.innerHTML = '';
                            
                            // Create image element safely
                            const img = createSafeElement('img', {
                                'src': e.target.result,
                                'class': 'img-fluid preview-image',
                                'alt': 'File Preview'
                            });
                            
                            // Append the safe element
                            previewContainer.appendChild(img);
                            previewContainer.style.display = 'block';
                        }
                    };
                    
                    reader.readAsDataURL(this.files[0]);
                } else {
                    // Show file type icon for non-image files
                    if (previewContainer) {
                        const fileExtension = fileName.split('.').pop().toLowerCase();
                        let iconClass = 'bi-file-earmark';
                        
                        // Set icon based on file extension
                        if (['pdf'].includes(fileExtension)) {
                            iconClass = 'bi-file-earmark-pdf';
                        } else if (['doc', 'docx'].includes(fileExtension)) {
                            iconClass = 'bi-file-earmark-word';
                        } else if (['xls', 'xlsx'].includes(fileExtension)) {
                            iconClass = 'bi-file-earmark-excel';
                        } else if (['zip', 'rar', '7z'].includes(fileExtension)) {
                            iconClass = 'bi-file-earmark-zip';
                        } else if (['mp3', 'wav', 'ogg'].includes(fileExtension)) {
                            iconClass = 'bi-file-earmark-music';
                        } else if (['mp4', 'avi', 'mov'].includes(fileExtension)) {
                            iconClass = 'bi-file-earmark-play';
                        } else if (['html', 'css', 'js'].includes(fileExtension)) {
                            iconClass = 'bi-file-earmark-code';
                        }
                        
                        // Clear any existing content
                        previewContainer.innerHTML = '';
                        
                        // Create elements safely
                        const icon = createSafeElement('i', {'class': `bi ${sanitizeHTML(iconClass)} display-1`});
                        const fileNamePara = createSafeElement('p', {}, fileName);
                        
                        // Append the safe elements
                        previewContainer.appendChild(icon);
                        previewContainer.appendChild(fileNamePara);
                        previewContainer.style.display = 'block';
                    }
                }
            }
        });
    }
    
    // Handle form submission
    if (fileUploadForm) {
        fileUploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!fileInput.files || fileInput.files.length === 0) {
                showAlert('Please select a file to upload', 'warning');
                return;
            }
            
            // Show progress bar
            if (progressBar) {
                progressBar.style.width = '0%';
                progressBar.parentElement.style.display = 'block';
            }
            
            const formData = new FormData(fileUploadForm);
            
            // Simulate progress (in a real app, this would track actual upload progress)
            let progress = 0;
            const interval = setInterval(() => {
                progress += 5;
                if (progressBar) {
                    progressBar.style.width = `${progress}%`;
                    progressBar.setAttribute('aria-valuenow', progress);
                }
                
                if (progress >= 100) {
                    clearInterval(interval);
                }
            }, 200);
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                clearInterval(interval);
                
                if (progressBar) {
                    progressBar.style.width = '100%';
                }
                
                if (data.success) {
                    showAlert('File uploaded successfully!', 'success');
                    
                    // Reset form after successful upload
                    setTimeout(() => {
                        fileUploadForm.reset();
                        if (previewContainer) {
                            previewContainer.innerHTML = '';
                            previewContainer.style.display = 'none';
                        }
                        if (progressBar) {
                            progressBar.parentElement.style.display = 'none';
                        }
                        const fileInfo = document.getElementById('fileInfo');
                        if (fileInfo) {
                            fileInfo.textContent = 'No file selected';
                        }
                    }, 3000);
                } else {
                    showAlert(data.message || 'Upload failed', 'danger');
                    if (progressBar) {
                        progressBar.parentElement.style.display = 'none';
                    }
                }
            })
            .catch(error => {
                clearInterval(interval);
                console.error('Error uploading file:', error);
                showAlert('Error uploading file. Please try again.', 'danger');
                if (progressBar) {
                    progressBar.parentElement.style.display = 'none';
                }
            });
        });
    }
}

/**
 * Show an alert message
 * @param {string} message - The message to display
 * @param {string} type - Alert type (success, danger, warning, info)
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    // Create alert container safely
    const alertEl = createSafeElement('div', {
        'class': `alert alert-${sanitizeHTML(type)} alert-dismissible fade show`,
        'role': 'alert'
    });
    
    // Add message text safely
    const messageText = createSafeElement('span', {}, message);
    alertEl.appendChild(messageText);
    
    // Add dismiss button safely
    const dismissButton = createSafeElement('button', {
        'type': 'button',
        'class': 'btn-close',
        'data-bs-dismiss': 'alert',
        'aria-label': 'Close'
    });
    alertEl.appendChild(dismissButton);
    
    // Add to container
    alertContainer.appendChild(alertEl);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertEl.parentNode) {
            const bsAlert = new bootstrap.Alert(alertEl);
            bsAlert.close();
        }
    }, 5000);
}

/**
 * Initialize Keplr wallet functionality
 */
function initializeKeplrWallet() {
    // Check if Keplr is installed
    if (!window.keplr) {
        console.log('Please install Keplr extension');
        const keplrButton = document.getElementById('keplrButton');
        if (keplrButton) {
            keplrButton.textContent = 'Install Keplr';
            keplrButton.addEventListener('click', () => {
                window.open('https://www.keplr.app/download', '_blank');
            });
        }
        return;
    }
    
    // Keplr is available, setup wallet connect button
    const keplrButton = document.getElementById('keplrButton');
    if (keplrButton) {
        keplrButton.addEventListener('click', async () => {
            try {
                // Request connection to Keplr
                await window.keplr.enable(window.chainId || 'cosmoshub-4');
                
                // Get address from Keplr
                const offlineSigner = window.keplr.getOfflineSigner(window.chainId || 'cosmoshub-4');
                const accounts = await offlineSigner.getAccounts();
                const address = accounts[0].address;
                
                // Update button text
                keplrButton.textContent = address.substring(0, 8) + '...' + address.substring(address.length - 4);
                keplrButton.classList.replace('btn-primary', 'btn-success');
                
                // Store address in session
                sessionStorage.setItem('walletAddress', address);
                
                // Trigger wallet connected event
                const event = new CustomEvent('walletConnected', { detail: { address } });
                document.dispatchEvent(event);
                
                console.log('Connected to Keplr wallet:', address);
            } catch (error) {
                console.error('Error connecting to Keplr wallet:', error);
                showAlert('Error connecting to Keplr wallet. Please try again.', 'danger');
            }
        });
    }
    
    // Check if previously connected
    const savedAddress = sessionStorage.getItem('walletAddress');
    if (savedAddress && keplrButton) {
        keplrButton.textContent = savedAddress.substring(0, 8) + '...' + savedAddress.substring(savedAddress.length - 4);
        keplrButton.classList.replace('btn-primary', 'btn-success');
    }
}
