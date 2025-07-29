from flask_app import app
from flask import render_template, request, redirect, url_for, flash, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from flask_app.models.equipment import Equipment
from flask_app.models.component import Components
from flask_app.models.project import Projects
from flask_app.models.method import Methods
from flask_app.models.repairs import Repairs
from flask_app.models.user_projects import  User_Projects
from flask_app.models.component_method import Component_Methods
from datetime import datetime

@app.route('/add_components/<int:project_id>/<int:equipment_id>', methods=['GET', 'POST'])
def add_components(project_id, equipment_id):
    if request.method == 'POST':
        component_names = request.form.getlist('components')
        
        for name in component_names:
            data = {
                'equipment_id': equipment_id,
                'project_id': project_id,
                'name': name
            }
            Components.add_component(data)

        return redirect(url_for('add_methods', project_id=project_id, equipment_id=equipment_id))

    components_list = ["External", "Shell", "Nozzles", "Shell Cover", "Bonnet","Inlet Channel", "Outlet Channel", "Channel", "Inlet Channel Cover", "Outlet Channel Cover", "Channel Cover", "Bundle", "Floating Head/Split Rings", "Header Boxes", "Tube Sheets", "Tubesheets", "Tubes", "Heads", "Primary Cyclones", "Secondary Cyclones", "Airgrid", "Internal Components", "Refractory", "Radiant Mechanical", "Radiant Refractory", "Convection Mechanical", "Convection Refractory", "Stack", "Closure", "Hydro", "Report"]
    equipment_info = Equipment.get_equipment_by_id(equipment_id)[0]  
    return render_template('components/add_components.html', project_id=project_id, equipment_id=equipment_id, components_list=components_list, equipment_info = equipment_info)


@app.route('/manage_components/<int:project_id>/<int:equipment_id>', methods=['GET', 'POST'])
def manage_components(project_id, equipment_id):
    if request.method == 'POST':
        component_names = request.form.getlist('components[]')
        custom_component_names = request.form.getlist('custom_components[]')

        for i, name in enumerate(component_names):
            if name == 'other':
                name = custom_component_names[i]
            data = {
                'equipment_id': equipment_id,
                'project_id': project_id,
                'name': name
            }
            Components.add_component(data)

        flash('Components added successfully')
        return redirect(url_for('add_methods', project_id=project_id, equipment_id=equipment_id))
        

    components = Components.get_components_by_equipment_id(equipment_id)
    equipment = Equipment.get_equipment_by_id(equipment_id)[0]  # Assuming the query returns a list
    predetermined_components = ["External", "Shell", "Nozzles", "Shell Cover", "Bonnet","Inlet Channel", "Outlet Channel", "Channel", "Inlet Channel Cover", "Outlet Channel Cover", "Channel Cover", "Bundle", "Floating Head/Split Rings", "Header Boxes", "Tube Sheets", "Tubesheets", "Tubes", "Heads", "Primary Cyclones", "Secondary Cyclones", "Airgrid", "Internal Components", "Refractory", "Radiant Mechanical", "Radiant Refractory", "Convection Mechanical", "Convection Refractory", "Stack", "Closure", "Hydro", "Report"]  # List of predetermined components
    return render_template('components/manage_components.html', components=components, project_id=project_id, equipment_id=equipment_id, predetermined_components=predetermined_components, equipment=equipment)

# Initial page load route
@app.route('/wallchart/<int:project_id>')
def wallchart(project_id):
    project = Projects.get_project_by_id(project_id)
    equipment_types = Equipment.get_distinct_equipment_types(project_id)
    equipment_data = Equipment.get_equipment_by_project(project_id)
    components_by_equipment = {e.id: Components.get_components_by_equipment_id(e.id) for e in equipment_data}
    return render_template('wallchart/wallchart.html', equipment_types=equipment_types, equipment_data=equipment_data, project=project, components_by_equipment=components_by_equipment)


