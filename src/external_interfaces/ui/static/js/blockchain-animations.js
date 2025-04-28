/**
 * Blockchain Animations Library
 * Provides celebratory animations and micro-interaction visual feedback for blockchain actions
 */

// Animation Configuration
const AnimationConfig = {
  // Duration for animations in milliseconds
  durations: {
    short: 800,
    medium: 1500,
    long: 2500
  },
  
  // Colors for various animation states
  colors: {
    success: '#00E676',
    pending: '#FFC107',
    error: '#FF5252',
    primary: '#E00D79',
    secondary: '#2196F3',
    highlight: '#00E5FF',
    glow: 'rgba(224, 13, 121, 0.8)'
  },
  
  // Default particle settings
  particles: {
    count: {
      small: 30,
      medium: 80,
      large: 150
    },
    size: {
      min: 2,
      max: 8
    },
    velocity: {
      min: 1,
      max: 3
    }
  }
};

/**
 * Creates a canvas element for animations
 * @param {string} containerId - The ID of the container element
 * @param {Object} options - Animation options
 * @returns {HTMLCanvasElement} - The created canvas element
 */
function createAnimationCanvas(containerId, options = {}) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`Container with ID '${containerId}' not found`);
    return null;
  }
  
  // Create canvas element
  const canvas = document.createElement('canvas');
  canvas.className = 'animation-canvas';
  
  // Set canvas size to match container
  canvas.width = container.offsetWidth;
  canvas.height = container.offsetHeight;
  
  // Position the canvas absolutely within the container
  canvas.style.position = 'absolute';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.pointerEvents = 'none'; // Allows clicking through the canvas
  canvas.style.zIndex = options.zIndex || '1000';
  
  // Add to container
  if (container.style.position !== 'absolute' && container.style.position !== 'relative') {
    container.style.position = 'relative';
  }
  container.appendChild(canvas);
  
  return canvas;
}

/**
 * Particle class for confetti and other particle effects
 */
class Particle {
  constructor(canvas, options = {}) {
    const ctx = canvas.getContext('2d');
    
    this.canvas = canvas;
    this.ctx = ctx;
    this.x = options.x || Math.random() * canvas.width;
    this.y = options.y || Math.random() * canvas.height;
    this.size = options.size || Math.random() * (AnimationConfig.particles.size.max - AnimationConfig.particles.size.min) + AnimationConfig.particles.size.min;
    this.color = options.color || getRandomColor();
    this.velocity = {
      x: (Math.random() - 0.5) * (options.velocityFactor || 1) * (AnimationConfig.particles.velocity.max - AnimationConfig.particles.velocity.min) + AnimationConfig.particles.velocity.min,
      y: (Math.random() - 0.5) * (options.velocityFactor || 1) * (AnimationConfig.particles.velocity.max - AnimationConfig.particles.velocity.min) + AnimationConfig.particles.velocity.min
    };
    this.gravity = options.gravity || 0.05;
    this.friction = options.friction || 0.97;
    this.life = 1; // Life from 1 to 0
    this.decay = options.decay || 0.01;
    this.shape = options.shape || 'circle'; // 'circle', 'square', 'triangle', 'line', 'hexagon'
    this.opacity = options.opacity !== undefined ? options.opacity : 1;
    this.rotation = options.rotation || Math.random() * 360; // For shapes that can rotate
    this.rotationSpeed = (Math.random() - 0.5) * 2;
  }
  
  update() {
    // Apply gravity and friction
    this.velocity.y += this.gravity;
    this.velocity.x *= this.friction;
    this.velocity.y *= this.friction;
    
    // Update position
    this.x += this.velocity.x;
    this.y += this.velocity.y;
    
    // Update rotation
    this.rotation += this.rotationSpeed;
    
    // Decay life
    this.life -= this.decay;
    
    // Boundary check - bounce off edges
    if (this.x <= 0 || this.x >= this.canvas.width) {
      this.velocity.x *= -0.5;
    }
    
    if (this.y <= 0 || this.y >= this.canvas.height) {
      this.velocity.y *= -0.5;
      this.y = Math.min(this.y, this.canvas.height);
    }
  }
  
