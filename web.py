import sys, os
import logging
C = os.path.abspath(os.path.dirname(__file__))
sys.path.append(C)

logging.basicConfig(filename=os.path.join(C, "run_server.log"), level=logging.INFO, format="%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")

from datetime import datetime
import json
import yaml
import threading

from bottle import run, template, Bottle, route, response, Response
from bottle import jinja2_view
import bottle

from main import main as register_temperature
from main import monitor_temperature
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
@temperature.route("/<days:float>")
def index(days=3):
    with open(os.path.join(C, "capteurs.yaml"), "r") as f_in:
        capteurs_connus = yaml.safe_load(f_in.read())
    capteurs = []
    for file in os.listdir(C):
        if "28" in file:
            name = file[:-8]
            capteurs.append({"name": capteurs_connus.get(name, name),
                             "data": get_history(file, int(days*24*60))})
    fig, ax = plt.subplots()

    for capteur in capteurs:
        ax.plot(*prepare_for_plot(capteur), label=capteur["name"])
    ax.legend()
    return mpld3.fig_to_html(fig)


def prepare_for_plot(capteur):
    a, b = [], []
    for data in capteur["data"]:
        a.append(datetime.strptime(data[0], '%d/%m/%Y %H:%M:%S'))
        b.append(data[1])
    return np.array(a), np.array(b)

def get_history(capteur, n_data=60*24*3):
    with open(f"{os.path.join(C, capteur)}", "r") as f_in:
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
    [{nom_du_capteur:???temperature}, ..]
    """
    with open(os.path.join(C, "capteurs.yaml"), "r") as f_in:
        capteurs_connus = yaml.safe_load(f_in.read())
    capteurs = dict()
    for capteur in os.listdir(routes_capteurs):
        if "28" in capteur:
            capteurs[capteur] = {"name": capteurs_connus.get(capteur, "inconnu"),
                            "temperature": extraire_temperature(lire_fichier(os.path.join(routes_capteurs, capteur, "w1_slave")))}

    response.content_type = "application/json"
    response.set_header('Access-Control-Allow-Origin', '*')
    return capteurs


threading.Thread(target=register_temperature).start()
threading.Thread(target=monitor_temperature).start()

temperature.run(host="0.0.0.0", port=8081)