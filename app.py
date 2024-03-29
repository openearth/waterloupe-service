# FLASK
from flask import Flask, jsonify, request
from pathlib import Path
import sqlalchemy
from sqlalchemy import column, func, select, event


# from flask_cors import CORS  # only for development
from utils import establish_db_connection
import json

import logging

application = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s : %(message)s')

# CORS(application)  # only for development
service_path = Path(__file__).resolve().parent
conf_file = service_path / "configuration.txt"


@application.route("/")
def hello_world():
    return "Waterloupe api"


@application.route("/api/bar_chart", methods=["GET", "POST"])
def bar_chart():
    """The bar_chart is a stacked bar chart. Reads from database series data and period names
    Inputs: case, scenario, area, solution
    """

    inputs = request.json

    scenario = inputs["scenario"]
    area_id = inputs["area"]
    solution = inputs["solution"]
    db_schema = inputs["case"]


    query = f"select * from {db_schema}.scenariodata_agg_json({area_id}, '{scenario}','{solution}');"

    engine, connection = establish_db_connection()

    with connection as con:
        response = con.execute(query).fetchone()[0]


    # Get base options for the bar chart
    with open("echarts-templates/bar-chart.json", "r") as f:
        base_options = json.load(f)

    for key in base_options:
        response[key] = {**response.get(key, {}), **base_options[key]}

    return jsonify(response)


@application.route("/api/line_chart", methods=["GET", "POST"])
def line_chart():

    """The line_chart is a timeseries chart. Reads from database series data and period names
    Inputs: case, scenario, area, solution
    """

    inputs = request.json

    scenario = inputs["scenario"]
    area_id = inputs["area"]
    solution = inputs["solution"]
    db_schema = inputs["case"]


    query = f"select * from {db_schema}.scenariodata_per_date_total_json({area_id}, '{scenario}','{solution}');"
    engine, connection = establish_db_connection()

    with connection as con:
        response = con.execute(query).fetchone()[0]

    # Get base options for the line chart
    with open("echarts-templates/line-chart.json", "r") as f:
        base_options = json.load(f)
    for key in base_options:
        response[key] = {**response.get(key, {}), **base_options[key]}

    return jsonify(response)

@application.route("/api/maps", methods=["GET", "POST"])
def maps():

    """The risk_maps returns a geojson with the risk map.
    Inputs: case, scenario, period_id, solution, users
    """

    inputs = request.json

    scenario = inputs["scenario"]
    period_id = inputs["period_id"]
    solution = inputs["solution"]
    db_schema = inputs["case"]
    users = inputs["users"]
    map_type = inputs["map_type"]

    query = f"select * from {db_schema}.all_data_geojson('{map_type}', {period_id}, '{scenario}','{solution}', '{users}');"
    engine, connection = establish_db_connection()

    with connection as con:
        response = con.execute(query).fetchone()[0]

    return jsonify(response)



@application.route("/api/solutions_scenarios/<case>", methods=["GET", "POST"])
def solutions_scenarios(case):

    engine, connection = establish_db_connection()
    query_scenarios = f"select * from {case}.list_scenario;"
    query_solutions =  f"select * from {case}.list_solution;"

    with connection as con:
        scenarios_response = con.execute(query_scenarios).fetchall()
        solutions_response = con.execute(query_solutions).fetchall()
    scenarios = [scenario[0] for scenario in scenarios_response]
    solutions= [solution[0] for solution in solutions_response]
    response = {
        "solutions": solutions,
        "scenarios": scenarios
    }

    return jsonify(response)

@application.route("/api/users_periods/<case>", methods=["GET", "POST"])
def users_periods(case):

    engine, connection = establish_db_connection()
    query_users = f"select * from {case}.list_users;"
    query_periods =  f"select period_name, period_id from {case}.period;"

    with connection as con:
        users_response = con.execute(query_users).fetchall()
        periods_response = con.execute(query_periods).fetchall()

    users = [user[0] for user in users_response]
    if ('none' in users): #TODO: HORRIBLE, sometimes none, sometimes None.
      users.remove('none') #TODO: find a solution in the database side
    periods = []
    for period in periods_response:
        period_info = {
            "period_name": period[0],
            "period_id": period[1]
        }
        periods.append(period_info)



    response = {
        "users": users,
        "periods": periods
    }

    return jsonify(response)


@application.route("/api/parameters/<case>", methods=["GET", "POST"])
def scenarios(case):

    engine, connection = establish_db_connection()
    query = f"select * from {case}.list_parameter;"

    with connection as con:
        query_response = con.execute(query).fetchall()

    parameters = [parameter[0] for parameter in query_response]
    response = {
        "parameters" : parameters
    }
    return jsonify(parameters)


@application.route("/api/areas/<case>", methods=["GET", "POST"])
def areas(case):

    engine, connection = establish_db_connection()

    query =  f"select name, area_id from {case}.area;"

    with connection as con:
        query_response = con.execute(query).fetchall()


    areas = []
    for area in query_response:
        area_info = {
            "area_name": area[0],
            "area_id": area[1]
        }
        areas.append(area_info)

    response = {
        "areas": areas
    }
    return jsonify(response)