  draw() {
    this.ctx.save();
    this.ctx.globalAlpha = this.life * this.opacity;
    this.ctx.fillStyle = this.color;
    this.ctx.translate(this.x, this.y);
    this.ctx.rotate(this.rotation * Math.PI / 180);
    
    switch (this.shape) {
      case 'square':
        this.ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size);
        break;
      case 'triangle':
        this.ctx.beginPath();
        this.ctx.moveTo(0, -this.size / 2);
        this.ctx.lineTo(this.size / 2, this.size / 2);
        this.ctx.lineTo(-this.size / 2, this.size / 2);
        this.ctx.closePath();
        this.ctx.fill();
        break;
      case 'line':
        this.ctx.lineWidth = this.size / 4;
        this.ctx.strokeStyle = this.color;
        this.ctx.beginPath();
        this.ctx.moveTo(0, -this.size);
        this.ctx.lineTo(0, this.size);
        this.ctx.stroke();
        break;
      case 'hexagon':
        this.drawHexagon(this.size / 2);
        break;
      case 'blockchain':
        this.drawBlockchainSymbol(this.size);
        break;  
      case 'circle':
      default:
        this.ctx.beginPath();
        this.ctx.arc(0, 0, this.size / 2, 0, Math.PI * 2);
        this.ctx.fill();
        break;
    }
    
    this.ctx.restore();
  }
  
  drawHexagon(size) {
    this.ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const angle = (i * Math.PI / 3);
      const x = size * Math.cos(angle);
      const y = size * Math.sin(angle);
      
      if (i === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
    }
    this.ctx.closePath();
    this.ctx.fill();
  }

  drawBlockchainSymbol(size) {
    // Draw a simple blockchain-like symbol
    this.ctx.beginPath();
    this.ctx.arc(0, 0, size / 2, 0, Math.PI * 2);
    this.ctx.fill();
    
    // Draw connecting lines
    this.ctx.strokeStyle = this.color;
    this.ctx.lineWidth = size / 8;
    this.ctx.beginPath();
    this.ctx.moveTo(size / 2, 0);
    this.ctx.lineTo(size, 0);
    this.ctx.stroke();
    
    this.ctx.beginPath();
    this.ctx.moveTo(-size / 2, 0);
    this.ctx.lineTo(-size, 0);
    this.ctx.stroke();
  }
  
  isAlive() {
    return this.life > 0;
  }
}

/**
 * Utility function to generate a random color
 * @returns {string} - A random hex color
 */
function getRandomColor() {
  const colors = [
    AnimationConfig.colors.primary,
    AnimationConfig.colors.secondary,
    AnimationConfig.colors.highlight,
    '#7E57C2', // Purple
    '#26A69A', // Teal
    '#FFCA28', // Amber
  ];
  return colors[Math.floor(Math.random() * colors.length)];
}

/**
 * Celebration Confetti Animation
 * @param {string} containerId - The ID of the container element
 * @param {Object} options - Animation options
 */
function playCelebrationConfetti(containerId, options = {}) {
  const canvas = createAnimationCanvas(containerId, options);
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const particles = [];
  const particleCount = options.particleCount || AnimationConfig.particles.count.medium;
  
  // Create particles
  for (let i = 0; i < particleCount; i++) {
    const shapes = ['circle', 'square', 'triangle', 'hexagon', 'blockchain'];
    const randomShape = shapes[Math.floor(Math.random() * shapes.length)];
    
    // Place particles at the bottom or center based on option
    const positionY = options.fromBottom 
      ? canvas.height + Math.random() * 20 
      : (options.fromCenter ? canvas.height / 2 : Math.random() * canvas.height);
    
    const positionX = options.fromCenter 
      ? canvas.width / 2 
      : Math.random() * canvas.width;
    
    particles.push(new Particle(canvas, {
      x: positionX,
      y: positionY,
      color: getRandomColor(),
      size: Math.random() * 10 + 5,
      shape: randomShape,
      velocityFactor: options.velocityFactor || 2,
      gravity: options.gravity !== undefined ? options.gravity : -0.05, // Negative for upward movement
      friction: 0.99,
      decay: 0.005
    }));
  }
  
  // Animation loop
  let animationId;
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Update and draw all particles
    for (let i = particles.length - 1; i >= 0; i--) {
      const particle = particles[i];
      particle.update();
      particle.draw();
      
      // Remove dead particles
      if (!particle.isAlive()) {
        particles.splice(i, 1);
      }
    }
    
    // Continue animation if particles remain
    if (particles.length > 0) {
      animationId = requestAnimationFrame(animate);
    } else {
      // Clean up when done
      cancelAnimationFrame(animationId);
      if (canvas.parentNode) {
        canvas.parentNode.removeChild(canvas);
      }
      if (options.onComplete) options.onComplete();
    }
  };
  
  // Start animation
  animate();
  
  // Auto cancel after max duration to prevent endless animations
  const maxDuration = options.duration || AnimationConfig.durations.long;
  setTimeout(() => {
    if (animationId) {
      cancelAnimationFrame(animationId);
      if (canvas.parentNode) {
        canvas.parentNode.removeChild(canvas);
      }
      if (options.onComplete) options.onComplete();
    }
  }, maxDuration);
}

