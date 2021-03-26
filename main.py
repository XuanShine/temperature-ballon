import sys, os
import logging
C = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(filename=os.path.join(C, "run_server.log"), level=logging.INFO, format="%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")


import glob
import time
import datetime

import yaml


def lire_fichier(emplacement) :
    fichier = open(emplacement)
    contenu = fichier.read()
    fichier.close()
    return contenu


def extraire_temperature(contenu) :
    seconde_ligne = contenu.split("\n")[1]
    donnees_temperature = seconde_ligne.split(" ")[9]
    return float(donnees_temperature[2:]) / 1000


def sauvegarde(temperature, date, emplacement):
    with open(emplacement, "a") as fichier_cible:
        fichier_cible.write(str(date) + "   ")
        fichier_cible.write(str(temperature) + '\r\n')


def main():
    # routes_capteurs = glob.glob("/sys/bus/w1/devices/28*/w1_slave")
    # capteurs_name = ["Capteur1", "Capteur2"]

    routes_capteurs = "/sys/bus/w1/devices/"

    with open("capteurs.yaml", "r") as f_in:
        capteurs_connus = yaml.load(f_in)  # {<id_capteur>: <name_capteur>, ...}

    capteurs_presents = {capteur for capteur in os.listdir(routes_capteurs) if capteur.startswith("28")}
    capteurs_inconnus = capteurs_presents - capteurs_connus.keys()
    capteurs_absents = capteurs_connus.keys() - capteurs_presents

    logging.info(f"Capteurs Présents: {capteurs_presents}\nCapteursConnus: {capteurs_connus}\nCapteurs Inconnus: {capteurs_inconnus}\nCapteurs Absents: {capteurs_absents}")


    if len(routes_capteurs) > 0 :
        while True:
            date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            for capteur in capteurs_presents:
                contenu_fichier = lire_fichier(os.path.join(routes_capteurs, capteur, "w1_slave"))
                temperature = extraire_temperature(contenu_fichier)
                sauvegarde(temperature, date, os.path.join(C, capteur) + ".templog")
            time.sleep(60)
    else :
        print("Sonde non détectee. Vérifier le branchement, ou rendez-vous dans la section montrant une solution possible")