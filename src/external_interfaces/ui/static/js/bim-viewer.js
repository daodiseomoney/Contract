/**
 * BIM Viewer Component for BIM AI Management Dashboard
 * A simplified 3D viewer for building models
 */

const bimViewer = {
    // Viewer container element
    container: null,
    
    // Canvas context
    canvas: null,
    ctx: null,
    
    // Viewer state
    state: {
        initialized: false,
        dataLoaded: false,
        cameraPosition: { x: 0, y: 0, z: -10 },
        cameraTarget: { x: 0, y: 0, z: 0 },
        rotating: false,
        autoRotate: false,
        showWireframe: false,
        defaultColor: '#4CAF50',
        highlightColor: '#FF4081',
        currentFloor: 1,
        totalFloors: 3,
    },
    
    // Mock building data
    buildingData: {
        name: "Cosmic Tower",
        location: "Silicon Valley, CA",
        floors: 3,
        yearBuilt: 2024,
        totalArea: 12500,
        elements: []
    },
    
    /**
     * Initialize the BIM viewer
     * @param {string} containerId - ID of the container element
     */
    init(containerId) {
        this.container = document.getElementById(containerId);
        
        if (!this.container) {
            console.error('BIM Viewer container not found');
            return;
        }
        
        // Create viewer UI
        this.createViewerUI();
        
        // Set up controls
        this.setupControls();
        
        // Generate mock building data
        this.generateMockData();
        
        // Start rendering
        this.startRenderLoop();
        
        this.state.initialized = true;
        console.log('BIM Viewer initialized');
    },
    
    /**
     * Create the viewer UI elements
     */
    createViewerUI() {
        // Create canvas and controls
        this.container.innerHTML = `
            <canvas class="bim-viewer-canvas" id="bim-canvas"></canvas>
            <div class="viewer-controls">
                <button class="viewer-control-btn" id="btn-rotate" title="Toggle Auto-Rotate">
                    <i data-feather="refresh-cw"></i>
                </button>
                <button class="viewer-control-btn" id="btn-wireframe" title="Toggle Wireframe">
                    <i data-feather="grid"></i>
                </button>
                <button class="viewer-control-btn" id="btn-floor-up" title="Next Floor">
                    <i data-feather="chevron-up"></i>
                </button>
                <button class="viewer-control-btn" id="btn-floor-down" title="Previous Floor">
                    <i data-feather="chevron-down"></i>
                </button>
                <button class="viewer-control-btn" id="btn-reset" title="Reset View">
                    <i data-feather="home"></i>
                </button>
            </div>
        `;
        
        // Initialize Feather icons
        feather.replace();
        
        // Get canvas
        this.canvas = document.getElementById('bim-canvas');
        this.ctx = this.canvas.getContext('2d');
        
        // Set canvas size
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    },
    
    /**
     * Set up viewer controls
     */
    setupControls() {
        // Toggle auto-rotate
        document.getElementById('btn-rotate').addEventListener('click', () => {
            this.state.autoRotate = !this.state.autoRotate;
        });
        
        // Toggle wireframe
        document.getElementById('btn-wireframe').addEventListener('click', () => {
            this.state.showWireframe = !this.state.showWireframe;
        });
        
        // Floor navigation
        document.getElementById('btn-floor-up').addEventListener('click', () => {
            if (this.state.currentFloor < this.state.totalFloors) {
                this.state.currentFloor++;
            }
        });
        
        document.getElementById('btn-floor-down').addEventListener('click', () => {
            if (this.state.currentFloor > 1) {
                this.state.currentFloor--;
            }
        });
        
        // Reset view
        document.getElementById('btn-reset').addEventListener('click', () => {
            this.state.cameraPosition = { x: 0, y: 0, z: -10 };
            this.state.cameraTarget = { x: 0, y: 0, z: 0 };
            this.state.autoRotate = false;
            this.state.showWireframe = false;
            this.state.currentFloor = 1;
        });
        
        // Mouse interaction for rotation
        this.canvas.addEventListener('mousedown', () => {
            this.state.rotating = true;
        });
        
        this.canvas.addEventListener('mouseup', () => {
            this.state.rotating = false;
        });
        
        this.canvas.addEventListener('mousemove', (e) => {
            if (this.state.rotating) {
                // Rotate the camera position around the target
                const deltaX = e.movementX * 0.01;
                const deltaY = e.movementY * 0.01;
                
                // Update camera position
                const x = this.state.cameraPosition.x;
                const z = this.state.cameraPosition.z;
                
                // Rotate around Y axis (left/right)
                this.state.cameraPosition.x = x * Math.cos(deltaX) - z * Math.sin(deltaX);
                this.state.cameraPosition.z = z * Math.cos(deltaX) + x * Math.sin(deltaX);
                
                // Limit vertical rotation
                const y = this.state.cameraPosition.y;
                this.state.cameraPosition.y = Math.max(-5, Math.min(5, y + deltaY));
            }
        });
    },
    
    /**
     * Resize canvas to match container size
     */
    resizeCanvas() {
        if (this.canvas) {
            this.canvas.width = this.container.clientWidth;
            this.canvas.height = this.container.clientHeight;
        }
    },
    
    /**
     * Generate mock building data for visualization
     */
    generateMockData() {
        // Reset building elements
        this.buildingData.elements = [];
        
        // Generate mock walls, floors, doors, windows
        
        // Floor 1
        this.buildingData.elements.push(
            // Floor
            {
                type: 'floor',
                position: { x: 0, y: -2, z: 0 },
                size: { x: 8, y: 0.2, z: 8 },
                color: '#78909C',
                floor: 1,
            },
            // Exterior walls
            {
                type: 'wall',
                position: { x: -4, y: -1, z: 0 },
                size: { x: 0.2, y: 2, z: 8 },
                color: '#455A64',
                floor: 1,
            },
            {
                type: 'wall',
                position: { x: 4, y: -1, z: 0 },
                size: { x: 0.2, y: 2, z: 8 },
                color: '#455A64',
                floor: 1,
            },
            {
                type: 'wall',
                position: { x: 0, y: -1, z: -4 },
                size: { x: 8, y: 2, z: 0.2 },
                color: '#455A64',
                floor: 1,
            },
            {
                type: 'wall',
                position: { x: 0, y: -1, z: 4 },
                size: { x: 8, y: 2, z: 0.2 },
                color: '#455A64',
                floor: 1,
            }
        );
        
        // Floor 2
        this.buildingData.elements.push(
            // Floor
            {
                type: 'floor',
                position: { x: 0, y: 0, z: 0 },
                size: { x: 8, y: 0.2, z: 8 },
                color: '#78909C',
                floor: 2,
            },
            // Exterior walls
            {
                type: 'wall',
                position: { x: -4, y: 1, z: 0 },
                size: { x: 0.2, y: 2, z: 8 },
                color: '#455A64',
                floor: 2,
            },
            {
                type: 'wall',
                position: { x: 4, y: 1, z: 0 },
                size: { x: 0.2, y: 2, z: 8 },
                color: '#455A64',
                floor: 2,
            },
            {
                type: 'wall',
                position: { x: 0, y: 1, z: -4 },
                size: { x: 8, y: 2, z: 0.2 },
                color: '#455A64',
                floor: 2,
            },
            {
                type: 'wall',
                position: { x: 0, y: 1, z: 4 },
                size: { x: 8, y: 2, z: 0.2 },
                color: '#455A64',
                floor: 2,
            },
            // Interior walls floor 2
            {
                type: 'wall',
                position: { x: -2, y: 1, z: 0 },
                size: { x: 0.2, y: 2, z: 8 },
                color: '#607D8B',
                floor: 2,
            }
        );
        
        // Floor 3
        this.buildingData.elements.push(
            // Floor
            {
                type: 'floor',
                position: { x: 0, y: 2, z: 0 },
                size: { x: 8, y: 0.2, z: 8 },
                color: '#78909C',
                floor: 3,
            },
            // Exterior walls
            {
                type: 'wall',
                position: { x: -3, y: 3, z: 0 },
                size: { x: 0.2, y: 2, z: 6 },
                color: '#455A64',
                floor: 3,
            },
            {
                type: 'wall',
                position: { x: 3, y: 3, z: 0 },
                size: { x: 0.2, y: 2, z: 6 },
                color: '#455A64',
                floor: 3,
            },
            {
                type: 'wall',
                position: { x: 0, y: 3, z: -3 },
                size: { x: 6, y: 2, z: 0.2 },
                color: '#455A64',
                floor: 3,
            },
            {
                type: 'wall',
                position: { x: 0, y: 3, z: 3 },
                size: { x: 6, y: 2, z: 0.2 },
                color: '#455A64',
                floor: 3,
            }
        );
        
        // Windows and doors
        for (let floor = 1; floor <= 3; floor++) {
            const yPos = (floor - 2) * 2;
            
            // Windows
            this.buildingData.elements.push(
                {
                    type: 'window',
                    position: { x: -4, y: yPos, z: -2 },
                    size: { x: 0.3, y: 1, z: 1 },
                    color: '#BBDEFB',
                    floor: floor,
                },
                {
                    type: 'window',
                    position: { x: -4, y: yPos, z: 2 },
                    size: { x: 0.3, y: 1, z: 1 },
                    color: '#BBDEFB',
                    floor: floor,
                },
                {
                    type: 'window',
                    position: { x: 4, y: yPos, z: -2 },
                    size: { x: 0.3, y: 1, z: 1 },
                    color: '#BBDEFB',
                    floor: floor,
                },
                {
                    type: 'window',
                    position: { x: 4, y: yPos, z: 2 },
                    size: { x: 0.3, y: 1, z: 1 },
                    color: '#BBDEFB',
                    floor: floor,
                }
            );
            
            // Door
            this.buildingData.elements.push({
                type: 'door',
                position: { x: 0, y: yPos - 0.5, z: 4 },
                size: { x: 1.2, y: 1, z: 0.3 },
                color: '#5D4037',
                floor: floor,
            });
        }
        
        this.state.dataLoaded = true;
    },
    
    /**
     * Start the rendering loop
     */
    startRenderLoop() {
        const render = () => {
            if (this.state.initialized) {
                this.render();
            }
            requestAnimationFrame(render);
        };
        
        render();
    },
    
    /**
     * Render the 3D scene
     */
    render() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Update camera position if auto-rotate is enabled
        if (this.state.autoRotate) {
            const x = this.state.cameraPosition.x;
            const z = this.state.cameraPosition.z;
            const angle = 0.01;
            
            this.state.cameraPosition.x = x * Math.cos(angle) - z * Math.sin(angle);
            this.state.cameraPosition.z = z * Math.cos(angle) + x * Math.sin(angle);
        }
        
        // Draw background grid
        this.drawGrid();
        
        // Get visible elements (for the current floor)
        const visibleElements = this.buildingData.elements.filter(
            element => element.floor === this.state.currentFloor
        );
        
        // Sort elements by distance (painter's algorithm)
        visibleElements.sort((a, b) => {
            const distA = this.distance(a.position, this.state.cameraPosition);
            const distB = this.distance(b.position, this.state.cameraPosition);
            return distB - distA;
        });
        
        // Draw each element
        visibleElements.forEach(element => {
            this.drawElement(element);
        });
        
        // Draw floor indicator
        this.drawFloorIndicator();
    },
    
    /**
     * Draw the background grid
     */
    drawGrid() {
        const gridSize = 20;
        const gridSpacing = 50;
        
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        this.ctx.lineWidth = 1;
        
        // Calculate center of canvas
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        // Draw horizontal grid lines
        for (let i = -gridSize; i <= gridSize; i++) {
            const y = centerY + i * gridSpacing;
            
            this.ctx.beginPath();
            this.ctx.moveTo(centerX - gridSize * gridSpacing, y);
            this.ctx.lineTo(centerX + gridSize * gridSpacing, y);
            this.ctx.stroke();
        }
        
        // Draw vertical grid lines
        for (let i = -gridSize; i <= gridSize; i++) {
            const x = centerX + i * gridSpacing;
            
            this.ctx.beginPath();
            this.ctx.moveTo(x, centerY - gridSize * gridSpacing);
            this.ctx.lineTo(x, centerY + gridSize * gridSpacing);
            this.ctx.stroke();
        }
    },
    
    /**
     * Draw a 3D element with perspective projection
     * @param {object} element - The element to draw
     */
    drawElement(element) {
        // Extract element properties
        const { position, size, color, type } = element;
        
        // Define vertices of the cuboid
        const vertices = [
            // Front face
            { x: position.x - size.x/2, y: position.y - size.y/2, z: position.z + size.z/2 },
            { x: position.x + size.x/2, y: position.y - size.y/2, z: position.z + size.z/2 },
            { x: position.x + size.x/2, y: position.y + size.y/2, z: position.z + size.z/2 },
            { x: position.x - size.x/2, y: position.y + size.y/2, z: position.z + size.z/2 },
            
            // Back face
            { x: position.x - size.x/2, y: position.y - size.y/2, z: position.z - size.z/2 },
            { x: position.x + size.x/2, y: position.y - size.y/2, z: position.z - size.z/2 },
            { x: position.x + size.x/2, y: position.y + size.y/2, z: position.z - size.z/2 },
            { x: position.x - size.x/2, y: position.y + size.y/2, z: position.z - size.z/2 },
        ];
        
        // Project vertices to 2D
        const projectedVertices = vertices.map(vertex => this.projectVertex(vertex));
        
        // Define faces (pairs of vertices that form edges)
        const faces = [
            // Front face
            [0, 1, 2, 3],
            // Back face
            [4, 5, 6, 7],
            // Top face
            [3, 2, 6, 7],
            // Bottom face
            [0, 1, 5, 4],
            // Left face
            [0, 3, 7, 4],
            // Right face
            [1, 2, 6, 5],
        ];
        
        // Draw faces
        faces.forEach(face => {
            const points = face.map(index => projectedVertices[index]);
            
            // Set fill color based on element type
            this.ctx.fillStyle = color;
            
            // Start path
            this.ctx.beginPath();
            this.ctx.moveTo(points[0].x, points[0].y);
            
            // Draw lines between vertices
            for (let i = 1; i < points.length; i++) {
                this.ctx.lineTo(points[i].x, points[i].y);
            }
            
            // Close path
            this.ctx.closePath();
            
            // Fill or stroke based on wireframe setting
            if (this.state.showWireframe) {
                this.ctx.strokeStyle = color;
                this.ctx.stroke();
            } else {
                this.ctx.fill();
                this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
                this.ctx.stroke();
            }
        });
    },
    
    /**
     * Draw floor indicator
     */
    drawFloorIndicator() {
        const text = `Floor ${this.state.currentFloor} of ${this.state.totalFloors}`;
        this.ctx.font = '14px Arial';
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
        this.ctx.fillText(text, 20, this.canvas.height - 20);
    },
    
    /**
     * Project a 3D vertex to 2D with perspective
     * @param {object} vertex - The 3D vertex { x, y, z }
     * @returns {object} The projected 2D point { x, y }
     */
    projectVertex(vertex) {
        // Translate based on camera position
        const translated = {
            x: vertex.x - this.state.cameraPosition.x,
            y: vertex.y - this.state.cameraPosition.y,
            z: vertex.z - this.state.cameraPosition.z,
        };
        
        // Apply perspective
        const focalLength = 1.5;
        const depth = Math.max(0.1, translated.z + 10);
        const scale = focalLength / depth;
        
        // Project to 2D
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        return {
            x: centerX + translated.x * scale * 50,
            y: centerY - translated.y * scale * 50, // Flip Y for screen coordinates
        };
    },
    
    /**
     * Calculate distance between two points
     * @param {object} p1 - First point { x, y, z }
     * @param {object} p2 - Second point { x, y, z }
     * @returns {number} Distance between the points
     */
    distance(p1, p2) {
        const dx = p2.x - p1.x;
        const dy = p2.y - p1.y;
        const dz = p2.z - p1.z;
        return Math.sqrt(dx * dx + dy * dy + dz * dz);
    }
};