/**
 * Success Transaction Animation 
 * Shows a ripple effect with checkmark
 * @param {string} containerId - The ID of the container element
 * @param {Object} options - Animation options
 */
function playSuccessAnimation(containerId, options = {}) {
  const canvas = createAnimationCanvas(containerId, options);
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  
  // Animation properties
  const maxRadius = Math.max(canvas.width, canvas.height) * 0.3;
  let currentRadius = 0;
  let alpha = 0;
  const checkmarkProgress = { value: 0 };
  
  // Animation loop
  let animationId;
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw ripple
    currentRadius = Math.min(currentRadius + maxRadius / 50, maxRadius);
    alpha = Math.min(alpha + 0.05, 0.5);
    
    ctx.beginPath();
    ctx.arc(centerX, centerY, currentRadius, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(0, 230, 118, ${0.7 - alpha})`; // Green with fading alpha
    ctx.fill();
    
    // Draw inner circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, currentRadius * 0.6, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(0, 230, 118, ${alpha * 1.5})`; // Green with increasing alpha
    ctx.fill();
    
    // Draw checkmark when ripple is almost complete
    if (currentRadius > maxRadius * 0.6) {
      checkmarkProgress.value = Math.min(checkmarkProgress.value + 0.1, 1);
      drawCheckmark(ctx, centerX, centerY, maxRadius * 0.3, checkmarkProgress.value);
    }
    
    // Continue animation until complete
    if (currentRadius < maxRadius || checkmarkProgress.value < 1) {
      animationId = requestAnimationFrame(animate);
    } else {
      // Fade out
      setTimeout(() => {
        fadeOutCanvas(canvas, () => {
          cancelAnimationFrame(animationId);
          if (canvas.parentNode) {
            canvas.parentNode.removeChild(canvas);
          }
          if (options.onComplete) options.onComplete();
        });
      }, 500);
    }
  };
  
  // Start animation
  animate();
  
  // Auto cancel after max duration
  const maxDuration = options.duration || AnimationConfig.durations.medium;
  setTimeout(() => {
    if (animationId) {
      cancelAnimationFrame(animationId);
      if (canvas.parentNode) {
        canvas.parentNode.removeChild(canvas);
      }
      if (options.onComplete) options.onComplete();
    }
  }, maxDuration);
}

/**
 * Draw checkmark with animation progress
 */
function drawCheckmark(ctx, x, y, size, progress) {
  ctx.save();
  ctx.strokeStyle = '#FFFFFF';
  ctx.lineWidth = size / 5;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  
  // Calculate checkmark points
  const startX = x - size * 0.5;
  const startY = y;
  const midX = x - size * 0.1;
  const midY = y + size * 0.4;
  const endX = x + size * 0.5;
  const endY = y - size * 0.4;
  
  // Draw first part of checkmark (shorter line)
  if (progress <= 0.5) {
    const firstProgress = progress * 2; // Scale to 0-1 for first half
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(
      startX + (midX - startX) * firstProgress,
      startY + (midY - startY) * firstProgress
    );
    ctx.stroke();
  } else {
    // First part complete
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(midX, midY);
    ctx.stroke();
    
    // Draw second part (longer line)
    const secondProgress = (progress - 0.5) * 2; // Scale to 0-1 for second half
    ctx.beginPath();
    ctx.moveTo(midX, midY);
    ctx.lineTo(
      midX + (endX - midX) * secondProgress,
      midY + (endY - midY) * secondProgress
    );
    ctx.stroke();
  }
  
  ctx.restore();
}

/**
 * Fade out animation for a canvas
 */
function fadeOutCanvas(canvas, callback) {
  let opacity = 1;
  const fadeStep = 0.05;
  
  const fadeInterval = setInterval(() => {
    opacity -= fadeStep;
    canvas.style.opacity = opacity;
    
    if (opacity <= 0) {
      clearInterval(fadeInterval);
      if (callback) callback();
    }
  }, 30);
}

