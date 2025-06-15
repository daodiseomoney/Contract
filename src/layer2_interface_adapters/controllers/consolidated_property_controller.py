"""
Consolidated Property Controller for DAODISEO Platform
Combines BIM, IFC, upload, and property analysis functionality
"""

import os
import json
import logging
from typing import Dict, List
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from openai import OpenAI

from src.layer4_external_interfaces.web.services.ai.bim_agent import BIMAgentManager
from src.layer4_external_interfaces.web.services.ai.ai_agent_service import AIAgentService
from src.layer3_interface_adapters.gateways.ifc.ifc_gateway import IFCGateway
from src.layer4_external_interfaces.config import Config
from src.security_utils import secure_endpoint

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
property_bp = Blueprint("property", __name__, url_prefix="/api/property")

# Initialize services
bim_agent_manager = BIMAgentManager()
ai_service = AIAgentService()

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# =============================================================================
# FILE UPLOAD MANAGEMENT
# =============================================================================

def allowed_file(filename):
    """Check if uploaded file has an allowed extension"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )

@property_bp.route("/upload", methods=["POST"])
@secure_endpoint
def upload_file():
    """Handle file upload requests"""
    if "file" not in request.files:
        logger.debug("No file part in the request")
        return jsonify({"success": False, "message": "No file part in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        logger.debug("No selected file")
        return jsonify({"success": False, "message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)

        logger.debug(f"File uploaded successfully: {filename}")
        
        # If it's an IFC file, try to load it with the BIM Agent
        if filename.lower().endswith('.ifc'):
            try:
                load_result = bim_agent_manager.load_ifc_file(file_path)
                
                return jsonify({
                    "success": True,
                    "message": "IFC file uploaded and loaded successfully",
                    "filename": filename,
                    "path": file_path,
                    "ifc_loaded": load_result.get("success", False),
                    "ifc_message": load_result.get("message", ""),
                    "building_data": load_result.get("building_data", {})
                })
                
            except Exception as e:
                logger.error(f"Error loading IFC file after upload: {str(e)}")
                return jsonify({
                    "success": True,
                    "message": "File uploaded but IFC loading failed",
                    "filename": filename,
                    "path": file_path,
                    "error": str(e)
                })
        
        # Standard response for non-IFC files
        return jsonify({
            "success": True,
            "message": "File uploaded successfully",
            "filename": filename,
            "path": file_path,
        })

    logger.debug("File type not allowed")
    return jsonify({"success": False, "message": "File type not allowed"}), 400

@property_bp.route("/ifc/reload", methods=["POST"])
@secure_endpoint
def reload_ifc_file():
    """Force reload of an IFC file"""
    try:
        data = request.json
        file_path = data.get("file_path")
        
        if not file_path:
            return jsonify({"success": False, "message": "No file path provided"}), 400
        
        if not os.path.exists(file_path):
            return jsonify({"success": False, "message": "File not found"}), 404
        
        # Reload the IFC file
        result = bim_agent_manager.load_ifc_file(file_path)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error reloading IFC file: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# =============================================================================
# BIM MODEL MANAGEMENT
# =============================================================================

@property_bp.route("/bim/load", methods=["POST"])
@secure_endpoint
def load_bim_file():
    """Load a BIM file for analysis"""
    try:
        data = request.json
        file_path = data.get("file_path")
        
        if not file_path:
            return jsonify({
                "success": False,
                "message": "No file path provided"
            }), 400
            
        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "message": f"File not found: {file_path}"
            }), 404
            
        result = bim_agent_manager.load_ifc_file(file_path)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error loading BIM file: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@property_bp.route("/bim/building-data", methods=["GET"])
@secure_endpoint
def get_building_data():
    """Get building data from loaded BIM model"""
    try:
        result = bim_agent_manager.get_building_data()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting building data: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@property_bp.route("/bim/process-message", methods=["POST"])
@secure_endpoint
def process_message():
    """Process a message using the BIM agent"""
    try:
        data = request.json
        message = data.get("message")
        
        if not message:
            return jsonify({
                "success": False,
                "message": "No message provided"
            }), 400
            
        result = bim_agent_manager.process_message(message)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@property_bp.route("/bim/element/<element_id>", methods=["GET"])
@secure_endpoint
def get_element(element_id):
    """Get element details by ID"""
    try:
        result = bim_agent_manager.get_element_by_id(element_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting element {element_id}: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@property_bp.route("/bim/element-types", methods=["GET"])
@secure_endpoint
def get_element_types():
    """Get all element types in the loaded BIM model"""
    try:
        result = bim_agent_manager.get_element_types()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting element types: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@property_bp.route("/bim/elements/<element_type>", methods=["GET"])
@secure_endpoint
def get_elements_by_type(element_type):
    """Get all elements of a specific type"""
    try:
        result = bim_agent_manager.get_elements_by_type(element_type)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting elements of type {element_type}: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@property_bp.route("/bim/enhanced/toggle", methods=["POST"])
@secure_endpoint
def toggle_enhanced_mode():
    """Toggle enhanced BIM analysis mode"""
    try:
        data = request.json
        enabled = data.get("enabled", False)
        
        result = bim_agent_manager.toggle_enhanced_mode(enabled)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error toggling enhanced mode: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@property_bp.route("/bim/enhanced/status", methods=["GET"])
@secure_endpoint
def get_enhanced_status():
    """Get enhanced mode status"""
    try:
        result = bim_agent_manager.get_enhanced_status()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting enhanced status: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

# =============================================================================
# IFC FILE ANALYSIS
# =============================================================================

@property_bp.route("/ifc/summary", methods=["GET"])
@secure_endpoint
def get_ifc_summary():
    """Get a summary of an IFC file"""
    try:
        file_path = request.args.get("file")
        
        if not file_path:
            # Look for default file in uploads directory
            uploads_dir = os.path.join(os.getcwd(), "uploads")
            
            if not os.path.exists(uploads_dir):
                return jsonify({
                    "success": False,
                    "message": "Uploads directory not found"
                }), 404
            
            # Find first IFC file
            ifc_files = [
                os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir)
                if f.lower().endswith(".ifc")
            ]
            
            if not ifc_files:
                return jsonify({
                    "success": False,
                    "message": "No IFC files found in uploads directory"
                }), 404
            
            file_path = ifc_files[0]
        
        result = ai_service.get_ifc_summary(file_path)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting IFC summary: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@property_bp.route("/ifc/analyze", methods=["POST"])
@secure_endpoint
def analyze_ifc_file():
    """Analyze an IFC file with AI"""
    try:
        data = request.json
        file_path = data.get("file_path")
        
        if not file_path:
            return jsonify({
                "success": False,
                "message": "No file path provided"
            }), 400
        
        result = ai_service.analyze_ifc_file(file_path)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error analyzing IFC file: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =============================================================================
# PROPERTY INVESTMENT ANALYSIS
# =============================================================================

@property_bp.route('/analyze-property')
@secure_endpoint
def analyze_property():
    """Analyze property using AI for investment potential"""
    asset_id = request.args.get('asset_id')
    if not asset_id:
        return jsonify({'success': False, 'error': 'Asset ID required'}), 400
    
    try:
        # Property data mapping - this would typically come from a database
        property_data = {
            'prop-001': {'name': 'Downtown Office Complex - Miami', 'type': 'Commercial', 'value': '$12.5M'},
            'prop-002': {'name': 'Luxury Residential Tower - NYC', 'type': 'Residential', 'value': '$45.2M'},
            'prop-003': {'name': 'Industrial Warehouse - Dallas', 'type': 'Industrial', 'value': '$8.9M'},
            'prop-004': {'name': 'Mixed-Use Development - LA', 'type': 'Mixed-Use', 'value': '$28.7M'},
            'property-downtown-001': {'name': 'Downtown Office Complex', 'type': 'Commercial', 'value': '$2.4M'},
            'property-residential-002': {'name': 'Luxury Residential Tower', 'type': 'Residential', 'value': '$8.9M'},
            'property-industrial-003': {'name': 'Industrial Warehouse Complex', 'type': 'Industrial', 'value': '$1.2M'}
        }.get(asset_id, {'name': 'Unknown Property', 'type': 'Unknown', 'value': '$0'})
        
        # Use OpenAI for analysis
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        prompt = f"""
        Analyze the following real estate property for tokenization and investment potential:
        
        Property: {property_data['name']}
        Type: {property_data['type']}
        Value: {property_data['value']}
        
        Provide comprehensive investment analysis including:
        - Investment score (1-10)
        - ROI projection (annual percentage)  
        - Risk assessment (Low/Medium/High)
        - Liquidity analysis
        - Market positioning
        - Tokenization benefits
        - Detailed analysis report
        - Confidence score (0-1)
        
        Return as JSON with all metrics calculated.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a real estate investment analyst specializing in tokenization. Provide detailed investment analysis for properties. Always return data in JSON format with real calculations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Property analysis error: {e}")
        return jsonify({
            'success': False,
            'error': 'Property analysis service temporarily unavailable'
        }), 500

