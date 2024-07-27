from flask_app import app
from flask import render_template, request, redirect, url_for, flash, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from flask_app.models.project import Projects
from flask_app.models.equipment import Equipment
from flask_app.models.component import Components
from flask_app.models.method import Methods
from flask_app.models.user import User
from flask_app.models.component_method import Component_Methods
import pandas as pd
import os

@app.route('/upload_all/<int:project_id>', methods=['GET', 'POST'])
def upload_all(project_id):
    user_id = session.get('user_id')
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Read equipment, components, and methods tabs from the Excel file
            with pd.ExcelFile(file_path) as xls:
                equipment_df = pd.read_excel(xls, 'equipment', dtype={'number': str})
                components_df = pd.read_excel(xls, 'components', dtype={'equipment_number': str})
                methods_df = pd.read_excel(xls, 'methods', dtype={'equipment_number': str})

            # Add equipment to the database
            Equipment.add_equipment_by_file(equipment_df, project_id, user_id)

            # Add components to the database
            Components.add_components_by_file(components_df, project_id)

            # Add methods to the database
            for index, row in methods_df.iterrows():
                number = row['number']
                methods_str = row['name']
                methods_list = methods_str.split(';')  # Split by semicolon

                equipment = Equipment.get_equipment_by_number(number)
                if equipment:
                    equipment_id = equipment[0]['id']
                    for method_entry in methods_list:
                        method_entry = method_entry.strip()
                        if method_entry:
                            name, methods_str = method_entry.split(',', 1)
                            name = name.strip()
                            methods = [method.strip() for method in methods_str.split(',')]

                            # Check if the component exists, if not create it
                            component = Components.get_component_by_name_and_equipment_id(name, equipment_id)
                            if not component:
                                data = {
                                    "equipment_id": equipment_id,
                                    "project_id": project_id,
                                    "name": name
                                }
                                component_id = Components.add_component(data)
                            else:
                                component_id = component.id

                            # Add or update methods for the component
                            for method_type in methods:
                                method = Methods.get_method_by_name(method_type)
                                if not method:
                                    method_id = Methods.add_method(method_type)
                                else:
                                    method_id = method['id']
                                Component_Methods.add_or_update_method(component_id, method_id, "Pending")

            flash('File successfully uploaded and data inserted into the database')
            return redirect(f'/view_equipment_per_project/{project_id}')
    
    equipment = Equipment.get_equipment_by_id(project_id)
    return render_template('equipment/add_equipment.html', project_id=project_id, equipment=equipment)


@app.route('/add_single_equipment/<int:project_id>', methods=['GET', 'POST'])
def add_single_equipment(project_id):
    if request.method == 'POST':
        data = {
            'project_id': project_id,
            'name': request.form['name'],
            'type': request.form['type'],
            'number': request.form['number'],
            'scope': request.form['scope'],
            'user_id': session.get('user_id')
        }
        equipment_id = Equipment.add_single_equipment(data)
        return redirect(url_for('manage_components', project_id=project_id, equipment_id=equipment_id))
    return render_template('equipment/add_single_equipment.html', project_id=project_id)

@app.route('/view_equipment_per_project/<int:project_id>')
def view_equipment_by_project(project_id):
    equipment_data = Equipment.get_equipment_by_project(project_id)
    project = Projects.get_project_by_id(project_id)
    user = session.get('user_id') 
    user_role = User.get_user_by_id(user)
    
    return render_template('equipment/all_equipment_per_project.html', equipment_data=equipment_data, project=project, user_role = user_role)

@app.route('/view_equipment_by_type/<int:project_id>', methods=['GET'])
def view_equipment_by_type(project_id):
    equipment_type = request.args.get('equipment_type')
    equipment_data = Equipment.get_equipment_by_type(project_id, equipment_type)
    return render_template('equipment/equipment_by_type.html', equipment_data=equipment_data)


@app.route('/edit_equipment/<int:project_id>/<int:equipment_id>', methods=['GET', 'POST'])
def edit_equipment(project_id, equipment_id):
    equipment = Equipment.get_equipment_by_id(equipment_id)
    project = Projects.get_project_by_id(project_id)
    components = Components.get_components_by_equipment_id(equipment_id)
    user = session.get('user_id')
    user_role = User.get_user_by_id(user)

    # Fetch and associate methods with each component
    for component in components:
        component.methods = Component_Methods.get_methods_by_component_id(component.id)
    
    if request.method == "POST":
        data = {
            "id": equipment_id,
            "name": request.form["name"],
            "number": request.form['number'],
            "scope": request.form["scope"],
            "type": request.form["type"],
            "user_id": session.get('user_id')
        }
        Equipment.edit_equipment(data)  
        return redirect(f"/view_equipment_per_project/{project_id}")
    
    return render_template('equipment/edit_equipment.html', equipment=equipment, project=project, components=components, user_role = user_role)



@app.route('/delete_equipment/<int:project_id>/<int:equipment_id>', methods=['GET', 'POST'])
def remove_equipment(project_id, equipment_id):
    # Retrieve equipment details before deletion
    equipment = Equipment.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash(f'Equipment with ID {equipment_id} not found', 'danger')
        return redirect(f"/view_equipment_per_project/{project_id}")
    
    equipment_number = equipment[0]['number']  # Assuming `equipment` is a list with one dictionary
    equipment_name = equipment[0]['name']
    
    if Equipment.delete_equipment(equipment_id):
        flash(f'Equipment "{equipment_number} - {equipment_name}" deleted successfully', 'success')
    else:
        flash(f'Failed to delete equipment "{equipment_number} - {equipment_name}"', 'danger')
    
    return redirect(f"/view_equipment_per_project/{project_id}")

    



