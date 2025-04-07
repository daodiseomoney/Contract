/**
 * BIM Viewer Module
 * Handles 3D visualization of BIM models using Three.js and Google Model Viewer
 */
class BIMViewer {
    constructor() {
        this.currentModel = null;
        this.selectedObjects = [];
        this.objectTree = [];
        this.isWireframe = false;
    }

    /**
     * Initialize the BIM viewer with a container element
     * @param {HTMLElement} container - The container element for the viewer
     */
    initialize(container) {
        this.container = container;
        this.setupModelViewer();
        console.log('BIM Viewer initialized');
    }

    /**
     * Set up the model viewer component
     */
    setupModelViewer() {
        if (!this.container) return;
        
        // Check if we're using a model-viewer component or Three.js
        if (this.container.tagName === 'MODEL-VIEWER') {
            this.modelViewer = this.container;
            
            // Add event listeners for model-viewer
            this.modelViewer.addEventListener('load', () => this.onModelLoaded());
            this.modelViewer.addEventListener('model-visibility', (event) => {
                console.log('Model visibility changed:', event.detail.visible);
            });
            
            // Set viewer options
            this.modelViewer.cameraControls = true;
            this.modelViewer.autoRotate = false;
            this.modelViewer.shadowIntensity = 1;
            this.modelViewer.exposure = 0.75;
            this.modelViewer.environmentImage = 'neutral';
            
            // Add custom AR button if available
            if ('xr' in navigator) {
                this.modelViewer.ar = true;
                this.modelViewer.arModes = 'webxr scene-viewer';
            }
        } else {
            console.error('Unsupported viewer type');
        }
    }

    /**
     * Load a 3D model into the viewer
     * @param {string} modelUrl - URL to the model file
     */
    loadModel(modelUrl) {
        if (!this.modelViewer) return;
        
        console.log('Loading model:', modelUrl);
        
        // Set the source of the model-viewer component
        this.modelViewer.src = modelUrl;
        
        // Update UI elements
        this.showLoadingIndicator(true);
        
        // If we have model-viewer, we let the component handle loading
        if (this.modelViewer) {
            this.modelViewer.addEventListener('load', () => {
                this.showLoadingIndicator(false);
                this.currentModel = modelUrl;
                console.log('Model loaded successfully');
                
                // Generate object tree from model
                this.generateObjectTree();
            }, { once: true });
            
            this.modelViewer.addEventListener('error', (error) => {
                this.showLoadingIndicator(false);
                console.error('Error loading model:', error);
                this.showErrorMessage('Failed to load model. Please check the file format and try again.');
            }, { once: true });
        }
    }

    /**
     * Show or hide the loading indicator
     * @param {boolean} show - Whether to show the loading indicator
     */
    showLoadingIndicator(show) {
        const loadingElement = document.querySelector('.tree-loading');
        if (loadingElement) {
            loadingElement.style.display = show ? 'flex' : 'none';
        }
    }

    /**
     * Display an error message
     * @param {string} message - The error message to display
     */
    showErrorMessage(message) {
        const elementProperties = document.getElementById('elementProperties');
        if (elementProperties) {
            elementProperties.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        }
    }

