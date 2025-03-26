from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import logging
import hashlib
import json
import requests
from src.gateways.storage_factory import StorageFactory

upload_bp = Blueprint('upload', __name__, url_prefix='/api')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'ifc', 'dwg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload with proper error handling and JSON responses"""
    try:
        current_app.logger.debug("Received file upload request")

        if 'file' not in request.files:
            current_app.logger.error("No file part in request")
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            current_app.logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400

        if not file or not allowed_file(file.filename):
            current_app.logger.error(f"Invalid file type. Allowed types: {ALLOWED_EXTENSIONS}")
            return jsonify({'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

        try:
            # Create appropriate storage gateway based on configuration
            storage_gateway = StorageFactory.create_storage_gateway()
            
            # Store the file using the selected gateway
            try:
                file_path = storage_gateway.store_file(file)
                current_app.logger.info(f"File uploaded successfully: {file_path}")
            except Exception as e:
                current_app.logger.error(f"Error storing file: {str(e)}", exc_info=True)
                return jsonify({'error': f'Error storing file: {str(e)}'}), 500

            # Get budget splits from form data
            budget_splits = {}
            roles = request.form.getlist('roles[]')
            percentages = request.form.getlist('percentages[]')

            current_app.logger.debug(f"Received roles: {roles}")
            current_app.logger.debug(f"Received percentages: {percentages}")

            if len(roles) != len(percentages):
                current_app.logger.error("Invalid budget split data: mismatched roles and percentages")
                return jsonify({'error': 'Invalid budget split data'}), 400

            try:
                for role, percentage in zip(roles, percentages):
                    budget_splits[role] = float(percentage)

                total = sum(budget_splits.values())
                if abs(total - 100) > 0.01:  # Allow for small floating point differences
                    current_app.logger.error(f"Budget splits total {total}% instead of 100%")
                    return jsonify({'error': 'Budget splits must total 100%'}), 400

            except ValueError as e:
                current_app.logger.error(f"Invalid percentage value: {str(e)}")
                return jsonify({'error': 'Invalid percentage values'}), 400

            # Prepare data for tokenization
            tokenize_data = {
                'file_path': file_path,
                'budget_splits': budget_splits,
                'storage_type': 'bimserver' if current_app.config.get('BIMSERVER_ENABLED', False) else 'local'
            }

            current_app.logger.debug(f"Sending tokenization request: {tokenize_data}")

            # Call tokenize endpoint
            try:
                response = requests.post(
                    'http://localhost:5000/api/tokenize',
                    json=tokenize_data,
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 200:
                    current_app.logger.info("Tokenization successful")
                    return jsonify(response.json())
                else:
                    error_msg = response.json().get('error', 'Unknown error during tokenization')
                    current_app.logger.error(f"Tokenization failed: {error_msg}")
                    return jsonify({
                        'success': True,
                        'message': 'File uploaded but tokenization failed',
                        'file_path': file_path,
                        'error': error_msg
                    }), response.status_code

            except requests.exceptions.RequestException as e:
                current_app.logger.error(f"Error calling tokenize endpoint: {str(e)}", exc_info=True)
                return jsonify({
                    'success': True,
                    'message': 'File uploaded but tokenization failed',
                    'file_path': file_path,
                    'error': str(e)
                }), 500

        except Exception as e:
            current_app.logger.error(f"Error processing upload: {str(e)}", exc_info=True)
            return jsonify({'error': f'Error processing upload: {str(e)}'}), 500

    except Exception as e:
        current_app.logger.error(f"Upload error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500