@app.route('/view_wallchart/<int:project_id>')
def view_wallchart(project_id):
    equipment_type = request.args.get('equipment_type', 'all')
    equipment_data = Equipment.get_equipment_by_project(project_id)
    users = User_Projects.view_all_users_per_project(project_id)
    current_user = session['user_id']
    current_date = datetime.now().strftime('%Y-%m-%d')

    if equipment_type and equipment_type != 'all':
        equipment_data = [equipment for equipment in equipment_data if equipment.type == equipment_type]

    project = Projects.get_project_by_id(project_id)

    components_by_equipment = {}
    all_component_names = ["External", "Shell", "Nozzles", "Shell Cover", "Bonnet","Inlet Channel", "Outlet Channel", "Channel", "Inlet Channel Cover", "Outlet Channel Cover", "Channel Cover", "Bundle", "Floating Head/Split Rings", "Header Boxes", "Tube Sheets", "Tubesheets", "Tubes", "Heads", "Primary Cyclones", "Secondary Cyclones", "Airgrid", "Internal Components", "Refractory", "Radiant Mechanical", "Radiant Refractory", "Convection Mechanical", "Convection Refractory", "Stack", "Closure", "Hydro", "Report"]

    for equipment in equipment_data:
        components = Components.get_components_by_equipment_id(equipment.id)
        component_dict = {component.name: component for component in components}
        components_by_equipment[equipment.id] = component_dict

        # Identify custom components and insert them before "Closure"
        closure_index = all_component_names.index("Closure")
        for component in components:
            if component.name not in all_component_names:
                all_component_names.insert(closure_index, component.name)
                closure_index += 1  # Adjust the index as we insert new components

            component_methods = Component_Methods.get_methods_by_component_id(component.id)
            
            for method in component_methods:
                # Fetch all repairs for the specific method of the component
                repair_info = Repairs.get_by_component_method_and_equipment(component.id, method['id'], equipment.id)
                method['repairs'] = repair_info

                if method['updated_at']:
                    method['updated_at'] = datetime.strptime(method['updated_at'], '%Y-%m-%d %H:%M:%S') if isinstance(method['updated_at'], str) else method['updated_at']

            component.methods = [{'id': method['id'], 'method_type': method['method_type'], 'status': method['status'], 'updated_by': method.get('updated_by', ''), 'updated_at': method.get('updated_at', None), 'created_at': method['created_at'], 'repairs': method.get('repairs', [])} for method in component_methods]
    
    equipment_types = Equipment.get_distinct_equipment_types(project_id)
    
    return render_template('wallchart/equipment_table.html', 
                            project=project, 
                            equipment_data=equipment_data, 
                            components_by_equipment=components_by_equipment, 
                            all_component_names=all_component_names,
                            equipment_types=equipment_types, 
                            users=users, current_user=current_user, current_date=current_date)


@app.route('/add_method_to_components/<int:project_id>', methods=['GET', 'POST'])
def add_method_to_components(project_id):
    if request.method == 'POST':
        component_ids = request.form.getlist('component_ids')
        method_name = request.form['method_name']
        
        # Get or create the method
        method_id = Methods.get_or_create_method(method_name)
        
        # Add the method to each selected component
        for component_id in component_ids:
            data = {
                'component_id': component_id,
                'method_id': method_id
            }
            Component_Methods.add_method_to_component(data)
        
        flash('Method added to selected components successfully')
        return redirect(url_for('view_wallchart', project_id=project_id))
    
    # Fetch necessary data for the form
    equipment_data = Equipment.get_equipment_by_project(project_id)
    components = Components.get_all_components_by_project(project_id)  # Define this method to fetch components

    return render_template('add_method_to_component.html', equipment_data=equipment_data, components=components, project_id=project_id)

@app.route('/update_method_status/<int:component_id>/<int:method_id>', methods=['GET', 'POST'])
def update_method_status(component_id, method_id):
    component = Components.get_component_by_id(component_id)
    method = Methods.get_method_by_id(method_id)
    if request.method == 'POST':
        status = request.form['status']
        updated_at = request.form['updated_at']
        data = {
            'status': status,
            'component_id': component_id,
            'method_id': method_id,
            'updated_at': updated_at
        }
        Component_Methods.update_method_status(data)
        flash('Method status updated successfully')
        return redirect(url_for('view_wallchart', project_id=component.project_id))
    return render_template('update_method_status.html', component=component, method=method)

@app.route('/project/components/<int:project_id>')
def get_components(project_id):
    components_data = Components.get_all_components_by_project(project_id)
    components = []
    for component in components_data:
        component_id = component.get('id')
        component_name = component.get('name')
        # Assuming you have a method to fetch the equipment number based on the component
        equipment_number = Equipment.get_equipment_number_by_component_id(component_id)  
        component_methods = Component_Methods.get_methods_by_component_id(component_id)
        for method in component_methods:
            components.append({
                'name': component_name,
                'status': method['status'],
                'equipment_number': equipment_number
            })
    return jsonify(components)

@app.route('/component/edit_component/<int:component_id>', methods=['GET', 'POST'])
def edit_component(component_id):
    component = Components.get_component_by_id(component_id)
    if request.method == 'POST':
        name = request.form['name']
        data = {
            'id': component_id,
            'name': name,
        }
        Components.edit_component(data)
        flash('Component updated successfully')
        return redirect(url_for('manage_components', project_id=component.project_id, equipment_id=component.equipment_id))
    
    return render_template('components/edit_component.html', component=component)


@app.route('/component/delete_component/<int:component_id>', methods=['POST'])
def delete_component(component_id):
    component = Components.get_component_by_id(component_id)
    Components.delete_component(component_id)
    flash('Component deleted successfully')
    return redirect(url_for('manage_components', project_id=component.project_id, equipment_id=component.equipment_id))