    /**
     * Generate object tree from the loaded model
     */
    generateObjectTree() {
        const treeContainer = document.getElementById('objectTree');
        if (!treeContainer) return;
        
        // Clear existing tree
        while (treeContainer.firstChild) {
            if (treeContainer.firstChild.classList && treeContainer.firstChild.classList.contains('tree-loading')) {
                // Skip removing the loading indicator
                treeContainer.removeChild(treeContainer.firstChild);
            }
        }
        
        // For demonstration, generate a sample tree structure
        // In a real implementation, this would be derived from the model
        const sampleStructure = [
            {
                name: 'Building Structure',
                id: 'structure',
                children: [
                    { name: 'Foundation', id: 'foundation' },
                    { name: 'Columns', id: 'columns' },
                    { name: 'Beams', id: 'beams' },
                    { name: 'Floors', id: 'floors' }
                ]
            },
            {
                name: 'Architectural Elements',
                id: 'architecture',
                children: [
                    { name: 'Walls', id: 'walls' },
                    { name: 'Windows', id: 'windows' },
                    { name: 'Doors', id: 'doors' },
                    { name: 'Stairs', id: 'stairs' }
                ]
            },
            {
                name: 'MEP Systems',
                id: 'mep',
                children: [
                    { name: 'HVAC', id: 'hvac' },
                    { name: 'Plumbing', id: 'plumbing' },
                    { name: 'Electrical', id: 'electrical' },
                    { name: 'Fire Protection', id: 'fire' }
                ]
            }
        ];
        
        // Create tree UI
        const treeHtml = this.createTreeHtml(sampleStructure);
        treeContainer.innerHTML = treeHtml;
        
        // Add event listeners for tree nodes
        const treeToggleButtons = treeContainer.querySelectorAll('.tree-toggle');
        treeToggleButtons.forEach(button => {
            button.addEventListener('click', () => {
                const treeItem = button.closest('.tree-item');
                treeItem.classList.toggle('expanded');
                const icon = button.querySelector('i');
                if (treeItem.classList.contains('expanded')) {
                    icon.classList.replace('bi-chevron-right', 'bi-chevron-down');
                } else {
                    icon.classList.replace('bi-chevron-down', 'bi-chevron-right');
                }
            });
        });
        
        const treeElements = treeContainer.querySelectorAll('.tree-element');
        treeElements.forEach(element => {
            element.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectElement(element.dataset.id);
                
                // Highlight the selected element
                treeElements.forEach(el => el.classList.remove('selected'));
                element.classList.add('selected');
                
                // Show element properties
                this.showElementProperties(element.dataset.id);
            });
        });
        
        // Update state
        this.objectTree = sampleStructure;
    }

    /**
     * Create HTML for the tree structure
     * @param {Array} items - Array of tree items
     * @param {number} level - Indentation level
     * @returns {string} - HTML string
     */
    createTreeHtml(items, level = 0) {
        if (!items || items.length === 0) return '';
        
        let html = '<ul class="tree-list" style="padding-left: ' + (level * 16) + 'px">';
        
        items.forEach(item => {
            const hasChildren = item.children && item.children.length > 0;
            
            html += '<li class="tree-item">';
            
            if (hasChildren) {
                html += `<div class="tree-toggle"><i class="bi bi-chevron-right"></i></div>`;
            } else {
                html += `<div class="tree-toggle-placeholder"></div>`;
            }
            
            html += `<div class="tree-element" data-id="${item.id}">${item.name}</div>`;
            
            if (hasChildren) {
                html += this.createTreeHtml(item.children, level + 1);
            }
            
            html += '</li>';
        });
        
        html += '</ul>';
        return html;
    }

    /**
     * Select an element in the model
     * @param {string} elementId - ID of the element to select
     */
    selectElement(elementId) {
        console.log('Selected element:', elementId);
        
        // In a real implementation, we would highlight the element in the 3D model
        // and possibly adjust camera view to focus on it
        this.selectedObjects = [elementId];
        
        // For model-viewer, we could use annotations if supported
        if (this.modelViewer) {
            // This is a placeholder - model-viewer doesn't directly support selecting parts
            // of a model, but we could add annotations or custom highlighting
        }
    }

    /**
     * Show properties of the selected element
     * @param {string} elementId - ID of the element
     */
    showElementProperties(elementId) {
        const propertiesContainer = document.getElementById('elementProperties');
        if (!propertiesContainer) return;
        
        // For demonstration, show some sample properties
        // In a real implementation, these would be retrieved from the model
        const sampleProperties = {
            'foundation': {
                'Type': 'Concrete Slab',
                'Material': 'Reinforced Concrete',
                'Thickness': '500mm',
                'Strength Class': 'C30/37',
                'Reinforcement': 'Steel Rebar #8@12"O.C.E.W.'
            },
            'columns': {
                'Type': 'Structural Column',
                'Material': 'Steel',
                'Profile': 'W12x40',
                'Height': '3.5m',
                'Fire Rating': '2hr'
            },
            'beams': {
                'Type': 'Structural Beam',
                'Material': 'Steel',
                'Profile': 'W16x26',
                'Length': '6m',
                'Connection': 'Bolted'
            },
            'walls': {
                'Type': 'External Wall',
                'Material': 'Brick Veneer with CMU Backup',
                'Thickness': '300mm',
                'R-Value': 'R-19',
                'Fire Rating': '2hr'
            },
            'windows': {
                'Type': 'Double-Hung Window',
                'Material': 'Aluminum Frame with Low-E Glass',
                'Size': '1.2m x 1.8m',
                'U-Factor': '0.35',
                'SHGC': '0.40'
            }
        };
        
        // Default properties if none are found
        const defaultProperties = {
            'Type': 'Unknown Element',
            'ID': elementId,
            'Status': 'Loaded'
        };
        
        const properties = sampleProperties[elementId] || defaultProperties;
        
        // Create properties table
        let propertiesHtml = '<table class="table table-sm table-striped">';
        propertiesHtml += '<thead><tr><th>Property</th><th>Value</th></tr></thead>';
        propertiesHtml += '<tbody>';
        
        Object.entries(properties).forEach(([key, value]) => {
            propertiesHtml += `<tr><td>${key}</td><td>${value}</td></tr>`;
        });
        
        propertiesHtml += '</tbody></table>';
        propertiesContainer.innerHTML = propertiesHtml;
    }

    /**
     * Called when model is loaded
     */
    onModelLoaded() {
        console.log('Model loaded event fired');
        this.showLoadingIndicator(false);
    }

    /**
     * Reset the view to default camera position
     */
    resetView() {
        if (this.modelViewer) {
            this.modelViewer.cameraOrbit = 'auto auto auto';
            this.modelViewer.cameraTarget = 'auto auto auto';
            this.modelViewer.fieldOfView = 'auto';
        }
    }

    /**
     * Take a screenshot of the current view
     */
    takeScreenshot() {
        if (this.modelViewer) {
            // For model-viewer, we can use the built-in toDataURL method if available
            const img = this.modelViewer.toDataURL('image/png');
            
            // Create a download link
            const link = document.createElement('a');
            link.href = img;
            link.download = 'bim-screenshot-' + new Date().toISOString().slice(0, 10) + '.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    /**
     * Toggle wireframe mode
     */
    toggleWireframe() {
        this.isWireframe = !this.isWireframe;
        
        if (this.modelViewer) {
            // Model-viewer doesn't have a built-in wireframe mode
            // This is a placeholder - in a real implementation, we might 
            // need to modify the model or use custom shaders
            console.log('Wireframe mode toggled:', this.isWireframe);
            
            // Visual feedback for the user
            const toggleButton = document.getElementById('toggleWireframe');
            if (toggleButton) {
                if (this.isWireframe) {
                    toggleButton.classList.replace('btn-outline-success', 'btn-success');
                } else {
                    toggleButton.classList.replace('btn-success', 'btn-outline-success');
                }
            }
        }
    }
}
