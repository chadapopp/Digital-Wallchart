from flask_app.config.mysqlconnection import connectToMySQL

class Projects:
    DB = "digital_wallchart_schema"
    def __init__(self, project_data):
        self.id = project_data["id"]
        self.user_id = project_data["user_id"]
        self.project_name = project_data["project_name"]
        self.project_company = project_data["project_company"]
        self.created_at = project_data["created_at"]
        self.updated_at = project_data["updated_at"]
        
    @classmethod
    def create_new_project(cls, data):
        query = """INSERT INTO projects (user_id, project_name, project_company) VALUES (%(user_id)s, %(project_name)s,%(project_company)s)"""
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result
    
    @classmethod
    def edit_project(cls, project_id, data):
        query = """
            UPDATE projects
            SET project_name = %(project_name)s, project_company = %(project_company)s
            WHERE id = %(project_id)s
        """
        data['id'] = project_id
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result
    
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM projects"
        result = connectToMySQL(cls.DB).query_db(query)
        projects = []
        for project in result:
            projects.append(cls(project))
        print(projects)
        return projects
    
    @classmethod
    def get_project_by_id(cls, project_id):
        query = "SELECT * FROM projects WHERE id = %(project_id)s"
        result = connectToMySQL(cls.DB).query_db(query, {'project_id':project_id})
        if len(result) < 1:
            return False
        return cls(result[0])
    
    @classmethod
    def remove_project(cls, project_id):
        query = "DELETE FROM projects WHERE id = %(project_id)s"
        result = connectToMySQL(cls.DB).query_db(query, {'project_id':project_id})
        return result

