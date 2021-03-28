import sys, os
import logging
C = os.path.abspath(os.path.dirname(__file__))
sys.path.append(C)

logging.basicConfig(filename=os.path.join(C, "run_server.log"), level=logging.INFO, format="%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")

from datetime import datetime
import json
import yaml

from bottle import run, template, Bottle, route, response, Response
from bottle import jinja2_view
import bottle

from main import main as register_temperature
from main import extraire_temperature, lire_fichier, routes_capteurs
import matplotlib.pyplot as plt, mpld3
import numpy as np



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
    with open("capteurs.yaml", "r") as f_in:
        capteurs_connus = yaml.safe_load(f_in.read())
    capteurs = []
    for file in os.listdir(C):
        if "28" in file:
            name = file[:-8]
            capteurs.append({"name": capteurs_connus.get(name, name),
                             "data": get_history(file)})
    a, b = [], []
    for data in capteurs[0]["data"]:
        a.append(datetime.strptime(data[0], '%d/%m/%Y %H:%M:%S'))
        b.append(data[1])


    a = np.array(a, dtype='datetime64')
    b = np.array(b)
    plt.plot(a, b)
    plt.show()


def get_history(capteur, n_data=60*24*7):
    with open(f"{capteur}", "r") as f_in:
        data = f_in.readlines()
    # data = [tuple(info.strip().split("   ")) for info in data]
    data = list(map(lambda x: (x[0], float(x[1])),
                map(lambda x: x.strip().split("   "),
                data)))
    if len(data) <= n_data:
        return data
    else:
        return data[len(data) - n_data:]


@temperature.route("/get_temperature")
def get_temperature():
    """Retourne les valeurs en JSON:
    [{nom_du_capteur: temperature}, ..]
    """
    with open("capteurs.yaml", "r") as f_in:
        capteurs_connus = yaml.safe_load(f_in.read())
    capteurs = []
    for file in os.listdir(C):
        if "28" in file:
            capteurs.append({"name": capteurs_connus.get(file, "inconnu"),
                             "id": file,
                             "temperature": extraire_temperature(lire_fichier(os.path.join(routes_capteurs, file)))})