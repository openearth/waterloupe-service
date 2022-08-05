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
    area = inputs["area"].replace(" ", "")
    formatted_area = area[0].lower() + area[1:]
    solution = inputs["solution"]

    # query series for bar chart
    query = select(func.wl.scenariodata_agg_json(formatted_area, scenario, solution))
    result = connection.execute(query).fetchone()

    # Get base options for the bar chart
    with open("echarts-templates/bar-chart.json", "r") as f:
        base_options = json.load(f)

    response = dict(result.items())["scenariodata_agg_json_1"]

    return jsonify({**base_options, **response})


@application.route("/api/line_chart", methods=["GET", "POST"])
def line_chart():
    """** WIP ** The line_chart is a timeseries chart. Reads from database series data and period names
    Inputs: scenario, area, solution
    """

    inputs = request.json

    scenario = inputs["scenario"]
    area = inputs["area"].replace(" ", "")
    formatted_area = area[0].lower() + area[1:]
    solution = inputs["solution"]

    # query series for line chart
    query = select(
        func.wl.scenariodata_per_date_total_json(formatted_area, scenario, solution)
    )
    result = connection.execute(query).fetchone()

    # Get base options for the line chart
    with open("echarts-templates/line-chart.json", "r") as f:
        base_options = json.load(f)

    response = dict(result.items())["scenariodata_per_date_total_json_1"]

    return jsonify({**base_options, **response})
    # return jsonify(response)
