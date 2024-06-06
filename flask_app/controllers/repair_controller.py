from flask import session, request, render_template, redirect, flash, jsonify, url_for, send_from_directory
from flask_app import app
from flask_app.models.project import Projects
from flask_app.models.component import Components
from flask_app.models.equipment import Equipment
from flask_app.models.repairs import Repairs
from werkzeug.utils import secure_filename
import os

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/repairs/upload_repair/<int:component_id>/<int:equipment_id>', methods=['GET', 'POST'])
def upload_repair(component_id, equipment_id):
    if request.method == 'POST':
        description = request.form.get('description', '')
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            data = {
                'component_id': component_id,
                'equipment_id': equipment_id,
                'description': description,
                'file_path': file_path
            }
            Repairs.add_repair(data)
            return redirect(url_for('component_methods', component_id=component_id, equipment_id=equipment_id))
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)

@app.route('/get_repair_details', methods=['GET'])
def get_repair_details():
    component_id = request.args.get('component_id')
    equipment_id = request.args.get('equipment_id')

    repair_info = Repairs.get_by_component_and_equipment(component_id, equipment_id)
    
    if repair_info:
        return jsonify({
            'repair_number': repair_info.get('repair_number'),
            'description': repair_info.get('description'),
            'file_path': repair_info.get('file_path')
        })
    else:
        return jsonify({
            'repair_number': None,
            'description': None,
            'file_path': None
        })






