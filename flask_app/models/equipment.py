from flask_app.config.mysqlconnection import connectToMySQL
import pandas as pd 
import re

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
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result


    @classmethod
    def get_equipment_by_project(cls, project_id):
        query = "SELECT * FROM equipment WHERE project_id = %s"
        data = (project_id,)
        results = connectToMySQL(cls.DB).query_db(query, data)

        equipment_list = [Equipment(equipment_data) for equipment_data in results]

        # ✅ Clean and correct sort for equipment like '55V9', '55V10', '55E1', etc.
        def sort_key(e):
            match = re.match(r'([A-Za-z]*)(\d+)', re.sub(r'\D*(\d+)', r'\1', e.number))
            if match:
                prefix = ''.join(re.findall(r'^\D+', e.number))  # non-digits at the start
                number = int(''.join(re.findall(r'\d+', e.number)))  # all digits
                return (prefix, number)
            else:
                return (e.number, 0)

        equipment_list.sort(key=sort_key)
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
    def delete_equipment(cls, equipment_id):
        # Get the connection
        connection = connectToMySQL(cls.DB)
        
        try:
            with connection.connection.cursor() as cursor:
                # Start a transaction
                cursor.execute("START TRANSACTION")
                
                # Delete associated repairs
                delete_repairs_query = """
                    DELETE r FROM repairs r
                    JOIN components c ON r.component_id = c.id
                    WHERE c.equipment_id = %(id)s
                """
                cursor.execute(delete_repairs_query, {"id": equipment_id})

                # Delete associated component methods
                delete_component_methods_query = """
                    DELETE cm FROM component_methods cm
                    JOIN components c ON cm.component_id = c.id
                    WHERE c.equipment_id = %(id)s
                """
                cursor.execute(delete_component_methods_query, {"id": equipment_id})

                # Delete associated components
                delete_components_query = """
                    DELETE FROM components WHERE equipment_id = %(id)s
                """
                cursor.execute(delete_components_query, {"id": equipment_id})

                # Delete the equipment
                delete_equipment_query = """
                    DELETE FROM equipment WHERE id = %(id)s
                """
                cursor.execute(delete_equipment_query, {"id": equipment_id})

                # Commit the transaction
                connection.connection.commit()
            
            return True
        except Exception as e:
            # Rollback the transaction in case of an error
            connection.connection.rollback()
            print(f"Error: {e}")
            return False
        finally:
            connection.connection.close()



    @classmethod
    def get_equipment_number_by_component_id(cls, component_id):
        query = """SELECT equipment.number
                FROM equipment
                JOIN components ON equipment.id = components.equipment_id
                WHERE components.id = %(component_id)s"""
        data = {"component_id": component_id}  # Pass component_id as a dictionary
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results[0]['number'] if results else None
