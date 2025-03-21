from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from src.gateways.storage_gateway import LocalStorageGateway
from src.gateways.llm_gateway import SimpleLLMGateway

upload_bp = Blueprint('upload', __name__)
storage = LocalStorageGateway()
llm = SimpleLLMGateway()

ALLOWED_EXTENSIONS = {'ifc', 'dwg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
async def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            file_path = storage.store_file(file)

            # Analyze file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            analysis = await llm.analyze_bim_file(file_content)

            return jsonify({
                'message': 'File uploaded successfully',
                'file_path': file_path,
                'analysis': analysis
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400