from flask_app.config.mysqlconnection import connectToMySQL
import pandas as pd 

class Equipment:
    DB = "digital_wallchart_schema"
    def __init__(self, equip_data):
        self.id = equip_data["id"]
        self.project_id = equip_data["project_id"]
        self.user_id = equip_data["user_id"]
        self.name = equip_data["name"]
        self.number = equip_data["number"]
        self.scope = equip_data["scope"]
        self.type = equip_data["type"]
        self.created_at = equip_data["created_at"]
        self.updated_at = equip_data["updated_at"]
        
    
    @classmethod
    def add_equipment_by_file(cls, df, project_id, user_id):
        for index, row in df.iterrows():
            data = {
                "project_id": project_id,  # Use the provided project_id
                "user_id": user_id,  # Assuming user_id may be optional
                "type": row["type"],
                "name": row["name"],
                "number": row["number"],
                "scope": row["scope"]
            }
            query = "INSERT INTO equipment (project_id, user_id, type, name, number, scope) VALUES (%(project_id)s, %(user_id)s, %(type)s, %(name)s, %(number)s, %(scope)s)"
            connectToMySQL(cls.DB).query_db(query, data)
            
    @classmethod
    def add_single_equipment(cls, data):
        query = "INSERT INTO equipment (project_id, user_id, name, number, type, scope) VALUES (%(project_id)s, %(user_id)s, %(name)s, %(number)s, %(type)s, %(scope)s)"
        connectToMySQL(cls.DB).query_db(query, data)


    @classmethod
    def get_equipment_by_project(cls, project_id):
        query = "SELECT * FROM equipment WHERE project_id = %s"
        data = (project_id,)
        results = connectToMySQL(cls.DB).query_db(query, data)
        equipment_list = [Equipment(equipment_data) for equipment_data in results]  # Convert dictionary objects to Equipment instances
        return equipment_list

    @classmethod
    def get_equipment_by_id(cls, equipment_id):
        query = "SELECT * FROM equipment WHERE id = %s"
        data = (equipment_id,)
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results
    
    @classmethod
    def get_equipment_by_number(cls, number):
        query = "SELECT * FROM equipment WHERE number = %s"
        data = (number,)
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results
    
    @classmethod
    def get_equipment_by_type(cls, type):
        query = "SELECT * FROM equipment WHERE type = %s"
        data = (type,)
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results
    
    @classmethod
    def get_distinct_equipment_types(cls, project_id):
        query = """SELECT DISTINCT type
                FROM equipment
                WHERE project_id = %(project_id)s"""
        data = {"project_id": project_id}  # Pass project_id as a dictionary
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results

    
    @classmethod
    def edit_equipment(cls, data):
        query = "UPDATE equipment SET name=%(name)s, number=%(number)s, scope=%(scope)s, type=%(type)s WHERE id=%(id)s"
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results


    @classmethod
    def delete_equipment(cls, data):
        query = "DELETE FROM equipment WHERE id=%(id)s"
        connectToMySQL(cls.DB).query_db(query, data)
        return True
    
    @classmethod
    def get_exchangers_by_project(cls, project_id):
        query = """SELECT *
                FROM equipment
                WHERE project_id = %(project_id)s
                AND type = 'exchanger'"""
        data = {"project_id": project_id}  # Pass project_id as a dictionary
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results
    
    @classmethod
    def get_equipment_number_by_component_id(cls, component_id):
        query = """SELECT equipment.number
                FROM equipment
                JOIN components ON equipment.id = components.equipment_id
                WHERE components.id = %(component_id)s"""
        data = {"component_id": component_id}  # Pass component_id as a dictionary
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results[0]['number'] if results else None