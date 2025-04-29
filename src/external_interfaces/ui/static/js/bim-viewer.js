/**
 * BIM Viewer Module
 * Provides 3D visualization for building models
 */

const bimViewer = {
    containerId: null,
    container: null,
    scene: null,
    camera: null,
    renderer: null,
    controls: null,
    building: null,
    isFullView: false,
    
    // Initialize the viewer
    init: function(containerId, full = false) {
        // Store settings
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.isFullView = full;
        
        if (!this.container) {
            console.error(`Viewer container with ID ${containerId} not found`);
            return;
        }
        
        // Initialize three.js components
        this.initScene();
        this.initCamera();
        this.initRenderer();
        this.initControls();
        this.initLights();
        
        // Add sample building
        this.createSampleBuilding();
        
        // Add event listeners
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Start animation loop
        this.animate();
        
        // Add controls if in full view
        if (this.isFullView) {
            this.addViewerControls();
        }
        
        console.log(`BIM Viewer initialized in ${full ? 'full' : 'mini'} mode`);
    },
    
    // Initialize the scene
    initScene: function() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x050a13);
        
        // Add a grid for reference in full view
        if (this.isFullView) {
            const grid = new THREE.GridHelper(100, 100, 0x555555, 0x333333);
            this.scene.add(grid);
        }
    },
    
    // Initialize the camera
    initCamera: function() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
        this.camera.position.set(30, 20, 30);
        this.camera.lookAt(0, 0, 0);
    },
    
    // Initialize the renderer
    initRenderer: function() {
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);
    },
    
    // Initialize the controls
    initControls: function() {
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = false;
        this.controls.minDistance = 10;
        this.controls.maxDistance = 100;
        this.controls.maxPolarAngle = Math.PI / 2;
    },
    
    // Initialize the lights
    initLights: function() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 1);
        this.scene.add(ambientLight);
        
        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 50, 50);
        directionalLight.castShadow = true;
        
        // Configure shadow properties
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 500;
        
        this.scene.add(directionalLight);
        
        // Add some colored spotlights for the cosmic theme
        const spotLight1 = new THREE.SpotLight(0xe00d79, 0.8, 100, Math.PI / 4, 0.3);
        spotLight1.position.set(20, 40, 20);
        this.scene.add(spotLight1);
        
        const spotLight2 = new THREE.SpotLight(0xb80596, 0.8, 100, Math.PI / 4, 0.3);
        spotLight2.position.set(-20, 40, -20);
        this.scene.add(spotLight2);
    },
    
    // Create a sample building
    createSampleBuilding: function() {
        const buildingGroup = new THREE.Group();
        
        // Base/ground floor
        const baseGeometry = new THREE.BoxGeometry(30, 1, 30);
        const baseMaterial = new THREE.MeshStandardMaterial({ color: 0x333333 });
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        base.position.y = -0.5;
        base.receiveShadow = true;
        buildingGroup.add(base);
        
        // Main building tower
        const towerGeometry = new THREE.BoxGeometry(20, 30, 20);
        const towerMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x555555,
            transparent: true,
            opacity: 0.9,
            metalness: 0.8,
            roughness: 0.2
        });
        const tower = new THREE.Mesh(towerGeometry, towerMaterial);
        tower.position.y = 15;
        tower.castShadow = true;
        tower.receiveShadow = true;
        buildingGroup.add(tower);
        
        // Add floors
        for (let i = 1; i <= 17; i++) {
            const floorGeometry = new THREE.BoxGeometry(22, 0.3, 22);
            const floorMaterial = new THREE.MeshStandardMaterial({ color: 0xe00d79, emissive: 0xe00d79, emissiveIntensity: 0.2 });
            const floor = new THREE.Mesh(floorGeometry, floorMaterial);
            floor.position.y = i * 2 - 0.5;
            floor.castShadow = true;
            floor.receiveShadow = true;
            buildingGroup.add(floor);
        }
        
        // Add windows as a pattern
        const windowMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x88ccff,
            transparent: true,
            opacity: 0.7,
            metalness: 0.9,
            roughness: 0.1,
            emissive: 0x4488aa,
            emissiveIntensity: 0.2
        });
        
        // Front windows
        for (let y = 0; y < 15; y++) {
            for (let x = 0; x < 8; x++) {
                const windowGeometry = new THREE.BoxGeometry(1.5, 1.5, 0.1);
                const window = new THREE.Mesh(windowGeometry, windowMaterial);
                window.position.set(-7 + x * 2, 2 + y * 2, 10.1);
                buildingGroup.add(window);
            }
        }
        
        // Back windows
        for (let y = 0; y < 15; y++) {
            for (let x = 0; x < 8; x++) {
                const windowGeometry = new THREE.BoxGeometry(1.5, 1.5, 0.1);
                const window = new THREE.Mesh(windowGeometry, windowMaterial);
                window.position.set(-7 + x * 2, 2 + y * 2, -10.1);
                window.rotation.y = Math.PI;
                buildingGroup.add(window);
            }
        }
        
        // Left windows
        for (let y = 0; y < 15; y++) {
            for (let z = 0; z < 8; z++) {
                const windowGeometry = new THREE.BoxGeometry(0.1, 1.5, 1.5);
                const window = new THREE.Mesh(windowGeometry, windowMaterial);
                window.position.set(-10.1, 2 + y * 2, -7 + z * 2);
                buildingGroup.add(window);
            }
        }
        
        // Right windows
        for (let y = 0; y < 15; y++) {
            for (let z = 0; z < 8; z++) {
                const windowGeometry = new THREE.BoxGeometry(0.1, 1.5, 1.5);
                const window = new THREE.Mesh(windowGeometry, windowMaterial);
                window.position.set(10.1, 2 + y * 2, -7 + z * 2);
                buildingGroup.add(window);
            }
        }
        
        // Add rooftop features
        const roofGeometry = new THREE.BoxGeometry(15, 2, 15);
        const roofMaterial = new THREE.MeshStandardMaterial({ color: 0x222222 });
        const roof = new THREE.Mesh(roofGeometry, roofMaterial);
        roof.position.y = 31;
        roof.castShadow = true;
        roof.receiveShadow = true;
        buildingGroup.add(roof);
        
        // Add antenna/spire
        const spireGeometry = new THREE.CylinderGeometry(0.2, 0.5, 10, 8);
        const spireMaterial = new THREE.MeshStandardMaterial({ color: 0xb80596, emissive: 0xb80596, emissiveIntensity: 0.5 });
        const spire = new THREE.Mesh(spireGeometry, spireMaterial);
        spire.position.y = 37;
        spire.castShadow = true;
        buildingGroup.add(spire);
        
        // Add the building to the scene
        this.scene.add(buildingGroup);
        this.building = buildingGroup;
    },
    
    // Add viewer controls (for full view)
    addViewerControls: function() {
        const controlsDiv = document.createElement('div');
        controlsDiv.className = 'viewer-controls';
        controlsDiv.innerHTML = `
            <button class="viewer-control-btn" id="view-front">
                <i data-feather="arrow-up"></i>
            </button>
            <button class="viewer-control-btn" id="view-side">
                <i data-feather="arrow-right"></i>
            </button>
            <button class="viewer-control-btn" id="view-top">
                <i data-feather="arrow-down"></i>
            </button>
            <button class="viewer-control-btn" id="view-3d">
                <i data-feather="box"></i>
            </button>
        `;
        
        this.container.appendChild(controlsDiv);
        
        // Initialize feather icons
        feather.replace();
        
        // Add event listeners for controls
        document.getElementById('view-front').addEventListener('click', () => {
            this.setCameraPosition(0, 15, 50);
        });
        
        document.getElementById('view-side').addEventListener('click', () => {
            this.setCameraPosition(50, 15, 0);
        });
        
        document.getElementById('view-top').addEventListener('click', () => {
            this.setCameraPosition(0, 50, 0);
        });
        
        document.getElementById('view-3d').addEventListener('click', () => {
            this.setCameraPosition(30, 20, 30);
        });
    },
    
    // Set camera position and target
    setCameraPosition: function(x, y, z) {
        // Create a tween for smooth camera movement
        const duration = 1000;
        const cameraPosition = this.camera.position.clone();
        
        // Simple animation without TWEEN
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease function (ease-out cubic)
            const ease = 1 - Math.pow(1 - progress, 3);
            
            // Update camera position
            this.camera.position.x = cameraPosition.x + (x - cameraPosition.x) * ease;
            this.camera.position.y = cameraPosition.y + (y - cameraPosition.y) * ease;
            this.camera.position.z = cameraPosition.z + (z - cameraPosition.z) * ease;
            
            // Look at center
            this.camera.lookAt(0, 15, 0);
            
            // Continue animation if not complete
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        // Start animation
        animate();
    },
    
    // Handle window resize
    onWindowResize: function() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    },
    
    // Animation loop
    animate: function() {
        requestAnimationFrame(() => this.animate());
        
        // Update controls
        if (this.controls) {
            this.controls.update();
        }
        
        // Render scene
        this.renderer.render(this.scene, this.camera);
    }
};

// Make sure Three.js is loaded before using this module
// This code assumes Three.js and OrbitControls are already loaded in the page
