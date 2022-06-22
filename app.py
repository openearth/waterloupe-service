# FLASK
from flask import Flask, jsonify, request
from pathlib import Path
import sqlalchemy
from sqlalchemy import column, func, select

from utils import establish_db_connection

application = Flask(__name__)


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


@application.route("/api/stacked_column_chart", methods=["GET", "POST"])
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

    response = dict(result.items())[
        "scenariodata_agg_json_1"
    ]  # TODO: see what the scenario_data_agg_json_1 stands for in the response

    # query period names
    query = select([period.columns.period_name])
    result = connection.execute(query).fetchall()
    labels = [r for r, in result]

    response["labels"] = labels
    return jsonify(response)
