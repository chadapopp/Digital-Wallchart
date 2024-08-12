from flask import session, request, render_template, redirect, flash, jsonify, send_file, url_for
from flask_app import app
from flask_app.models.project import Projects
from flask_app.models.user import User
from flask_app.models.component import Components
from flask_app.models.equipment import Equipment
from flask_app.models.repairs import Repairs
from flask_app.models.component_method import Component_Methods
from flask_app.models.user_projects import User_Projects
import pandas as pd
from io import BytesIO
import os


@app.route('/create_project', methods=["GET", "POST"])
def create_project():
    if request.method == "POST":
        # Prepare user data
        data = {
            "user_id": session.get('user_id'),
            "project_name": request.form["project_name"],
            "project_company": request.form["project_company"]
        }
        # Create user
        Projects.create_new_project(data)

        return redirect("/show_all_projects")
    else:
        # Render the create user page
        return render_template("/projects/create_project.html")

@app.route('/show_all_projects', methods=["GET"])
def show_all_projects():
    user_id = session.get('user_id')
    user_role = session.get('user_role')

    if user_role == 'admin':
        projects = Projects.get_all()
    else:
        projects = Projects.get_projects_by_user_id(user_id)
    print("Role:" , user_role)
    return render_template("/projects/all_projects.html", projects=projects, user_role=user_role)


@app.route('/add_user_to_project/<int:project_id>', methods=["GET", "POST"])
def add_user_to_project(project_id):
    if request.method == "POST":
        # Get form data
        user_id = request.form.get('user_id')

        # Query the database to get the selected user
        user = User.get_user_by_id(user_id)

        if user:
            # If user is found, check if they are already assigned to the project
            if User_Projects.is_user_assigned(user_id, project_id):
                flash(f"{user.first_name} {user.last_name} is already assigned to this project.", "error")
            else:
                # If not assigned, proceed to assign them
                project = Projects.get_project_by_id(project_id)
                if project:
                    User_Projects.assign_user(user_id, project_id)  # Corrected usage
                    flash(f"{user.first_name} {user.last_name} assigned to {project.project_name}.", "success")
                else:
                    flash(f"Project with ID {project_id} not found.", "error")
        else:
            flash(f"User with ID {user_id} not found.", "error")

        return redirect(f"/view_users_per_project/{project_id}")

    else:
        # Retrieve all users from the database
        users = User.get_all()
        return render_template("/projects/add_user_to_project.html", users=users, project_id=project_id)


@app.route('/view_users_per_project/<int:project_id>', methods=["GET"])
def view_users_per_project(project_id):
    users_data = User_Projects.view_all_users_per_project(project_id)
    project = Projects.get_project_by_id(project_id)
    
    users = []
    for user_data in users_data:
        user = User(user_data)  # Assuming User class accepts user data dictionary in its constructor
        users.append(user)
    
    if not users:
        flash(f"No users found for project with ID {project_id}.", "error")
        return redirect(f"/add_user_to_project/{project_id}")

    # Pass the list of users to the template for rendering
    return render_template("/projects/view_users_per_project.html", users=users, project=project)  

@app.route('/view_project_by_id/<int:project_id>', methods=["GET"])
def view_project_by_id(project_id):
    # Retrieve project information
    project = Projects.get_project_by_id(project_id)
    if not project:
        flash(f"Project with ID {project_id} not found.", "error")
        return redirect("/show_all_projects")
    return render_template("/projects/project_dashboard.html", project=project)

@app.route('/project/status_page/<int:project_id>')
def status_page(project_id):
    return render_template('projects/status_page.html', project_id=project_id)

