from flask_app import app
from flask import render_template, request, redirect, url_for, flash, send_from_directory, session, jsonify, json
from werkzeug.utils import secure_filename
from flask_app.models.project import Projects
from flask_app.models.equipment import Equipment
from flask_app.models.component import Components
from flask_app.models.method import Methods
from flask_app.models.component_method import Component_Methods
import os
import pandas as pd

@app.route('/edit_methods_all/<int:project_id>', methods=['GET', 'POST'])
def edit_methods_all(project_id):
    equipment_list = Equipment.get_equipment_by_project(project_id)
    components_by_equipment = {equipment.number: Components.get_components_by_equipment_number(equipment.number) for equipment in equipment_list}
    methods = ["VT", "UTT", "PT", "MT", "RT", "PAUT", "UT", "ECT", "RFT", "IRIS", "Ok to Install Bundle", "Shell Side", "Tube Side" "Ok to Close", "Complete"]  # Hardcoded methods

    if request.method == "POST":
        for equipment_number, components in components_by_equipment.items():
            for component in components:
                selected_methods = request.form.getlist(f'methods_{component.id}')
                for method_type in selected_methods:
                    Methods.add_or_update_method(component.id, method_type, "Pending")

        return redirect(f"/view_equipment_per_project/{project_id}")

    return render_template('components/edit_methods_all.html', equipment_list=equipment_list, components_by_equipment=components_by_equipment, methods=methods)

@app.route('/add_methods/<int:project_id>/<int:equipment_id>', methods=['GET', 'POST'])
def add_methods(project_id, equipment_id):
    equipment = Equipment.get_equipment_by_id(equipment_id)[0]  # Ensure it's a single object
    components = Components.get_components_by_equipment_id(equipment_id)

    if request.method == "POST":
        for component in components:
            new_methods = request.form.get(f'method_type_{component.id}')
            if new_methods:
                methods_list = [method.strip() for method in new_methods.split(',')]
                for new_method in methods_list:
                    method = Methods.get_method_by_name(new_method)
                    if not method:
                        method_id = Methods.add_method(new_method)
                    else:
                        method_id = method['id'] if 'id' in method else method.get('id')

                    if method_id:
                        Component_Methods.add_or_update_method(component.id, method_id, "Pending")
        return redirect(f"/wallchart/{project_id}")

    # Fetch existing methods for each component
    components_methods = {}
    for component in components:
        component_methods = Component_Methods.get_methods_by_component_id(component.id)
        components_methods[component.id] = [method['method_type'] for method in component_methods]

    return render_template('components/add_methods.html', project_id=project_id, equipment=equipment, components=components, components_methods=components_methods)

@app.route('/methods/edit_methods/<int:project_id>/<int:component_id>', methods=['GET', 'POST'])
def edit_methods(project_id, component_id):
    component = Components.get_component_by_id(component_id)
    current_methods = Component_Methods.get_methods_by_component_id(component_id)
    available_methods = ["VT", "UTT", "PT", "MT", "RT", "PAUT", "UT", "ECT", "RFT", "IRIS", "Ok to Install Bundle", "Shell Side", "Tube Side", "Ok to Close", "Complete"]  # List all available methods

    if request.method == 'POST':
        selected_methods = request.form.getlist('methods')
        Component_Methods.update_methods_for_component(component_id, selected_methods)
        flash('Methods updated successfully')
        return redirect(url_for('wallchart', project_id=project_id))

    return render_template('methods/edit_methods.html', component=component, current_methods=current_methods, available_methods=available_methods, project_id=project_id)

@app.route('/methods/delete_method/<int:project_id>/<int:component_id>/<int:method_id>', methods=['POST'])
def delete_method(project_id, component_id, method_id):
    Component_Methods.delete_method_from_component(component_id, method_id)
    flash('Method deleted successfully')
    return redirect(url_for('edit_methods', project_id=project_id, component_id=component_id))

@app.route('/methods/update_methods/<int:project_id>/<int:component_id>', methods=['POST'])
def update_methods(project_id, component_id):
    for key, value in request.form.items():
        if key.startswith('status_'):
            method_id = key.split('_')[1]
            status = value
            Component_Methods.update_method_status(component_id, method_id, status)
    flash('Methods updated successfully')
    return redirect(url_for('edit_methods', project_id=project_id, component_id=component_id))

@app.route('/update_method_status', methods=['POST'])
def update_component_method_status():
    component_id = request.form.get('component_id')
    method_id = request.form.get('method_id')
    status = request.form.get('status')
    description = request.form.get('description')
    repair_number = request.form.get('new_repair_number')
    file = request.files.get('file')
    current_tab = request.form.get('currentTab')

    # Log received data for debugging
    print(f"Received data - Component ID: {component_id}, Method ID: {method_id}, Status: {status}, Description: {description}, Current Tab: {current_tab}, Repair Number: {repair_number}")

    # Save the file if provided
    file_path = None
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

    # Get the equipment_id based on the component_id if needed
    component = Components.get_component_by_id(component_id)
    equipment_id = component.equipment_id if component else None

    # Update the method status and repair information in the database
    repair_data = {
        'component_id': component_id,
        'method_id': method_id,
        'status': status,
        'description': description,
        'repair_number': repair_number,
        'file_path': file_path,
        'equipment_id': equipment_id  # Ensure this is included
    }
    Component_Methods.update_method_status(repair_data)

    return jsonify({'currentTab': current_tab})


@app.route('/get_component_status', methods=['POST'])
def get_component_status():
    component_ids = request.json.get('component_ids', [])
    all_methods = {}

    for component_id in component_ids:
        component_methods = Component_Methods.get_methods_by_component_id(component_id)
        methods = [{'id': method['id'], 'status': method['status'], 'method_type': method['method_type']} for method in component_methods]
        all_methods[component_id] = methods

    return jsonify(all_methods)
