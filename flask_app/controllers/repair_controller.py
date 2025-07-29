from flask import session, request, render_template, redirect, flash, jsonify, url_for, send_from_directory
from flask_app import app
from flask_app.models.project import Projects
from flask_app.models.component import Components
from flask_app.models.equipment import Equipment
from flask_app.models.repairs import Repairs
from flask_app.models.component_method import Component_Methods
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
        
def fetch_repair_info(component_id, equipment_id):
    repair_info = Repairs.get_by_component_and_equipment(component_id, equipment_id)
    if repair_info:
        return [{
            'id': repair['id'],
            'repair_number': repair.get('repair_number'),
            'description': repair.get('description'),
            'repair_status': repair.get('repair_status'),
            'file_path': repair.get('file_path')
        } for repair in repair_info]
    return []

@app.route('/get_repair_details', methods=['GET'])
def get_repair_details():
    repair_id = request.args.get('repair_id')
    component_id = request.args.get('component_id')
    equipment_id = request.args.get('equipment_id')

    # Logging the received parameters
    print(f"Received parameters: repair_id={repair_id}, component_id={component_id}, equipment_id={equipment_id}")

    if repair_id:
        repair_info = Repairs.get_repair_by_id(repair_id)
        if repair_info:
            return jsonify({
                'id': repair_info['id'],
                'repair_number': repair_info.get('repair_number'),
                'description': repair_info.get('description'),
                'repair_status': repair_info.get('repair_status'),
                'file_path': repair_info.get('file_path')
            })
        else:
            return jsonify({'error': 'Repair not found for the given repair_id'}), 404

    if component_id and equipment_id:
        repair_info = Repairs.get_by_component_and_equipment(component_id, equipment_id)
        if repair_info:
            repair_details = [{
                'id': repair['id'],
                'repair_number': repair.get('repair_number'),
                'description': repair.get('description'),
                'repair_status': repair.get('repair_status'),
                'file_path': repair.get('file_path')
            } for repair in repair_info]
            return jsonify(repair_details)
        else:
            return jsonify({'error': 'No repairs found for the given component_id and equipment_id'}), 404

    return jsonify({'error': 'Invalid request parameters'}), 400




@app.route('/get_repair_info_by_component/<int:component_id>/<int:equipment_id>', methods=['GET'])
def get_repair_info_by_component(component_id, equipment_id):
    component = Components.get_component_by_id(component_id)
    equipment = Equipment.get_equipment_by_id(equipment_id)
    repair_details = fetch_repair_info(component_id, equipment_id)
    return render_template('repairs/view_repair.html', repair_info=repair_details, component=component, equipment=equipment)


@app.route('/repairs/view_all_repairs/<int:project_id>', methods=['GET'])
def get_all_repairs_per_project(project_id):
    repairs = Repairs.get_repairs_by_project(project_id)
    updated_methods = Component_Methods.get_methods_by_project_id(project_id)
    
    # Combining repairs with updated methods
    for repair in repairs:
        for method in updated_methods:
            if repair['component_id'] == method['component_id']:
                repair['updated_by'] = method['updated_by']
                break
    
    return render_template('repairs/view_all_repairs_per_project.html', repairs=repairs, project_id=project_id)

@app.route('/repairs/update_repair_status/<int:repair_id>', methods=['GET', 'POST'])
def update_repair_status(repair_id):
    repair = Repairs.get_repair_by_id(repair_id)
    if request.method == 'POST':
        new_status = request.form.get('status')
        update_data = {
            "id": repair_id,
            "repair_status": new_status
        }
        Repairs.update_repair_status(update_data)

        # Check if all repairs for the component are complete, rejected, or deferred
        component_id = repair['component_id']
        method_id = repair['method_id']
        Component_Methods.update_method_status_if_all_repairs_complete(component_id, method_id)

        flash('Repair status updated successfully', 'success')
        return redirect(url_for('wallchart', project_id=repair['project_id']))
    
    return render_template('repairs/update_repair.html', repair=repair)















