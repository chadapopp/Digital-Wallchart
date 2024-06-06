from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.method import Methods
from flask_app.models.repairs import Repairs

class Component_Methods:
    DB = "digital_wallchart_schema"
    def __init__(self, cm_data):
        self.id = cm_data["id"]
        self.method_id = cm_data["method_id"]
        self.component_id = cm_data["component_id"]
        self.status = cm_data["status"]
        self.created_at = cm_data["created_at"]
        self.updated_at = cm_data["updated_at"]
        

    @classmethod
    def add_or_update_method(cls, component_id, method_id, status):
        query = """
        INSERT INTO component_methods (component_id, method_id, status)
        VALUES (%(component_id)s, %(method_id)s, %(status)s)
        ON DUPLICATE KEY UPDATE status=VALUES(status)
        """
        data = {
            'component_id': component_id,
            'method_id': method_id,
            'status': status
        }
        connectToMySQL(cls.DB).query_db(query, data)
    
    
    @classmethod
    def get_methods_by_component_id(cls, component_id):
        query = """
        SELECT m.id, m.method_type, cm.status 
        FROM component_methods cm
        JOIN methods m ON cm.method_id = m.id
        WHERE cm.component_id = %(component_id)s
        """
        data = {'component_id': component_id}
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def update_methods_for_component(cls, component_id, selected_methods):
        # First, delete existing methods for the component
        delete_query = "DELETE FROM component_methods WHERE component_id = %(component_id)s"
        connectToMySQL(cls.DB).query_db(delete_query, {'component_id': component_id})

        # Then, insert the new methods
        for method_name in selected_methods:
            method = Methods.get_method_by_name(method_name)
            if not method:
                method_id = Methods.add_method(method_name)
            else:
                method_id = method['id']
            insert_query = "INSERT INTO component_methods (component_id, method_id) VALUES (%(component_id)s, %(method_id)s)"
            connectToMySQL(cls.DB).query_db(insert_query, {'component_id': component_id, 'method_id': method_id})

    @classmethod
    def delete_method_from_component(cls, component_id, method_id):
        query = "DELETE FROM component_methods WHERE component_id = %(component_id)s AND method_id = %(method_id)s"
        data = {
            'component_id': component_id,
            'method_id': method_id
        }
        connectToMySQL(cls.DB).query_db(query, data)
                

    @classmethod
    def update_method_status(cls, data):
        # Update the method status and add repair info if needed
        query = """
        UPDATE component_methods
        SET status = %(status)s
        WHERE component_id = %(component_id)s AND method_id = %(method_id)s
        """
        connectToMySQL(cls.DB).query_db(query, data)

        # If there's repair data, update or insert into repairs table
        if data['status'] == 'Repair Required':
            repair_query = """
            INSERT INTO repairs (component_id, equipment_id, method_id, repair_number, description, file_path)
            VALUES (%(component_id)s, %(equipment_id)s, %(method_id)s, %(repair_number)s, %(description)s, %(file_path)s)
            ON DUPLICATE KEY UPDATE
            repair_number = VALUES(repair_number),
            description = VALUES(description),
            file_path = VALUES(file_path)
            """
            connectToMySQL(cls.DB).query_db(repair_query, data)

        
    @classmethod
    def get_methods_by_project_id(cls, project_id):
        query = """
        SELECT cm.component_id, c.name, m.method_type, cm.status
        FROM component_methods cm
        JOIN components c ON cm.component_id = c.id
        JOIN methods m ON cm.method_id = m.id
        WHERE c.project_id = %(project_id)s
        """
        data = {'project_id': project_id}
        return connectToMySQL(cls.DB).query_db(query, data)