/**
 * Blockchain Transaction Animation
 * Visualizes a transaction moving through the blockchain
 * @param {string} containerId - The ID of the container element
 * @param {Object} options - Animation options
 */
function playBlockchainTransactionAnimation(containerId, options = {}) {
  const canvas = createAnimationCanvas(containerId, options);
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const blocks = [];
  const numBlocks = options.numBlocks || 5;
  const blockSize = Math.min(canvas.width / (numBlocks * 2), 30);
  const spacing = canvas.width / (numBlocks + 1);
  const centerY = canvas.height / 2;
  
  // Create blockchain blocks
  for (let i = 0; i < numBlocks; i++) {
    blocks.push({
      x: spacing * (i + 1),
      y: centerY,
      size: blockSize,
      active: false,
      pulseSize: 0,
      alpha: 1
    });
  }
  
  // Transaction object that moves through the blockchain
  const transaction = {
    x: 0,
    y: centerY,
    size: blockSize / 2,
    currentBlock: -1,
    speed: options.speed || 3
  };
  
  // Animation loop
  let animationId;
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw connecting lines between blocks
    ctx.strokeStyle = `rgba(224, 13, 121, 0.4)`;
    ctx.lineWidth = 2;
    for (let i = 0; i < blocks.length - 1; i++) {
      ctx.beginPath();
      ctx.moveTo(blocks[i].x, blocks[i].y);
      ctx.lineTo(blocks[i + 1].x, blocks[i + 1].y);
      ctx.stroke();
    }
    
    // Draw blocks
    blocks.forEach((block, index) => {
      // Draw pulse effect if block is active
      if (block.active) {
        block.pulseSize = Math.min(block.pulseSize + 0.5, blockSize * 1.5);
        ctx.beginPath();
        ctx.arc(block.x, block.y, block.pulseSize, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(224, 13, 121, ${0.5 - block.pulseSize / (blockSize * 3)})`; 
        ctx.fill();
      } else {
        block.pulseSize = 0;
      }
      
      // Draw block
      ctx.beginPath();
      ctx.arc(block.x, block.y, block.size, 0, Math.PI * 2);
      ctx.fillStyle = block.active ? AnimationConfig.colors.primary : `rgba(33, 150, 243, ${block.alpha})`;
      ctx.fill();
      
      // Draw block index
      ctx.fillStyle = '#FFFFFF';
      ctx.font = `${blockSize / 2}px Arial`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(index + 1, block.x, block.y);
    });
    
    // Update and draw transaction
    if (transaction.currentBlock < blocks.length) {
      transaction.x += transaction.speed;
      
      // Check if transaction reached a block
      blocks.forEach((block, index) => {
        if (Math.abs(transaction.x - block.x) < 5 && transaction.currentBlock < index) {
          transaction.currentBlock = index;
          block.active = true;
          
          // Add mini celebration at this block
          const burstParticles = [];
          const particleCount = 20;
          
          for (let i = 0; i < particleCount; i++) {
            burstParticles.push(new Particle(canvas, {
              x: block.x,
              y: block.y,
              color: getRandomColor(),
              size: Math.random() * 3 + 2,
              velocityFactor: 1,
              gravity: 0.02,
              friction: 0.95,
              decay: 0.03
            }));
          }
          
          // Mini animation for this block
          const miniAnimate = () => {
            // Only update particles, main animation handles clearing
            
            // Update and draw all particles
            for (let i = burstParticles.length - 1; i >= 0; i--) {
              const particle = burstParticles[i];
              particle.update();
              particle.draw();
              
              // Remove dead particles
              if (!particle.isAlive()) {
                burstParticles.splice(i, 1);
              }
            }
            
            // Continue mini animation if particles remain
            if (burstParticles.length > 0) {
              requestAnimationFrame(miniAnimate);
            }
          };
          
          // Start mini animation
          miniAnimate();
        }
      });
      
      // Draw transaction
      ctx.beginPath();
      ctx.arc(transaction.x, transaction.y, transaction.size, 0, Math.PI * 2);
      ctx.fillStyle = AnimationConfig.colors.highlight;
      ctx.fill();
    } else {
      // Animation complete
      setTimeout(() => {
        fadeOutCanvas(canvas, () => {
          cancelAnimationFrame(animationId);
          if (canvas.parentNode) {
            canvas.parentNode.removeChild(canvas);
          }
          if (options.onComplete) options.onComplete();
        });
      }, 500);
    }
    
    // Continue animation
    if (transaction.x < canvas.width + transaction.size) {
      animationId = requestAnimationFrame(animate);
    } else {
      if (options.onComplete) options.onComplete();
    }
  };
  
  // Start animation
  animate();
  
  // Auto cancel after max duration
  const maxDuration = options.duration || AnimationConfig.durations.long * 1.5;
  setTimeout(() => {
    if (animationId) {
      cancelAnimationFrame(animationId);
      if (canvas.parentNode) {
        canvas.parentNode.removeChild(canvas);
      }
      if (options.onComplete) options.onComplete();
    }
  }, maxDuration);
}

/**
 * Wallet Connection Animation
 * Shows a connection effect between user and wallet
 * @param {string} containerId - The ID of the container element
 * @param {Object} options - Animation options
 */
function playWalletConnectionAnimation(containerId, options = {}) {
  const canvas = createAnimationCanvas(containerId, options);
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const particles = [];
  
  // Create particles flowing along a connection line
  const createConnectionParticles = () => {
    const startX = canvas.width * 0.1;
    const startY = canvas.height * 0.5;
    const endX = canvas.width * 0.9;
    const endY = canvas.height * 0.5;
    
    // Add new particles at the start point
    for (let i = 0; i < 3; i++) {
      particles.push({
        x: startX,
        y: startY,
        size: Math.random() * 4 + 2,
        speed: Math.random() * 3 + 2,
        color: AnimationConfig.colors.highlight,
        progress: 0
      });
    }
    
    // Draw connection line
    ctx.strokeStyle = `rgba(224, 13, 121, 0.2)`;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.stroke();
    
    // Draw user icon (circle) at start
    ctx.beginPath();
    ctx.arc(startX, startY, 15, 0, Math.PI * 2);
    ctx.fillStyle = AnimationConfig.colors.secondary;
    ctx.fill();
    ctx.font = '15px Arial';
    ctx.fillStyle = '#FFFFFF';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('U', startX, startY);
    
    // Draw wallet icon (square) at end
    ctx.beginPath();
    ctx.rect(endX - 15, endY - 15, 30, 30);
    ctx.fillStyle = AnimationConfig.colors.primary;
    ctx.fill();
    ctx.font = '15px Arial';
    ctx.fillStyle = '#FFFFFF';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('W', endX, endY);
    
    // Update and draw particles
    for (let i = particles.length - 1; i >= 0; i--) {
      const particle = particles[i];
      
      // Update progress
      particle.progress += particle.speed / 100;
      
      // Calculate position on line
      particle.x = startX + (endX - startX) * particle.progress;
      particle.y = startY + (endY - startY) * particle.progress;
      
      // Draw particle
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      ctx.fillStyle = particle.color;
      ctx.fill();
      
      // Remove particles that reached the end
      if (particle.progress >= 1) {
        particles.splice(i, 1);
        
        // Add pulse effect at wallet
        ctx.beginPath();
        ctx.arc(endX, endY, 20, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(224, 13, 121, 0.3)`;
        ctx.fill();
      }
    }
  };
  
  // Animation loop
  let animationFrames = 0;
  const maxFrames = options.frames || 180; // About 3 seconds at 60fps
  
  let animationId;
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    createConnectionParticles();
    
    animationFrames++;
    
    // Complete animation after max frames
    if (animationFrames < maxFrames) {
      animationId = requestAnimationFrame(animate);
    } else {
      // Celebration at the end
      playCelebrationConfetti(containerId, {
        particleCount: 50,
        fromCenter: true,
        duration: 1000,
        onComplete: () => {
          if (options.onComplete) options.onComplete();
        }
      });
      
      // Clean up main animation
      cancelAnimationFrame(animationId);
    }
  };
  
  // Start animation
  animate();
  
  // Auto cancel after max duration
  const maxDuration = options.duration || AnimationConfig.durations.medium;
  setTimeout(() => {
    if (animationId) {
      cancelAnimationFrame(animationId);
      if (canvas.parentNode) {
        canvas.parentNode.removeChild(canvas);
      }
      if (options.onComplete) options.onComplete();
    }
  }, maxDuration);
}

