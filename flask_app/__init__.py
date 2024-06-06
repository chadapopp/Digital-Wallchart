from flask import Flask, send_from_directory
import os
from os.path import basename

app = Flask(__name__)
app.secret_key = "whateveryou123213432"

# Define the upload folder path
app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")

# Define the static URL path
app.static_url_path = '/static'


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.template_filter('basename')
def get_basename(path):
    return basename(path)

# Create the upload directory if it doesn't exist
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])
