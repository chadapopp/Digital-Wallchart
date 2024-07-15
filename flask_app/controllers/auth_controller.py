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
    user = User.get_by_email(request.form.get('email'))
    if user:
        session['user_id'] = user.id
        session['first_name'] = user.first_name
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
    user_role = user.role

    return render_template('homepage.html', user_first_name=user_first_name, user_role=user_role)


# Handle logout
@app.route("/logout")
def logout():
    # Clear session data
    session.clear()
    return redirect('/')


# from flask_app.config.mysqlconnection import connect_to_mysql
# # Function to hash passwords and update them in the database
# def hash_and_update_passwords():
#     # Create a connection to MySQL
#     connection = connect_to_mysql('digital_wallchart_schema')

#     # Export plaintext passwords from the database
#     query = "SELECT id, password FROM users"
#     passwords = connection.query_db(query)

#     # Hash passwords using bcrypt
#     hashed_passwords = []
#     for user in passwords:
#         id = user['id']
#         password = user['password']
#         hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
#         hashed_passwords.append((id, hashed_password))


#     # Update passwords in the database
#     for id, hashed_password in hashed_passwords:
#         query = "UPDATE users SET password = %s WHERE id = %s"
#         connection.query_db(query, (hashed_password, id))

#     print("Passwords hashed and updated successfully.")

# # Call the function to hash passwords and update them in the database
# hash_and_update_passwords()
