import sys, os
import logging
C = os.path.abspath(os.path.dirname(__file__))
sys.path.append(C)

logging.basicConfig(filename=os.path.join(C, "run_server.log"), level=logging.INFO, format="%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")

from datetime import datetime
import json

from bottle import run, template, Bottle, route, response, Response
from bottle import jinja2_view
import bottle

from main import main as register_temperature

import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

temperature = Bottle()
bottle.TEMPLATE_PATH.insert(0, os.path.join(C, 'views'))

@temperature.route("/")
def index():
    result = ""
    for file in os.listdir(C):
        if file.startswith("Capteur"):
            with open(file, "r") as f_in:
                result += f"{file} :\n {f_in.read()}\n{'=' * 50}\n"
    return result.replace("\n", "<br>")


@temperature.route("/get_temperature")
def get_temperature():
    return "TODO"