@property_bp.route('/investment-analysis', methods=['POST'])
@secure_endpoint
def investment_analysis():
    """Generate detailed investment analysis for property"""
    data = request.get_json()
    if not data or not data.get('asset_id'):
        return jsonify({'success': False, 'error': 'Asset ID required'}), 400
    
    try:
        asset_id = data['asset_id']
        wallet_address = data.get('wallet_address', '')
        
        # Get property data (this would typically come from database)
        property_data = {
            'prop-001': {
                'name': 'Downtown Office Complex - Miami',
                'type': 'Commercial',
                'value': '$12.5M',
                'location': 'Miami, FL',
                'size': '150,000 sq ft',
                'year_built': '2020'
            },
            'prop-002': {
                'name': 'Luxury Residential Tower - NYC',
                'type': 'Residential',
                'value': '$45.2M',
                'location': 'Manhattan, NY',
                'size': '200 units',
                'year_built': '2019'
            }
        }.get(asset_id, {
            'name': 'Sample Property',
            'type': 'Unknown',
            'value': '$0',
            'location': 'Unknown',
            'size': 'Unknown',
            'year_built': 'Unknown'
        })
        
        # Use OpenAI for comprehensive analysis
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        prompt = f"""
        Provide a comprehensive investment analysis for tokenization:
        
        Property Details:
        - Name: {property_data['name']}
        - Type: {property_data['type']}
        - Value: {property_data['value']}
        - Location: {property_data['location']}
        - Size: {property_data['size']}
        - Year Built: {property_data['year_built']}
        - Investor Address: {wallet_address}
        
        Generate detailed analysis including:
        1. Market Analysis (current trends, comparable sales)
        2. Financial Projections (5-year outlook, cash flow)
        3. Tokenization Strategy (token structure, liquidity options)
        4. Risk Assessment (market, regulatory, operational risks)
        5. Investment Recommendations (target allocation, exit strategy)
        6. Due Diligence Checklist
        7. Regulatory Compliance Requirements
        
        Return comprehensive JSON analysis with all calculations and recommendations.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior real estate investment analyst with expertise in blockchain tokenization. Provide institutional-grade investment analysis with detailed financial modeling and risk assessment."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        return jsonify({
            'success': True,
            'property': property_data,
            'analysis': analysis,
            'timestamp': json.dumps(os.time.time() if hasattr(os, 'time') else 0)
        })
        
    except Exception as e:
        logger.error(f"Investment analysis error: {e}")
        return jsonify({
            'success': False,
            'error': 'Investment analysis service temporarily unavailable'
        }), 500

# =============================================================================
# PROPERTY TOKENIZATION
# =============================================================================

@property_bp.route('/tokenize', methods=['POST'])
@secure_endpoint
def tokenize_property():
    """Initiate property tokenization process"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        asset_id = data.get('asset_id')
        wallet_address = data.get('wallet_address')
        token_count = data.get('token_count', 1000000)
        
        if not asset_id or not wallet_address:
            return jsonify({
                'success': False,
                'error': 'Asset ID and wallet address are required'
            }), 400
        
        # Generate tokenization proposal
        result = {
            'success': True,
            'tokenization_id': f"token-{asset_id}-{hash(wallet_address) % 10000}",
            'asset_id': asset_id,
            'wallet_address': wallet_address,
            'token_count': token_count,
            'token_symbol': f"PROP{asset_id.upper()[-3:]}",
            'status': 'pending_approval',
            'estimated_completion': '5-7 business days',
            'next_steps': [
                'Legal documentation review',
                'Property valuation verification',
                'Smart contract deployment',
                'Token distribution setup'
            ]
        }
        
        logger.info(f"Tokenization initiated for {asset_id} by {wallet_address}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in tokenize_property: {e}")
        return jsonify({
            'success': False,
            'error': 'Tokenization service temporarily unavailable'
        }), 500

