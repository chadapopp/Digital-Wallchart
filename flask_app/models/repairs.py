from flask_app.config.mysqlconnection import connectToMySQL

class Repairs:
    DB = "digital_wallchart_schema"
    def __init__(self, repair_data):
        self.id = repair_data["id"]
        self.method_id = repair_data["method_id"]
        self.equipment_id = repair_data["equipment_id"]
        self.component_id = repair_data["component_id"]
        self.repair_number = repair_data["repair_number"]
        self.repair_status = repair_data["repair_status"]
        self.description = repair_data["description"]
        self.file_path = repair_data["file_path"]
        self.modified_by = repair_data["modified_by"]
        self.created_at = repair_data["created_at"]
        self.updated_at = repair_data["updated_at"]

    @classmethod
    def save(cls, data):
        query = "INSERT INTO repairs (equipment_id, component_id, repair_number, repair_status, description, file_path) VALUES (%(equipment_id)s, %(component_id)s, %(repair_number)s, %(repair_status)s, %(description)s, %(file_path)s)"
        connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def update_repair(cls, data):
        query = "UPDATE repairs SET component_id = %(component_id)s, repair_number=%(repair_number)s, repair_status=%(repair_status)s, description = %(description)s, file_path = %(file_path)s, modified_by = %(modified_by)s WHERE id = %(id)s"
        data = {
            "id": data["id"],
            "component_id": data["component_id"],
            "repair_number": data["repair_number"],
            "description": data["description"],
            "repair_status": data["repair_status"],
            "file_path": data["file_path"],
            "modified_by": data["modified_by"]
        }
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results

    @classmethod
    def get_by_component_and_equipment(cls, component_id, equipment_id):
        query = """
        SELECT * FROM repairs 
        WHERE component_id = %(component_id)s AND equipment_id = %(equipment_id)s 
        ORDER BY created_at DESC
        """
        data = {
            'component_id': component_id,
            'equipment_id': equipment_id
        }
        return connectToMySQL(cls.DB).query_db(query, data)


    @classmethod
    def get_repairs_by_project(cls, project_id):
        query = """
        SELECT 
            repairs.*, 
            equipment.number AS equipment_number,
            components.name AS component_name
        FROM repairs 
        JOIN equipment ON repairs.equipment_id = equipment.id 
        JOIN components ON repairs.component_id = components.id 
        WHERE equipment.project_id = %(project_id)s 
        ORDER BY repairs.created_at ASC
        """
        data = {
            'project_id': project_id
        }
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results

    @classmethod
    def get_repair_by_id(cls, repair_id):
        query = """
        SELECT repairs.*, projects.id AS project_id
        FROM repairs
        JOIN components ON repairs.component_id = components.id
        JOIN equipment ON components.equipment_id = equipment.id
        JOIN projects ON equipment.project_id = projects.id
        WHERE repairs.id = %(id)s
        ORDER BY repairs.created_at ASC
        """
        data = {'id': repair_id}
        results = connectToMySQL(cls.DB).query_db(query, data)
        print("Query Results:", results) 
        if results:
            return results[0]
        return None

    @classmethod
    def update_repair_status(cls, data):
        query = "UPDATE repairs SET repair_status = %(repair_status)s WHERE id = %(id)s"
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results
    
    @classmethod
    def get_incomplete_repairs_by_method(cls, method_id):
        query = """
        SELECT * FROM repairs 
        WHERE method_id = %(method_id)s 
        AND repair_status NOT IN ('Complete', 'Rejected', 'Deferred')
        """
        data = {'method_id': method_id}
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def get_all_repairs_by_method_completed(cls, method_id):
        query = """
        SELECT * FROM repairs
        WHERE method_id = %(method_id)s
        AND repair_status IN ('Complete', 'Rejected', 'Deferred')
        """
        data = {'method_id': method_id}
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def get_by_component_and_method(cls, component_id, method_id):
        query = """
        SELECT * FROM repairs 
        WHERE component_id = %(component_id)s AND method_id = %(method_id)s 
        ORDER BY created_at DESC
        """
        data = {
            'component_id': component_id,
            'method_id': method_id
        }
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def get_by_method_id(cls, method_id):
        query = """
        SELECT * FROM repairs
        WHERE method_id = %(method_id)s
        ORDER BY created_at DESC
        """
        data = {'method_id': method_id}
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def get_by_component_method_and_equipment(cls, component_id, method_id, equipment_id):
        query = """
            SELECT * FROM repairs
            WHERE component_id = %s AND method_id = %s AND equipment_id = %s
        """
        data = (component_id, method_id, equipment_id)
        return connectToMySQL(cls.DB).query_db(query,data)
