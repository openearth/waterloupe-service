# FLASK
from flask import Flask, jsonify, request
from pathlib import Path
import sqlalchemy
from sqlalchemy import column, func, select
from flask_cors import CORS  # only for development
from utils import establish_db_connection
import json

application = Flask(__name__)

CORS(application)  # only for development
service_path = Path(__file__).resolve().parent
conf_file = service_path / "configuration.txt"


engine, connection = establish_db_connection()


metadata = sqlalchemy.MetaData()
metadata.reflect(views=True, bind=engine, schema="wl")

period = metadata.tables["wl.period"]
scenario_data = metadata.tables["wl.scenariodata"]
scenario_data_agg = metadata.tables["wl.scenariodata_agg"]


@application.route("/")
def hello_world():
    return "Waterloupe api"


@application.route("/api/bar_chart", methods=["GET", "POST"])
def bar_chart():
    """** WIP ** The bar_chart is a stacked bar chart. Reads from database series data and period names
    Inputs: scenario, area, solution
    """

    inputs = request.json

    scenario = inputs["scenario"]
    area = inputs["area"]
    solution = inputs["solution"]

    # query series for bar chart
    query = select(func.wl.scenariodata_agg_json(area, scenario, solution))
    result = connection.execute(query).fetchone()

    # Get base options for the bar chart
    with open('echarts-templates/bar-chart.json', 'r') as f:
        base_options = json.load(f)

    response = dict(result.items())[
        "scenariodata_agg_json_1"
    ]  # TODO: see what the scenario_data_agg_json_1 stands for in the response

    return jsonify({**base_options,**response})
