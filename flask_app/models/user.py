from flask_app.config.mysqlconnection import connectToMySQL


class User:
    DB = "digitalwallchart"
    def __init__(self, user_data):
        self.id = user_data["id"]
        self.first_name = user_data["first_name"]
        self.last_name = user_data["last_name"]
        self.email = user_data["email"]
        self.password = user_data["password"]
        self.role = user_data["role"]
        self.user_name =   user_data["user_name"]
        self.created_at = user_data["created_at"]
        self.updated_at = user_data["updated_at"]
        
    
    @classmethod
    def create_user(cls, data):
        query = """INSERT INTO users (first_name, last_name, email, role, user_name, password) VALUES (%(first_name)s, %(last_name)s,%(email)s, %(role)s, %(user_name)s, %(password)s)"""
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result
    
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users"
        result = connectToMySQL(cls.DB).query_db(query)
        users = []
        for user in result:
            users.append(cls(user))
        return users
    
    @classmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM users WHERE email=%(email)s"
        data = {'email': email}
        result = connectToMySQL(cls.DB).query_db(query, data)
        if len(result) < 1:
            return False
        return cls(result[0])
    
    @classmethod
    def get_by_username(cls, user_name):
        query = "SELECT * FROM users WHERE user_name=%(user_name)s"
        data = {'user_name': user_name}
        result = connectToMySQL(cls.DB).query_db(query, data)
        if len(result) <1:
            return False
        return cls(result[0])
    
    @classmethod
    def get_user_by_id(cls, user_id):
        query = "SELECT * FROM users WHERE id = %(user_id)s"
        result = connectToMySQL(cls.DB).query_db(query, {'user_id':user_id})
        if len(result) < 1:
            return False
        return cls(result[0])
    
    @classmethod
    def assign_project(cls, user_id, project_id):
        query = "INSERT INTO user_projects (user_id, project_id) VALUES (%s, %s)"
        data = (user_id, project_id)
        connectToMySQL(cls.DB).query_db(query, data)
        
    @classmethod
    def search_by_first_name(cls, first_name):
        query = "SELECT * FROM users WHERE first_name=%(first_name)s"
        data = {'first_name': first_name}
        result = connectToMySQL(cls.DB).query_db(query, data)
        if len(result) < 1:
            return False
        return cls(result[0])
    
    @classmethod
    def edit_user(cls, data):
        query = "UPDATE users SET first_name=%(first_name)s, last_name=%(last_name)s, email=%(email)s, role=%(role)s, password=%(password)s WHERE id=%(id)s"
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result
