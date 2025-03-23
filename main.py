import os
from flask import Flask, render_template
from src.controllers.upload_controller import upload_bp
from src.controllers.contract_controller import contract_bp
from src.controllers.account_controller import account_bp
from src.controllers.transaction_controller import transaction_bp
from src.external_interfaces.config import Config

app = Flask(__name__, 
    template_folder='src/external_interfaces/ui/templates',
    static_folder='src/external_interfaces/ui/static'
)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(upload_bp)
app.register_blueprint(contract_bp)
app.register_blueprint(account_bp)
app.register_blueprint(transaction_bp)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/contracts')
def contracts():
    return render_template('contracts.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)