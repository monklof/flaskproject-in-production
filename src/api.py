# coding: utf-8
"""api logic"""
from flask import Blueprint
from base import send_success

api = Blueprint("api", __name__)

@api.route("/ping")
def ping():
    return send_success("pong")


