from flask_app.config.mysqlconnection import connectToMySQL

class Repairs:
    DB = "digital_wallchart_schema"
    def __init__(self, repair_data):
        self.id = repair_data["id"]
        self.equipment_id = repair_data["equipment_id"]
        self.component_id = repair_data["component_id"]
        self.repair_number = repair_data["repair_number"]
        self.description = repair_data["description"]
        self.file_path = repair_data["file_path"]
        self.created_at = repair_data["created_at"]
        self.updated_at = repair_data["updated_at"]

    @classmethod
    def save(cls, data):
        query = "INSERT INTO repairs (equipment_id, component_id, repair_number, description, file_path) VALUES (%(equipment_id)s, %(component_id)s, %(repair_number)s, %(description)s, %(file_path)s)"
        connectToMySQL(cls.DB).query_db(query, data)
        
    @classmethod
    def update_repair(cls, data):
        query = "UPDATE repairs SET component_id = %(component_id)s, repair_number=%(repair_number)s, description = %(description)s, file_path = %(file_path)s WHERE id = %(id)s"
        data = {
            "id": data["id"],
            "component_id": data["component_id"],
            "repair_number": data["repair_number"],
            "description": data["description"],
            "file_path": data["file_path"]
        }
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results
    
    @classmethod
    def get_by_component_and_equipment(cls, component_id, equipment_id):
        query = "SELECT * FROM repairs WHERE component_id = %(component_id)s AND equipment_id = %(equipment_id)s ORDER BY created_at DESC LIMIT 1"
        data = {
            "component_id": component_id,
            "equipment_id": equipment_id
        }
        results = connectToMySQL(cls.DB).query_db(query, data)
        if results:
            return results[0]
        else:
            return None


    # @classmethod
    # def get_by_component_and_equipment_and_method(cls, component_id, equipment_id, method_id):
    #     query = """
    #     SELECT repair_number, description, file_path
    #     FROM repairs
    #     WHERE component_id = %(component_id)s AND equipment_id = %(equipment_id)s AND method_id = %(method_id)s
    #     """
    #     data = {
    #         'component_id': component_id,
    #         'equipment_id': equipment_id,
    #         'method_id': method_id
    #     }
    #     results = connectToMySQL(cls.DB).query_db(query, data)
    #     return results