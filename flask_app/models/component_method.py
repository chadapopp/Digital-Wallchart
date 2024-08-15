from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.method import Methods
from flask_app.models.repairs import Repairs

class Component_Methods:
    DB = "digitalwallchart"
    def __init__(self, cm_data):
        self.id = cm_data["id"]
        self.method_id = cm_data["method_id"]
        self.component_id = cm_data["component_id"]
        self.status = cm_data["status"]
        self.updated_by = cm_data["updated_by"]
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
        SELECT m.id, m.method_type, cm.status, cm.updated_by, cm.created_at, cm.updated_at
        FROM component_methods cm
        JOIN methods m ON cm.method_id = m.id
        WHERE cm.component_id = %(component_id)s
        """
        data = {'component_id': component_id}
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def update_methods_for_component(cls, component_id, selected_methods):
        delete_query = "DELETE FROM component_methods WHERE component_id = %(component_id)s"
        connectToMySQL(cls.DB).query_db(delete_query, {'component_id': component_id})

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
        query = """
        UPDATE component_methods
        SET status = %(status)s, updated_by = %(updated_by)s, updated_at = %(updated_at)s
        WHERE component_id = %(component_id)s AND method_id = %(method_id)s
        """
        connectToMySQL(cls.DB).query_db(query, data)

        if data['status'] == 'Repair Required':
            repair_query = """
            INSERT INTO repairs (component_id, equipment_id, method_id, repair_number, repair_status, description, file_path)
            VALUES (%(component_id)s, %(equipment_id)s, %(method_id)s, %(repair_number)s, %(status)s, %(description)s, %(file_path)s)
            ON DUPLICATE KEY UPDATE
            repair_number = VALUES(repair_number),
            description = VALUES(description),
            file_path = VALUES(file_path)
            """
            connectToMySQL(cls.DB).query_db(repair_query, data)
        
        # Check the method status and ensure repair details are updated correctly
        if data['status'] in ['Complete', 'Rejected', 'Deferred']:
            cls.check_and_update_method_status(data['component_id'], data['method_id'])

    @classmethod
    def check_and_update_method_status(cls, component_id, method_id):
        # This should not change the repair number or file path
        incomplete_repairs = Repairs.get_incomplete_repairs_by_method(method_id)
        if not incomplete_repairs:
            cls.update_method_status_to_complete(component_id, method_id)

    @classmethod
    def update_method_status_to_complete(cls, component_id, method_id):
        query = """
        UPDATE component_methods 
        SET status = 'Complete'
        WHERE component_id = %(component_id)s AND method_id = %(method_id)s
        AND status NOT IN ('Complete', 'Rejected', 'Deferred')
        """
        data = {
            'component_id': component_id,
            'method_id': method_id
        }
        connectToMySQL(cls.DB).query_db(query, data)

        
    @classmethod
    def update_method_status_if_all_repairs_complete(cls, component_id, method_id):
        all_repairs_complete = Repairs.get_all_repairs_by_method_completed(method_id)
        if all_repairs_complete:
            cls.update_method_status_to_complete(component_id, method_id)




    @classmethod
    def get_methods_by_project_id(cls, project_id):
        query = """
        SELECT cm.component_id, c.name, m.method_type, cm.status, cm.updated_by
        FROM component_methods cm
        JOIN components c ON cm.component_id = c.id
        JOIN methods m ON cm.method_id = m.id
        WHERE c.project_id = %(project_id)s
        """
        data = {'project_id': project_id}
        return connectToMySQL(cls.DB).query_db(query, data)
