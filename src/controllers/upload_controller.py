from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import logging
import hashlib
import json
from src.gateways.multisig_gateway import MultiSigBlockchainGateway

upload_bp = Blueprint('upload', __name__, url_prefix='/api')
blockchain = MultiSigBlockchainGateway(test_mode=True)

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
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not file or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed types: .ifc, .dwg'}), 400

        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            current_app.logger.info(f"File uploaded successfully: {file_path}")

            # Get budget splits from form data
            budget_splits = {}
            roles = request.form.getlist('roles[]')
            percentages = request.form.getlist('percentages[]')

            if len(roles) != len(percentages):
                return jsonify({'error': 'Invalid budget split data'}), 400

            for role, percentage in zip(roles, percentages):
                try:
                    budget_splits[role] = float(percentage)
                except ValueError:
                    return jsonify({'error': 'Invalid percentage value'}), 400

            # Create content hash from file path and budget splits
            content = {
                'file_path': file_path,
                'budget_splits': budget_splits
            }
            content_hash = hashlib.sha256(json.dumps(content).encode()).hexdigest()

            try:
                # Initialize blockchain transaction
                current_app.logger.info("Creating blockchain transaction...")
                transaction_id = blockchain.create_transaction(
                    content_hash=content_hash,
                    metadata=content
                )

                # Get full transaction details
                transaction = blockchain.get_transaction_status(transaction_id)

                return jsonify({
                    'success': True,
                    'message': 'File uploaded and contract created successfully',
                    'transaction': transaction
                })

            except Exception as e:
                current_app.logger.error(f"Error creating blockchain transaction: {str(e)}")
                return jsonify({
                    'success': True,
                    'message': 'File uploaded but blockchain transaction failed',
                    'file_path': file_path,
                    'warning': str(e)
                })

        except Exception as e:
            current_app.logger.error(f"Error saving file: {str(e)}")
            return jsonify({'error': f'Error saving file: {str(e)}'}), 500

    except Exception as e:
        current_app.logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload error: {str(e)}'}), 500