/**
 * Micro-interaction rewards system
 * Tracks user actions and triggers celebratory animations
 */
class MicroRewards {
  constructor() {
    this.userScore = 0;
    this.userLevel = 1;
    this.userActions = {
      walletConnected: false,
      contractSigned: false,
      transactionSubmitted: false,
      loginCount: 0,
      contractViews: 0
    };
    
    // Initialize from localStorage if available
    this.loadState();
    
    // Thresholds for leveling up
    this.levelThresholds = [0, 100, 250, 500, 1000, 2000];
  }
  
  /**
   * Load user rewards state from localStorage
   */
  loadState() {
    try {
      const savedState = localStorage.getItem('micro_rewards_state');
      if (savedState) {
        const state = JSON.parse(savedState);
        this.userScore = state.userScore || 0;
        this.userLevel = state.userLevel || 1;
        this.userActions = state.userActions || this.userActions;
      }
    } catch (e) {
      console.error('Failed to load rewards state:', e);
    }
  }
  
  /**
   * Save user rewards state to localStorage
   */
  saveState() {
    try {
      const state = {
        userScore: this.userScore,
        userLevel: this.userLevel,
        userActions: this.userActions
      };
      localStorage.setItem('micro_rewards_state', JSON.stringify(state));
    } catch (e) {
      console.error('Failed to save rewards state:', e);
    }
  }
  
