import bcrypt
from flask import session, request, render_template, redirect, flash, jsonify, url_for, send_from_directory
from flask_app import app
from flask_app.models.project import Projects
from flask_app.models.component import Components
from flask_app.models.equipment import Equipment
from flask_app.models.user import User
from flask_app.models.repairs import Repairs
from flask_app.models.component_method import Component_Methods
from flask_bcrypt import Bcrypt 
import os

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


        
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

@app.route('/create_user', methods=["GET", "POST"])
def create_user():
    if request.method == "POST":

        data = {
            "email": request.form["email"],
            "first_name": request.form['first_name'],
            "last_name": request.form["last_name"],
            "password": request.form['password'],
            "user_name": request.form['user_name'],  # Use plain text for simplicity, consider hashing in production
            "role": request.form.get('role')  # Extract permissions value
        }
        # Create user
        User.create_user(data)
        
        return redirect("/show_all_users")
    else:
        # Render the create user page
        return render_template("/users/create_user.html")

@app.route('/show_all_users', methods = ["GET"])
def show_all_users():
    users = User.get_all()
    return render_template("/users/all_users.html", users = users)

@app.route('/edit_user/<int:user_id>', methods=["GET", "POST"])
def edit_users(user_id):
    user = User.get_user_by_id(user_id)

    if request.method == "POST":
        data = {
            "id": user_id,
            "email": request.form["email"],
            "first_name": request.form["first_name"],
            "last_name": request.form["last_name"],
            "role": request.form.get("role"),
            "password": request.form["password"],
            "user_name": request.form["user_name"]
        }

        User.edit_user(data)
        return redirect("/show_all_users")

    return render_template("users/edit_user.html", user=user)

    
@app.route('/assign_project', methods=['POST'])
def assign_project():
    user_id = request.form['user_id']
    project_id = request.form['project_id']
    User.assign_project(user_id, project_id)
    flash("Project assigned successfully", "success")
    return redirect('/projects')

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    User.delete_user(user_id)
    flash("User deleted successfully", "success")
    return redirect('/show_all_users')
