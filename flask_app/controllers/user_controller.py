from flask import session, request, render_template, redirect, flash
from flask_app import app
from flask_app.models.user import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/create_user', methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        # Generate password hash
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        
        # Prepare user data
        data = {
            "email": request.form["email"],
            "first_name": request.form['first_name'],
            "last_name": request.form["last_name"],
            "password": pw_hash,
            "role": request.form.get('role')  # Extract permissions value
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
        pw_hash = bcrypt.generate_password_hash(request.form['password'])

        # Prepare user data
        data = {
            "id": user_id,  # Include the user_id
            "email": request.form["email"],
            "first_name": request.form['first_name'],
            "last_name": request.form["last_name"],
            "password": pw_hash,
            "role": request.form.get('role')  # Extract permissions value
        }
        # Edit user
        User.edit_user(user_id, data)  # Pass user_id as the first argument
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
    return redirect('/projects')

