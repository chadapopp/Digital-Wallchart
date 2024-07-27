from flask import session, request, render_template, redirect, flash
from flask_app import app
from flask_app.models.user import User
from flask_bcrypt import Bcrypt 

bcrypt = Bcrypt(app)

# Display login form
@app.route('/', methods=["GET"])
def login_form():
    return render_template('index.html')

# Handle login form submission
@app.route('/login', methods=['POST'])
def login():
    user = User.get_by_username(request.form.get('user_name'))
    if user:
        session['user_id'] = user.id
        session['first_name'] = user.first_name
        session['last_name'] = user.last_name
        session['user_role'] = user.role
        session['logged_in'] = True
        return redirect('/homepage')
    else:
        flash('Invalid email or password', 'error')
        return redirect('/')

# Display user's homepage
@app.route('/homepage', methods=["GET"])
def user_homepage():
    if 'user_id' not in session:
        return redirect('/')

    user = User.get_user_by_id(session['user_id'])
    
    # Ensure user exists before proceeding
    if not user:
        return redirect('/')
    
    # Retrieve user's first_name and role from the user object
    user_first_name = user.first_name
    user_last_name = user.last_name
    user_role = user.role

    return render_template('homepage.html', user_first_name=user_first_name, user_role=user_role, user_last_name = user_last_name)


# Handle logout
@app.route("/logout")
def logout():
    # Clear session data
    session.clear()
    return redirect('/')
