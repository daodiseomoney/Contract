"""
Security Patch for Daodiseo Real Estate Tokenization Platform
Apply these changes before mainnet deployment
"""

import os
import sys
import logging
import hashlib
import json
import secrets
from functools import wraps
import time
from flask import request, jsonify, session, abort, current_app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Required environment variables for blockchain operations
REQUIRED_ENV_VARS = [
    "PINGPUB_API_URL", 
    "CHAIN_ID", 
    "CONTRACT_ADDRESS", 
    "VALIDATOR_POOL_ADDRESS"
]

def validate_environment():
    """
    Validate that all required environment variables are set
    """
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.critical(f"SECURITY ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        logger.critical("Application cannot start without proper configuration.")
        sys.exit(1)
    
    # Check if we're using production values
    chain_id = os.environ.get("CHAIN_ID")
    if "testnet" in chain_id.lower():
        logger.warning("WARNING: Application is using TESTNET configuration!")
        
    logger.info("Environment validation successful.")

# Rate limiting implementation
class RateLimiter:
    """Simple rate limiter for API endpoints"""
    
    def __init__(self):
        self.requests = {}
        self.window_size = 60  # 60 seconds window
        self.max_requests = 30  # 30 requests per window
        self.max_transaction_requests = 10  # 10 transaction requests per window
        
    def _get_identifier(self):
        """Get unique identifier from request"""
        return request.remote_addr
        
    def is_rate_limited(self, transaction_endpoint=False):
        """Check if request should be rate limited"""
        identifier = self._get_identifier()
        current_time = time.time()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests
        self.requests[identifier] = [t for t in self.requests[identifier] 
                                  if current_time - t < self.window_size]
        
        # Check if too many requests
        max_allowed = self.max_transaction_requests if transaction_endpoint else self.max_requests
        if len(self.requests[identifier]) >= max_allowed:
            return True
            
        # Add current request
        self.requests[identifier].append(current_time)
        return False

# Create rate limiter instance
rate_limiter = RateLimiter()

# Security decorator for API endpoints
def secure_endpoint(f):
    """Decorator to apply security measures to API endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check rate limits
        is_transaction = 'broadcast' in request.path or 'transaction' in request.path
        if rate_limiter.is_rate_limited(transaction_endpoint=is_transaction):
            return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
        
        # Log API access
        logger.info(f"API Access: {request.method} {request.path} from {request.remote_addr}")
        
        # Add CSRF protection for non-GET requests
        if request.method != 'GET' and request.headers.get('X-CSRF-Token') != session.get('csrf_token'):
            logger.warning(f"CSRF token validation failed from {request.remote_addr}")
            return jsonify({"error": "Invalid or missing CSRF token"}), 403
            
        return f(*args, **kwargs)
    return decorated

def verify_wallet_ownership(address):
    """
    Verify a wallet address belongs to the authenticated user
    Replace with actual implementation based on your authentication system
    """
    user_address = session.get('wallet_address')
    if not user_address or user_address != address:
        logger.warning(f"Unauthorized wallet access attempt: {address}")
        abort(403)  # Forbidden
    return True

def validate_ifc_file(file_data):
    """
    Validate IFC file content
    
    Args:
        file_data: Raw bytes of the file
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValueError: If validation fails with details
    """
    if not file_data or len(file_data) < 16:
        raise ValueError("Empty or too small file")
        
    # Check file signature for IFC files (magic bytes)
    # IFC files typically start with "ISO-10303-21"
    signature = file_data[:16].decode('utf-8', errors='ignore')
    if not signature.startswith("ISO-10303-21"):
        raise ValueError("Invalid IFC file format: missing ISO-10303-21 header")
        
    # Check file size
    if len(file_data) > 100 * 1024 * 1024:  # 100MB limit
        raise ValueError("File too large (max 100MB)")
        
    # Additional validations could be added here
    
    return True

def secure_hash_file(file_data):
    """
    Create a secure hash of file content
    
    Args:
        file_data: Raw bytes of the file
        
    Returns:
        str: Secure hash of the file
    """
    # Use SHA-256 for file hashing
    return hashlib.sha256(file_data).hexdigest()

def verify_transaction_hash(tx_hash, expected_hash):
    """
    Verify that a transaction hash matches the expected hash
    
    Args:
        tx_hash: The transaction hash to verify
        expected_hash: The expected hash
        
    Returns:
        bool: True if the hashes match
    """
    if not tx_hash or not expected_hash:
        return False
        
    # Normalize hashes (remove 0x prefix if present, convert to lowercase)
    tx_hash = tx_hash.lower().replace('0x', '')
    expected_hash = expected_hash.lower().replace('0x', '')
    
    return tx_hash == expected_hash

# Sample implementation of secure transaction verification
def verify_transaction_security(transaction_data, blockchain_service):
    """
    Enhanced security verification for transactions
    
    Args:
        transaction_data: Data for the transaction
        blockchain_service: Service to interact with blockchain
        
    Returns:
        dict: Verification result with security checks
    """
    # Get transaction hash
    tx_hash = transaction_data.get('transaction_hash')
    if not tx_hash:
        return {
            'verified': False,
            'security_status': 'failed',
            'error': 'Missing transaction hash'
        }
    
    # Basic transaction verification
    status = blockchain_service.verify_transaction(tx_hash)
    
    # Enhanced security checks
    security_checks = {
        'hash_verified': False,
        'sender_verified': False,
        'content_verified': False
    }
    
    # Verify transaction was successful on blockchain
    if not status.get('verified', False):
        return {
            'verified': False,
            'security_status': 'failed',
            'error': 'Transaction not verified on blockchain',
            'security_checks': security_checks
        }
    
    # Verify content hash if provided
    content_hash = transaction_data.get('content_hash')
    if content_hash:
        memo_data = extract_memo_data(status.get('status', {}).get('memo', ''))
        if memo_data and memo_data.get('hash') == content_hash:
            security_checks['content_verified'] = True
        else:
            return {
                'verified': False,
                'security_status': 'failed',
                'error': 'Content hash verification failed',
                'security_checks': security_checks
            }
    
    # Verify sender address
    expected_sender = transaction_data.get('user_address')
    actual_sender = extract_sender_from_tx(status)
    if expected_sender and actual_sender and expected_sender == actual_sender:
        security_checks['sender_verified'] = True
    else:
        return {
            'verified': False,
            'security_status': 'failed', 
            'error': 'Sender verification failed',
            'security_checks': security_checks
        }
    
    # All security checks passed
    security_checks['hash_verified'] = True
    return {
        'verified': True,
        'security_status': 'passed',
        'security_checks': security_checks,
        'transaction_details': status
    }

def extract_memo_data(memo):
    """Extract data from transaction memo"""
    if not memo:
        return None
        
    try:
        # Try parsing as JSON
        return json.loads(memo)
    except:
        # Try legacy format (key:value|key:value)
        if '|' in memo and ':' in memo:
            data = {}
            pairs = memo.split('|')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    data[key.strip()] = value.strip()
            return data
        # Try simple format (id:hash:role)
        elif ':' in memo:
            parts = memo.split(':')
            if len(parts) >= 3:
                return {
                    'id': parts[0],
                    'hash': parts[1],
                    'role': parts[2]
                }
    
    return None

def extract_sender_from_tx(tx_status):
    """Extract sender address from transaction status"""
    try:
        # Implementation depends on your blockchain's response format
        return tx_status.get('status', {}).get('tx', {}).get('body', {}).get('messages', [{}])[0].get('from_address')
    except (IndexError, KeyError, TypeError):
        return None

def generate_csrf_token():
    """Generate a secure CSRF token"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def apply_security_headers(response):
    """
    Apply security headers to all responses
    
    Args:
        response: Flask response object
        
    Returns:
        response: Modified response with security headers
    """
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "connect-src 'self' https://*.daodiseo.com https://*.nodeshub.online; "
        "frame-src 'self'; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    
    # Other security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # HSTS - only in production
    if not current_app.debug:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response


# -----------------------------
# USAGE EXAMPLES
# -----------------------------

# 1. Add to main.py at startup
"""
# Validate environment variables before startup
validate_environment()

# Add CSRF protection
app.before_request(generate_csrf_token)

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    return apply_security_headers(response)
"""

# 2. Secure the blockchain controller endpoints
"""
@blockchain_bp.route('/account', methods=['GET'])
@secure_endpoint
def get_account():
    '''Get account information for a wallet address'''
    try:
        address = request.args.get('address')
        if not address:
            return jsonify({'error': 'Address parameter is required'}), 400
            
        # Verify wallet ownership
        verify_wallet_ownership(address)
        
        # Get account information from the blockchain
        account_info = blockchain_service.pingpub_gateway.get_account_info(address)
        
        return jsonify(account_info), 200
    
    except Exception as e:
        logger.error(f"Error in get_account: {str(e)}")
        return jsonify({'error': 'Failed to retrieve account information'}), 500
"""

# 3. Secure file upload
"""
@blockchain_bp.route('/prepare-upload', methods=['POST'])
@secure_endpoint
def prepare_upload():
    '''Prepare a transaction for uploading an IFC file hash'''
    try:
        # Check if file and address are provided
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        user_address = request.form.get('address')
        if not user_address:
            return jsonify({'error': 'User address is required'}), 400
        
        # Verify wallet ownership
        verify_wallet_ownership(user_address)
        
        # Get and validate file data
        file = request.files['file']
        file_data = file.read()
        
        try:
            validate_ifc_file(file_data)
        except ValueError as e:
            return jsonify({'error': f'Invalid IFC file: {str(e)}'}), 400
        
        # Get metadata if provided
        metadata = {}
        if 'metadata' in request.form:
            try:
                metadata = json.loads(request.form.get('metadata'))
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid metadata format'}), 400
        
        # Add filename to metadata
        metadata['filename'] = file.filename
        
        # Process the file upload
        result = blockchain_service.process_ifc_upload(file_data, user_address, metadata)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in prepare_upload: {str(e)}")
        return jsonify({'error': 'Failed to process upload'}), 500
"""

# 4. Secure transaction verification
"""
@blockchain_bp.route('/verify/<tx_hash>', methods=['GET'])
@secure_endpoint
def verify_transaction(tx_hash):
    '''Verify a transaction on the blockchain with enhanced security'''
    try:
        # Get expected content hash if available
        content_hash = request.args.get('content_hash')
        user_address = request.args.get('address')
        
        # Create transaction data for verification
        transaction_data = {
            'transaction_hash': tx_hash,
            'content_hash': content_hash,
            'user_address': user_address
        }
        
        # Enhanced security verification
        result = verify_transaction_security(transaction_data, blockchain_service)
        
        if not result.get('verified'):
            logger.warning(f"Transaction verification failed: {result.get('error')}")
            
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in verify_transaction: {str(e)}")
        return jsonify({'error': 'Transaction verification failed', 'verified': False}), 500
"""

# 5. Update PingPub Gateway initialization
"""
class PingPubGateway:
    '''Gateway for interacting with the Odiseo blockchain via ping.pub'''
    
    def __init__(self):
        # Require environment variables without fallbacks
        self.base_url = os.environ.get("PINGPUB_API_URL")
        if not self.base_url:
            raise ValueError("PINGPUB_API_URL environment variable is required")
            
        self.chain_id = os.environ.get("CHAIN_ID")
        if not self.chain_id:
            raise ValueError("CHAIN_ID environment variable is required")
            
        # Additional security: validate URLs
        if not self.base_url.startswith(('https://', 'http://localhost')):
            raise ValueError("PINGPUB_API_URL must use HTTPS (except for localhost)")
            
        # Set endpoints
        self.broadcast_endpoint = "broadcast"
        self.account_endpoint = "account"
        self.validators_endpoint = "validators"
        
        # Default gas settings (could also come from environment)
        self.default_gas = os.environ.get("DEFAULT_GAS", "100000")
        self.default_fee = os.environ.get("DEFAULT_FEE", "2500")
        self.default_denom = os.environ.get("DEFAULT_DENOM", "uodis")
        
        # Initialize session with proper timeouts
        self.session = requests.Session()
        self.session.timeout = (5, 30)  # Connect timeout, Read timeout
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Daodiseo-RWA-Client/1.0"
        })
        
        logger.info(f"PingPub Gateway initialized for chain: {self.chain_id}")
"""

# 6. Update frontend wallet storage
"""
// Secure wallet connection - replace localStorage with sessionStorage
class KeplerWallet {
    constructor() {
        this.chainId = 'odiseotestnet_1234-1';
        this.connected = false;
        this.address = null;

        // Try to restore from session storage only (not localStorage)
        const savedAddress = sessionStorage.getItem('kepler_address');
        if (savedAddress) {
            this.address = savedAddress;
            this.connected = true;
            this.updateUI();
        }
    }
    
    // ... other methods ...
    
    disconnect() {
        this.connected = false;
        this.address = null;
        
        // Clear session storage only
        sessionStorage.removeItem('kepler_address');
        sessionStorage.removeItem('walletConnected');
        
        this.updateUI();
    }
}
"""