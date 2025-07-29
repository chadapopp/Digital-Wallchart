from flask_app.config.mysqlconnection import connectToMySQL

class Methods:
    DB = "digitalwallchart"

    def __init__(self, method_data):
        self.id = method_data["id"]
        self.method_type = method_data["method_type"]
        self.created_at = method_data["created_at"]
        self.updated_at = method_data["updated_at"]

    @classmethod
    def get_method_by_id(cls, method_id):
        query = "SELECT * FROM methods WHERE id = %(id)s"
        data = {'id': method_id}
        results = connectToMySQL(cls.DB).query_db(query, data)
        if results:
            return cls(results[0])
        return None

    @classmethod
    def get_or_create_method(cls, method_name):
        query = "SELECT id FROM methods WHERE method_type = %(method_type)s"
        data = {'method_type': method_name}
        results = connectToMySQL(cls.DB).query_db(query, data)
        if results:
            return results[0]['id']
        else:
            query = "INSERT INTO methods (method_type) VALUES (%(method_type)s)"
            return connectToMySQL(cls.DB).query_db(query, data)
        
    @classmethod
    def add_method_to_component(cls, data):
        method_query = "INSERT INTO methods (method_type, status) VALUES (%(method_type)s, %(status)s)"
        method_id = connectToMySQL(cls.DB).query_db(method_query, data)
        link_query = "INSERT INTO component_methods (component_id, method_id) VALUES (%(component_id)s, %(method_id)s)"
        link_data = {'component_id': data['component_id'], 'method_id': method_id}
        connectToMySQL(cls.DB).query_db(link_query, link_data)

    @classmethod
    def add_or_update_method(cls, component_id, method_type, status):
        # Check if the method already exists for the component
        query = """
        INSERT INTO methods (component_id, method_type, status)
        VALUES (%(component_id)s, %(method_type)s, %(status)s)
        ON DUPLICATE KEY UPDATE status=%(status)s
        """
        data = {
            'component_id': component_id,
            'method_type': method_type,
            'status': status
        }
        connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def get_method_by_name(cls, method_type):
        query = "SELECT * FROM methods WHERE method_type = %(method_type)s"
        data = {'method_type': method_type}
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results[0] if results else None
    
    @classmethod
    def add_method(cls, method_type):
        query = "INSERT INTO methods (method_type) VALUES (%(method_type)s)"
        data = {'method_type': method_type}
        return connectToMySQL(cls.DB).query_db(query, data)
    
