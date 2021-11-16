from flask import Flask, render_template, request, redirect,render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import sys
import traceback

from sqlalchemy.sql.expression import delete

app = Flask(__name__)
try:
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
except KeyError:
    os.system("env.bat")
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)
import data.models

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/sync", methods=["GET","POST"])
def sync():
    if request.method == 'POST':
        try:
            from data.projects import sync_projects
            from data.commodities import sync_commodities
            p_added, p_updated = sync_projects(db)
            c_added = sync_commodities(db)
            sync_message = f"{p_added} projects added, {p_updated} projects updated.\n{c_added} lumber prices added."
        except Exception:
            sync_message = traceback.print_exc()
        return render_template("index.html",sync_message=sync_message)
    else:
        return render_template("index.html")

@app.route("/deleteLumber", methods=["POST"])
def delete_lumber():
    if request.method == 'POST':
        from data.commodities import delete_all_lumber
        l_deleted = delete_all_lumber(db)
        sync_message = f"{l_deleted} lumber price records deleted. Press Sync to reload."
        return render_template("index.html",sync_message=sync_message)
    else:
        return render_template('index.html')

@app.route("/deleteProjects", methods=["POST"])
def delete_projects():
    if request.method == 'POST':
        from data.projects import delete_all_projects
        l_deleted = delete_all_projects(db)
        sync_message = f"{l_deleted} project records deleted. Press Sync to reload."
        return render_template("index.html",sync_message=sync_message)
    else:
        return render_template('index.html')

@app.route("/get-estimate", methods=["GET"])
def get_estimate():
    if request.method == 'GET':
        data = request.args
        estimate_output = data['sqft']
        return render_template_string("<b>$ {{estimate_output}} / sqft</b> &#128020 &#128020 &#128020",estimate_output=estimate_output)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run()