  /**
   * Award points for user action
   * @param {string} action - The action type
   * @param {number} points - Points to award
   * @param {Object} options - Animation options
   */
  awardPoints(action, points, options = {}) {
    // Update user score
    this.userScore += points;
    
    // Update specific action tracking
    switch (action) {
      case 'wallet_connect':
        this.userActions.walletConnected = true;
        break;
      case 'contract_sign':
        this.userActions.contractSigned = true;
        break;
      case 'transaction_submit':
        this.userActions.transactionSubmitted = true;
        break;
      case 'login':
        this.userActions.loginCount++;
        break;
      case 'view_contract':
        this.userActions.contractViews++;
        break;
    }
    
    // Check for level up
    const newLevel = this.calculateLevel();
    const leveledUp = newLevel > this.userLevel;
    this.userLevel = newLevel;
    
    // Save state
    this.saveState();
    
    // Show animation based on action and points
    if (options.animationContainer) {
      this.playActionAnimation(action, points, options.animationContainer, {
        onComplete: () => {
          // Show level up animation if leveled up
          if (leveledUp && options.animationContainer) {
            this.playLevelUpAnimation(options.animationContainer);
          }
          
          if (options.onComplete) options.onComplete();
        }
      });
    }
    
    return {
      points,
      newTotal: this.userScore,
      level: this.userLevel,
      leveledUp
    };
  }
  
  /**
   * Calculate user level based on score
   * @returns {number} - The user level
   */
  calculateLevel() {
    for (let i = this.levelThresholds.length - 1; i >= 0; i--) {
      if (this.userScore >= this.levelThresholds[i]) {
        return i + 1;
      }
    }
    return 1;
  }
  
  /**
   * Play action-specific animation
   * @param {string} action - The action type
   * @param {number} points - Points awarded
   * @param {string} containerId - Container for animation
   * @param {Object} options - Animation options
   */
  playActionAnimation(action, points, containerId, options = {}) {
    switch (action) {
      case 'wallet_connect':
        playWalletConnectionAnimation(containerId, {
          duration: 2000,
          onComplete: () => {
            this.showPointsGained(containerId, points, options);
          }
        });
        break;
      case 'contract_sign':
        playSuccessAnimation(containerId, {
          duration: 1500,
          onComplete: () => {
            this.showPointsGained(containerId, points, options);
          }
        });
        break;
      case 'transaction_submit':
        playBlockchainTransactionAnimation(containerId, {
          duration: 3000,
          onComplete: () => {
            this.showPointsGained(containerId, points, options);
          }
        });
        break;
      default:
        // Simple confetti for other actions
        playCelebrationConfetti(containerId, {
          particleCount: 30,
          duration: 1500,
          onComplete: () => {
            this.showPointsGained(containerId, points, options);
          }
        });
        break;
    }
  }
  
