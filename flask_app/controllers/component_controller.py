from flask_app import app
from flask import render_template, request, redirect, url_for, flash, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from flask_app.models.equipment import Equipment
from flask_app.models.component import Components
from flask_app.models.project import Projects
from flask_app.models.method import Methods
from flask_app.models.component_method import Component_Methods
from datetime import datetime



@app.route('/add_components/<int:project_id>/<int:equipment_id>', methods=['GET', 'POST'])
def add_components(project_id, equipment_id):
    if request.method == 'POST':
        component_names_str = request.form.get('name', '')
        component_names = [name.strip() for name in component_names_str.split(',') if name.strip()]

        for name in component_names:
            data = {
                'equipment_id': equipment_id,
                'project_id': project_id,
                'name': name
            }
            Components.add_component(data)

        return redirect(url_for('wallchart', project_id=project_id))

    return render_template('components/add_components.html', project_id=project_id, equipment_id=equipment_id)

@app.route('/manage_components/<int:project_id>/<int:equipment_id>', methods=['GET', 'POST'])
def manage_components(project_id, equipment_id):
    if request.method == 'POST':
        component_names_str = request.form.get('name', '')
        component_names = [name.strip() for name in component_names_str.split(',') if name.strip()]

        for name in component_names:
            data = {
                'equipment_id': equipment_id,
                'project_id': project_id,
                'name': name
            }
            Components.add_component(data)

        flash('Components added successfully')
        return redirect((f'/wallchart/{project_id}'))

    components = Components.get_components_by_equipment_id(equipment_id)
    return render_template('components/manage_components.html', components=components, project_id=project_id, equipment_id=equipment_id)

@app.route('/wallchart/<int:project_id>')
def wallchart(project_id):
    project = Projects.get_project_by_id(project_id)
    equipment_types = Equipment.get_distinct_equipment_types(project_id)
    equipment_data = Equipment.get_equipment_by_project(project_id)

    components_by_equipment = {}
    for equipment in equipment_data:
        components = Components.get_components_by_equipment_id(equipment.id)
        for component in components:
            component_methods = Component_Methods.get_methods_by_component_id(component.id)
            component.methods = [method['method_type'] for method in component_methods]
        components_by_equipment[equipment.id] = components
    
    return render_template('wallchart/wallchart.html', equipment_types=equipment_types, equipment_data=equipment_data, project=project, components_by_equipment=components_by_equipment)


@app.route('/view_wallchart/<int:project_id>')
def view_wallchart(project_id):
    # Get the equipment type from the query parameters, default to 'Exchanger' if not provided
    equipment_type = request.args.get('equipment_type', 'Exchanger')

    # Fetch equipment data for the specified project
    equipment_data = Equipment.get_equipment_by_project(project_id)

    # Filter equipment data based on the equipment type
    if equipment_type and equipment_type != 'all':
        equipment_data = [equipment for equipment in equipment_data if equipment.type == equipment_type]

    project = Projects.get_project_by_id(project_id)

    # Initialize a dictionary to hold components and their methods
    components_by_equipment = {}
    all_component_names = []

    for equipment in equipment_data:
        components = Components.get_components_by_equipment_id(equipment.id)
        component_dict = {component.name: component for component in components}
        components_by_equipment[equipment.id] = component_dict

        for component in components:
            if component.name not in all_component_names:
                all_component_names.append(component.name)
            component_methods = Component_Methods.get_methods_by_component_id(component.id)
            component.methods = [{'id': method['id'], 'method_type': method['method_type'], 'status': method['status']} for method in component_methods]

    # Collect all unique component names and order by creation time
    all_component_names = sorted(all_component_names, key=lambda name: Components.get_component_by_id(component.id).created_at)

    equipment_types = Equipment.get_distinct_equipment_types(project_id)
    
    return render_template('wallchart/equipment_table.html', 
                        project=project, 
                        equipment_data=equipment_data, 
                        components_by_equipment=components_by_equipment, 
                        all_component_names=all_component_names,
                        equipment_types=equipment_types)




@app.route('/update_component/<int:component_id>', methods=['POST'])
def update_status(component_id):
    component = Components.get_component_by_id(component_id)
    if request.method == 'POST':
        status = request.form['status']
        data = {
            'status': status,
            'id': component_id
        }
        Components.edit_component_status(component_id, data)
        flash('Component status updated successfully')
        
        # Redirect to the edit_component page with component_id
        return redirect(url_for('view_wallchart', project_id=request.args.get('project_id')))
    return render_template('components/update_component.html', component = component) 

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
        data = {
            'status': status,
            'component_id': component_id,
            'method_id': method_id
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



