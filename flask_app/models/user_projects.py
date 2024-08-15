from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.user import User

class User_Projects:
    DB = "digitalwallchart"
    def __init__(self, user_projects_data):
        self.id = user_projects_data["id"]
        self.user_id = user_projects_data["user_id"]
        self.project_id = user_projects_data["project_id"]
        self.user = []
        
    @classmethod
    def assign_user(cls, user_id, project_id):
        query = "INSERT INTO user_projects (user_id, project_id) VALUES (%s, %s)"
        data = (user_id, project_id)
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result

    @classmethod
    def view_all_users_per_project(cls, project_id):
        query = """
            SELECT *, users.id, users.first_name, users.last_name, users.email, users.password, users.role, users.created_at, users.updated_at
            FROM users
            INNER JOIN user_projects ON users.id = user_projects.user_id
            INNER JOIN projects ON user_projects.project_id = projects.id
            WHERE projects.id = %(project_id)s
        """
        data = {'project_id': project_id}
        result = connectToMySQL(cls.DB).query_db(query, data)
        if result: 
            return result  # Return the list of users
        else: 
            return []  # Return an empty list if no users found
    
    
    @staticmethod
    def is_user_assigned(user_id, project_id):
        query = "SELECT COUNT(*) as count FROM user_projects WHERE user_id = %(user_id)s AND project_id = %(project_id)s"
        data = {
            "user_id": user_id,
            "project_id": project_id
        }
        result = connectToMySQL("digital_wallchart_schema").query_db(query, data)
        return result[0]['count'] > 0

    @staticmethod
    def remove_user(user_id, project_id):
        query = "DELETE FROM user_projects WHERE user_id = %(user_id)s AND project_id = %(project_id)s"
        data = {
            "user_id": user_id,
            "project_id": project_id
        }
        return connectToMySQL("digital_wallchart_schema").query_db(query, data)



