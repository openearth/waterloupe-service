# FLASK
from flask import Flask, jsonify, request

application = Flask(__name__)


@application.route("/")
def hello_world():
    return "Hellow, World"