@app.route('/project/status/<int:project_id>')
def project_status(project_id):
    equipment_data = Equipment.get_equipment_by_project(project_id)

    total_methods = 0
    completed_methods = 0
    repair_methods = 0
    repairs_info = []

    for equipment in equipment_data:
        components = Components.get_components_by_equipment_id(equipment.id)
        for component in components:
            component_methods = Component_Methods.get_methods_by_component_id(component.id)
            total_methods += len(component_methods)
            for method in component_methods:
                if method['status'] == 'Complete':
                    completed_methods += 1
                elif method['status'] == 'Repair Required':
                    repair_methods += 1
                    repair_info = Repairs.get_by_component_and_equipment(component.id, equipment.id)
                    if repair_info:
                        repair_info = repair_info[0] if isinstance(repair_info, list) and len(repair_info) > 0 else repair_info
                        method['repair_number'] = repair_info.get('repair_number', 'N/A')
                        method['file_path'] = repair_info.get('file_path', '')
                        document_url = None
                        if method['file_path']:
                            document_url = url_for('uploaded_file', filename=os.path.basename(method['file_path']))
                        repairs_info.append({
                            'component': component.name,
                            'equipment': equipment.number,
                            'status': method['status'],
                            'description': repair_info.get('description', 'No description available'),
                            'document': document_url,
                            'repair_number': repair_info.get('repair_number', 'N/A')
                        })

    if total_methods > 0:
        completed_percentage = (completed_methods / total_methods) * 100
        repair_percentage = (repair_methods / total_methods) * 100
        pending_percentage = 100 - completed_percentage - repair_percentage
    else:
        completed_percentage = repair_percentage = pending_percentage = 0

    return jsonify({
        'complete': completed_percentage,
        'repair': repair_percentage,
        'pending': pending_percentage,
        'repairs': repairs_info
    })

    
@app.route('/export_data/<int:project_id>')
def export_data(project_id):
    # Fetch equipment data for the specified project
    equipment_data = Equipment.get_equipment_by_project(project_id)

    # Prepare data for export
    export_data = []
    component_order = []  # List to maintain order of components

    for equipment in equipment_data:
        components = Components.get_components_by_equipment_id(equipment.id)
        for component in components:
            if component.name not in [name for name, _ in component_order]:
                component_order.append((component.name, component.created_at))
            component_methods = Component_Methods.get_methods_by_component_id(component.id)
            method_summary = ', '.join([f"{method['method_type']} ({method['status']})" for method in component_methods])

            export_data.append({
                'Equipment Number': equipment.number,
                'Component Name': component.name,
                'Methods': method_summary,
                'Created At': component.created_at  # Add created_at field
            })

    # Sort the component_order list by the created_at field
    component_order.sort(key=lambda x: x[1])

    # Separate the "Report" and "Closure" components if they exist
    report_component = None
    closure_component = None
    sorted_component_names = []
    for name, created_at in component_order:
        if name.lower() == 'report':
            report_component = name
        elif name.lower() == 'closure':
            closure_component = name
        else:
            sorted_component_names.append(name)

    # Append the "Closure" component before the "Report" component at the end
    if closure_component:
        sorted_component_names.append(closure_component)
    if report_component:
        sorted_component_names.append(report_component)

    # Convert data to DataFrame
    df = pd.DataFrame(export_data)

    # Pivot the DataFrame to aggregate methods and statuses for each component within each equipment row
    pivot_df = df.pivot_table(
        index='Equipment Number',
        columns='Component Name',
        values='Methods',  # Removed the list to avoid MultiIndex
        aggfunc=lambda x: ' | '.join(x) if len(x) > 1 else x.iloc[0]
    )

    # Reorder the columns according to sorted_component_names
    pivot_df = pivot_df.reindex(columns=sorted_component_names)

    # Flatten the column MultiIndex (if there's any)
    if isinstance(pivot_df.columns, pd.MultiIndex):
        pivot_df.columns = [' '.join(col).strip() for col in pivot_df.columns.values]

    # Reset the index to turn the index into a column
    pivot_df.reset_index(inplace=True)

    # Create an in-memory output file for the Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pivot_df.to_excel(writer, index=False, sheet_name='Project Data')

    output.seek(0)

    return send_file(output, download_name='project_data.xlsx', as_attachment=True)

@app.route('/delete_project/<int:project_id>')
def remove_project(project_id):
    # Retrieve project details before deletion
    project = Projects.get_project_by_id(project_id)
    
    if not project:
        flash(f'Project with ID {project_id} not found', 'danger')
        return redirect(url_for('show_all_projects'))


    if Projects.remove_project(project_id):
        flash(f'Project "{project.project_name}" deleted successfully', 'success')
    else:
        flash(f'Failed to delete project "{project.project_name}"', 'danger')
    
    return redirect(url_for('show_all_projects'))


