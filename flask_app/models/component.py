from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.method import Methods
from flask_app.models.project import Projects
from flask_app.models.equipment import Equipment
import pandas as pd 

class Components:
    DB = "digitalwallchart"
    
    def __init__(self, component_data):
        self.id = component_data["id"]
        self.equipment_id = component_data["equipment_id"]
        self.project_id = component_data["project_id"]
        self.name = component_data["name"]
        self.created_at = component_data["created_at"]
        self.updated_at = component_data["updated_at"]
        
    @classmethod
    def add_components_by_file(cls, df, project_id):
        for index, row in df.iterrows():
            equipment_number = row["number"]
            equipment = Equipment.get_equipment_by_number(equipment_number)
            if equipment:
                equipment_id = equipment[0]['id']
                component_names_str = row["name"]
                component_names = [name.strip() for name in component_names_str.split(',') if name.strip()]
                for component_name in component_names:
                    data = {
                        "equipment_id": equipment_id,
                        "project_id": project_id,
                        "name": component_name
                    }
                    query = "INSERT INTO components (equipment_id, project_id, name) VALUES (%(equipment_id)s, %(project_id)s, %(name)s)"
                    connectToMySQL(cls.DB).query_db(query, data)
            
    @classmethod
    def add_component(cls, data):
        query = "INSERT INTO components (project_id, equipment_id, name) VALUES (%(project_id)s, %(equipment_id)s, %(name)s)"
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results
        
    @classmethod
    def get_components_by_equipment_id(cls, equipment_id):
        query = """
            SELECT components.*, GROUP_CONCAT(methods.method_type) AS methods 
            FROM components
            LEFT JOIN component_methods ON components.id = component_methods.component_id
            LEFT JOIN methods ON component_methods.method_id = methods.id
            WHERE components.equipment_id = %(equipment_id)s
            GROUP BY components.id
        """
        data = {'equipment_id': equipment_id}
        results = connectToMySQL(cls.DB).query_db(query, data)
        components = []
        if results:
            for result in results:
                component_data = dict(result)
                component_data['methods'] = result['methods'].split(',') if result['methods'] else []
                components.append(cls(component_data))
        
        # Define a specific order for components
        order = ["External", "Shell", "Nozzles", "Shell Cover", "Bonnet","Inlet Channel", "Outlet Channel", "Channel", "Inlet Channel Cover", "Outlet Channel Cover", "Channel Cover", "Bundle", "Floating Head/Split Rings", "Header Boxes", "Tube Sheets", "Tubesheets", "Tubes", "Heads", "Primary Cyclones", "Secondary Cyclones", "Airgrid", "Internal Components", "Radiant Mechanical", "Radiant Refractory", "Convection Mechanical", "Convection Refractory", "Stack", "Closure", "Hydro", "Report"]
        
        # Sort components based on the defined order
        components.sort(key=lambda x: order.index(x.name) if x.name in order else len(order))
        
        return components

    
    @classmethod
    def get_component_by_id(cls, component_id):
        query = "SELECT * FROM components WHERE id = %(component_id)s"
        data = {'component_id': component_id}
        result = connectToMySQL(cls.DB).query_db(query, data)
        if result:
            return cls(result[0])
        else:
            return False
        
    @classmethod
    def get_components_by_equipment_number(cls, number):
        query = """
            SELECT components.* 
            FROM components
            JOIN equipment ON components.equipment_id = equipment.id
            WHERE equipment.number = %(number)s
        """
        data = {'number': number}
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results
    
    @classmethod
    def get_all_components_by_project(cls, project_id):
        query = "SELECT * FROM components WHERE project_id = %(project_id)s"
        data = {'project_id': project_id}
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results

    @classmethod
    def edit_component(cls, component_id, data):
        query = "UPDATE components SET name = %(name)s WHERE id = %(component_id)s"
        data['component_id'] = component_id
        results = connectToMySQL(cls.DB).query_db(query, data)
        return results
    
    @classmethod
    def get_component_by_name_and_equipment_id(cls, name, equipment_id):
        query = "SELECT * FROM components WHERE name = %(name)s AND equipment_id = %(equipment_id)s"
        data = {'name': name, 'equipment_id': equipment_id}
        result = connectToMySQL(cls.DB).query_db(query, data)
        if result:
            return cls(result[0])
        else:
            return False
        
    @classmethod
    def get_component_by_name(cls, name):
        query = "SELECT * FROM components WHERE name = %(name)s"
        data = {'name': name}
        result = connectToMySQL(cls.DB).query_db(query, data)
        if result:
            return cls(result[0])
        else:
            return False
    
    @classmethod
    def edit_component(cls, data):
        query = "UPDATE components SET name=%(name)s WHERE id=%(id)s"
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def delete_component(cls, component_id):
        query = "DELETE FROM components WHERE id = %(component_id)s"
        data = {'component_id': component_id}
        return connectToMySQL(cls.DB).query_db(query, data)