  /**
   * Show points gained animation
   * @param {string} containerId - Container for animation
   * @param {number} points - Points to display
   * @param {Object} options - Animation options
   */
  showPointsGained(containerId, points, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Create floating points element
    const pointsEl = document.createElement('div');
    pointsEl.className = 'floating-points';
    pointsEl.innerHTML = `+${points} pts`;
    pointsEl.style.position = 'absolute';
    pointsEl.style.top = '50%';
    pointsEl.style.left = '50%';
    pointsEl.style.transform = 'translate(-50%, -50%)';
    pointsEl.style.color = AnimationConfig.colors.highlight;
    pointsEl.style.fontSize = '24px';
    pointsEl.style.fontWeight = 'bold';
    pointsEl.style.textShadow = '0 0 10px rgba(0, 229, 255, 0.5)';
    pointsEl.style.zIndex = '1001';
    pointsEl.style.opacity = '0';
    pointsEl.style.transition = 'all 1.5s ease-out';
    
    container.appendChild(pointsEl);
    
    // Animate points
    setTimeout(() => {
      pointsEl.style.opacity = '1';
      pointsEl.style.transform = 'translate(-50%, -100%)';
    }, 10);
    
    // Remove after animation
    setTimeout(() => {
      pointsEl.style.opacity = '0';
      setTimeout(() => {
        if (container.contains(pointsEl)) {
          container.removeChild(pointsEl);
        }
        if (options.onComplete) options.onComplete();
      }, 500);
    }, 1500);
  }
  
  /**
   * Play level up animation
   * @param {string} containerId - Container for animation
   */
  playLevelUpAnimation(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Create level up element
    const levelEl = document.createElement('div');
    levelEl.className = 'level-up-notification';
    levelEl.innerHTML = `
      <div style="font-size: 28px; font-weight: bold; margin-bottom: 5px; color: ${AnimationConfig.colors.primary};">
        LEVEL UP!
      </div>
      <div style="font-size: 20px;">
        You are now Level ${this.userLevel}
      </div>
    `;
    levelEl.style.position = 'fixed';
    levelEl.style.top = '50%';
    levelEl.style.left = '50%';
    levelEl.style.transform = 'translate(-50%, -50%)';
    levelEl.style.background = 'rgba(17, 17, 34, 0.9)';
    levelEl.style.borderRadius = '10px';
    levelEl.style.padding = '20px 30px';
    levelEl.style.boxShadow = `0 0 20px ${AnimationConfig.colors.glow}`;
    levelEl.style.zIndex = '2000';
    levelEl.style.textAlign = 'center';
    levelEl.style.border = `2px solid ${AnimationConfig.colors.primary}`;
    levelEl.style.opacity = '0';
    levelEl.style.transition = 'all 0.5s ease-out';
    
    document.body.appendChild(levelEl);
    
    // Animate level up notification
    setTimeout(() => {
      levelEl.style.opacity = '1';
      
      // Play celebration animation
      playCelebrationConfetti('app-container', {
        particleCount: 150,
        fromCenter: true,
        duration: 3000
      });
      
    }, 10);
    
    // Remove after animation
    setTimeout(() => {
      levelEl.style.opacity = '0';
      setTimeout(() => {
        if (document.body.contains(levelEl)) {
          document.body.removeChild(levelEl);
        }
      }, 500);
    }, 4000);
  }
  
  /**
   * Get user rewards summary
   * @returns {Object} - User rewards state
   */
  getRewardsSummary() {
    return {
      score: this.userScore,
      level: this.userLevel,
      nextLevelAt: this.getNextLevelThreshold(),
      progress: this.getLevelProgress(),
      actions: this.userActions
    };
  }
  
  /**
   * Get threshold for next level
   * @returns {number} - Points needed for next level
   */
  getNextLevelThreshold() {
    const currentLevel = this.userLevel;
    if (currentLevel >= this.levelThresholds.length) {
      return null; // Max level reached
    }
    return this.levelThresholds[currentLevel];
  }
  
  /**
   * Get progress towards next level (0-100%)
   * @returns {number} - Progress percentage
   */
  getLevelProgress() {
    const currentLevel = this.userLevel;
    const nextThreshold = this.getNextLevelThreshold();
    
    if (nextThreshold === null) {
      return 100; // Max level reached
    }
    
    const currentThreshold = this.levelThresholds[currentLevel - 1];
    const range = nextThreshold - currentThreshold;
    const progress = this.userScore - currentThreshold;
    
    return Math.min(Math.floor((progress / range) * 100), 100);
  }
}

// Create global instance of the rewards system
window.microRewards = new MicroRewards();

// Export functions and classes
export {
  playCelebrationConfetti,
  playSuccessAnimation,
  playBlockchainTransactionAnimation,
  playWalletConnectionAnimation,
  AnimationConfig,
  MicroRewards
};