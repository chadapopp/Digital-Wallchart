from flask_app import app

from flask_app.controllers import auth_controller
from flask_app.controllers import user_controller
from flask_app.controllers import project_controller
from flask_app.controllers import equipment_controller
from flask_app.controllers import component_controller
from flask_app.controllers import method_controller
from flask_app.controllers import repair_controller


if __name__ == "__main__":
    app.run(debug=True, port=5000)