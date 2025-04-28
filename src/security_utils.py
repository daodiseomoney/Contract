"""
Security Utilities for Daodiseo Platform
Centralized module for security-related functionality
"""

import os
import sys
import logging
import hashlib
import secrets
import time
import json
from functools import wraps
from flask import request, jsonify, session, abort, current_app

# Set up logging
logger = logging.getLogger(__name__)

# Required environment variables for blockchain operations
REQUIRED_ENV_VARS = [
    "PINGPUB_API_URL", 
    "CHAIN_ID", 
    "CONTRACT_ADDRESS", 
    "VALIDATOR_POOL_ADDRESS",
    "SESSION_SECRET"
]

def validate_environment():
    """
    Validate that all required environment variables are set
    Exits application if critical variables are missing
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
    if chain_id and "testnet" in chain_id.lower():
        logger.warning("WARNING: Application is using TESTNET configuration!")
        
    # Check for development secret key
    secret_key = os.environ.get("SESSION_SECRET")
    if secret_key and (secret_key == "dev-secret-key" or len(secret_key) < 32):
        logger.warning("WARNING: Using weak development secret key!")
        
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