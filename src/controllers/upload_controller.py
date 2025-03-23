from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import logging

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
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'file_path': file_path
            })
        except Exception as e:
            current_app.logger.error(f"Error saving file: {str(e)}")
            return jsonify({'error': f'Error saving file: {str(e)}'}), 500

    except Exception as e:
        current_app.logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload error: {str(e)}'}), 500