# =============================================================================
# PROPERTY PORTFOLIO MANAGEMENT
# =============================================================================

@property_bp.route('/portfolio', methods=['GET'])
@secure_endpoint
def get_property_portfolio():
    """Get property portfolio for a wallet address"""
    try:
        wallet_address = request.args.get('wallet_address')
        
        if not wallet_address:
            return jsonify({'success': False, 'error': 'Wallet address required'}), 400
        
        # This would typically query the blockchain or database
        portfolio = {
            'success': True,
            'wallet_address': wallet_address,
            'total_properties': 3,
            'total_value': '$22.6M',
            'total_tokens': 2750000,
            'properties': [
                {
                    'asset_id': 'prop-001',
                    'name': 'Downtown Office Complex',
                    'token_balance': 150000,
                    'percentage_owned': '15%',
                    'current_value': '$1.875M',
                    'status': 'active'
                },
                {
                    'asset_id': 'prop-002',
                    'name': 'Luxury Residential Tower',
                    'token_balance': 100000,
                    'percentage_owned': '5%',
                    'current_value': '$2.26M',
                    'status': 'active'
                }
            ]
        }
        
        return jsonify(portfolio)
        
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return jsonify({
            'success': False,
            'error': 'Portfolio service temporarily unavailable'
        }), 500

def register_property_routes(app):
    """Register consolidated property routes with the Flask app"""
    app.register_blueprint(property_bp)
    logger.info("Consolidated property routes registered successfully")