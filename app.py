from flask import Flask, render_template, request, redirect,render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import sys
import traceback
import pandas as pd

from sqlalchemy.sql.expression import delete

from ml.training import train_model

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
            message = f"{p_added} projects added, {p_updated} projects updated.\n{c_added} lumber prices added."
        except Exception:
            message = traceback.print_exc()
        return render_template_string("{{message}}",message=message)
    else:
        return render_template("index.html")

@app.route("/deleteLumber", methods=["POST"])
def delete_lumber():
    if request.method == 'POST':
        from data.commodities import delete_all_lumber
        l_deleted = delete_all_lumber(db)
        message = f"{l_deleted} lumber price records deleted. Press Sync to reload."
        return render_template_string("{{message}}",message=message)
    else:
        return render_template('index.html')

@app.route("/deleteProjects", methods=["POST"])
def delete_projects():
    if request.method == 'POST':
        from data.projects import delete_all_projects
        l_deleted = delete_all_projects(db)
        message = f"{l_deleted} project records deleted. Press Sync to reload."
        return render_template_string("{{message}}",message=message)
    else:
        return render_template('index.html')

@app.route("/get-estimate", methods=["GET"])
def get_estimate():
    if request.method == 'GET':
        from ml.training import get_prediction
        from ml.ml_models import knn_model,rf_model,linear_model
        data = dict(request.args)
        try:
            algorithm = data['algorithm']
            data.pop('algorithm')
            print(data)
            prediction_df = pd.DataFrame(data,index=[0])
            if algorithm == 'KNeighborsRegressor':
                trained_model = knn_model
            elif algorithm == 'RandomForestRegressor':
                trained_model = rf_model
            elif algorithm == 'LinearRegression':
                trained_model = linear_model
            if trained_model:
                estimate = get_prediction(trained_model, prediction_df)[0]
                estimate_string = '{:.3f}'.format(estimate)
            else:
                return render_template_string("TRAIN MODELS FIRST")
            return render_template_string("<b>$ {{estimate_output}} / sqft</b> &#128020 &#128020 &#128020",estimate_output=estimate_string)
        except Exception as ex:
            ex = traceback.print_exc()
            print(ex)
            return render_template_string("{{error_output}}", error_output=ex)
    else:
        return render_template('index.html')

@app.route("/train", methods=['POST'])
def train_all():
    if request.method == 'POST':
        from ml.training import train_and_evaluate_all
        scores, f_importances = train_and_evaluate_all(True) 
        return render_template('ml_scores.html',scores=scores,f_importances=f_importances)

if __name__ == '__main__':
    app.run()