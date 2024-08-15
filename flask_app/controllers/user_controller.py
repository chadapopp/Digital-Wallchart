from flask import session, request, render_template, redirect, flash, url_for
from flask_app import app
from flask_app.models.user import User
from flask_app.models.user_projects import User_Projects
from flask_bcrypt import Bcrypt
from functools import wraps

bcrypt = Bcrypt(app)

@app.route('/create_user', methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        # Generate password hash
        pw_hash = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        
        # Prepare user data
        data = {
            "email": request.form["email"],
            "first_name": request.form['first_name'],
            "last_name": request.form["last_name"],
            "password": pw_hash,
            "role": request.form.get('role'),
            "user_name": request.form['user_name']# Extract role value
        }
        # Create user
        User.create_user(data)
        
        return redirect("/homepage")
    else:
        # Render the create user page
        return render_template("/users/create_user.html")

@app.route('/edit_user/<int:user_id>', methods=["GET", "POST"])
def edit_users(user_id):
    user = User.get_user_by_id(user_id)
    if request.method == "POST":
        # Generate password hash
        pw_hash = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        # Prepare user data
        data = {
            "id": user_id,  # Include the user_id
            "email": request.form["email"],
            "first_name": request.form['first_name'],
            "last_name": request.form["last_name"],
            "password": pw_hash,
            "role": request.form.get('role'),
            "user_name": request.form['user_name']# Extract role value
        }
        # Edit user
        User.edit_user(data)  # Pass only the data dictionary
        return redirect("/show_all_users")
    return render_template('/users/edit_user.html', user=user)

@app.route('/show_all_users', methods=["GET"])
def show_all_users():
    users = User.get_all()
    # Get the role of the logged-in user from the session
    logged_in_user_role = session.get('role')
    return render_template("/users/all_users.html", users=users, logged_in_user_role=logged_in_user_role)

@app.route('/assign_project', methods=['POST'])
def assign_project():
    user_id = request.form['user_id']
    project_id = request.form['project_id']
    User.assign_project(user_id, project_id)
    flash("Project assigned successfully", "success")
    return redirect(f'/view_users_per_project/{project_id}')

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            user_role = session.get('user_role')
            if user_role != required_role:
                return redirect(url_for('access_denied'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator



@app.route('/access_denied')
def access_denied():
    return "Access Denied"

@app.route('/remove_user_from_project/<int:project_id>/<int:user_id>', methods=["POST"])
def remove_user_from_project(project_id, user_id):
    user = User.get_user_by_id(user_id)

    if user:
        if User_Projects.is_user_assigned(user_id, project_id):
            User_Projects.remove_user(user_id, project_id)
            flash(f"{user.first_name} {user.last_name} removed from project.", "success")
        else:
            flash(f"{user.first_name} {user.last_name} is not assigned to this project.", "error")
    else:
        flash(f"User with ID {user_id} not found.", "error")

    return redirect(f"/view_users_per_project/{project_id}")

@app.route('/delete_user/<int:user_id>', methods=[ "GET", "POST"])
def delete_user(user_id):
    user = User.get_user_by_id(user_id)
    
    if user:
        User.delete_user(user_id)
        flash(f"{user.first_name} {user.last_name} deleted successfully.", "success")
    
    return redirect('/show_all_users')
