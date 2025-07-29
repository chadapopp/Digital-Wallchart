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
        return projects
    
    @classmethod
    def get_project_by_id(cls, project_id):
        query = "SELECT * FROM projects WHERE id = %(project_id)s"
        result = connectToMySQL(cls.DB).query_db(query, {'project_id':project_id})
        if len(result) < 1:
            return False
        return cls(result[0])
    
    @classmethod
    def get_projects_by_user_id(cls, user_id):
        query = """
        SELECT projects.* FROM projects
        JOIN user_projects ON projects.id = user_projects.project_id
        WHERE user_projects.user_id = %(user_id)s
        """
        result = connectToMySQL(cls.DB).query_db(query, {'user_id': user_id})
        projects = []
        for project in result:
            projects.append(project)
        return projects
    

    @classmethod
    def remove_project(cls, project_id):
        connection = connectToMySQL(cls.DB)
        cursor = connection.connection.cursor()

        try:
            # Start a transaction
            cursor.execute("START TRANSACTION")
            
            delete_user_projects_query = """
                DELETE FROM user_projects WHERE project_id = %(project_id)s
            """
            cursor.execute(delete_user_projects_query, {"project_id": project_id})
            
            # Delete associated repairs
            delete_repairs_query = """
                DELETE r FROM repairs r
                JOIN components c ON r.component_id = c.id
                JOIN equipment e ON c.equipment_id = e.id
                WHERE e.project_id = %(project_id)s
            """
            cursor.execute(delete_repairs_query, {"project_id": project_id})

            # Delete associated component methods
            delete_component_methods_query = """
                DELETE cm FROM component_methods cm
                JOIN components c ON cm.component_id = c.id
                JOIN equipment e ON c.equipment_id = e.id
                WHERE e.project_id = %(project_id)s
            """
            cursor.execute(delete_component_methods_query, {"project_id": project_id})

            # Delete associated components
            delete_components_query = """
                DELETE c FROM components c
                JOIN equipment e ON c.equipment_id = e.id
                WHERE e.project_id = %(project_id)s
            """
            cursor.execute(delete_components_query, {"project_id": project_id})

            # Delete associated equipment
            delete_equipment_query = """
                DELETE FROM equipment WHERE project_id = %(project_id)s
            """
            cursor.execute(delete_equipment_query, {"project_id": project_id})

            # Delete the project
            delete_project_query = """
                DELETE FROM projects WHERE id = %(project_id)s
            """
            cursor.execute(delete_project_query, {"project_id": project_id})

            # Commit the transaction
            cursor.execute("COMMIT")
            
            return True
        except Exception as e:
            # Rollback the transaction in case of an error
            cursor.execute("ROLLBACK")
            print(f"Error: {e}")
            return False
        finally:
            cursor.close()
            connection.connection.close()

