import glob
import time
import datetime


def lire_fichier (emplacement) :
    fichier = open(emplacement)
    contenu = fichier.read()
    fichier.close()
    return contenu


def extraire_temperature (contenu) :
    seconde_ligne = contenu.split("\n")[1]
    donnees_temperature = seconde_ligne.split(" ")[9]
    return float(donnees_temperature[2:]) / 1000


def sauvegarde(temperature, date, emplacement):
    fichier_cible = open(emplacement, "a")
    fichier_cible.write(str(date) + "   ")
    fichier_cible.write(str(temperature) + '\r\n')
    fichier_cible.close()


def main():
    routes_capteurs = glob.glob("/sys/bus/w1/devices/28*/w1_slave")
    capteurs_name = ["Capteur1", "Capteur2"]


    if len(routes_capteurs) > 0 :
        while True:
            date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            for capteur, name in zip(routes_capteurs, capteurs_name):
                contenu_fichier = lire_fichier(capteur)
                temperature = extraire_temperature(contenu_fichier)
                sauvegarde(temperature, date, name)
            time.sleep(60)

    else :
        print("Sonde non détectee. Vérifier le branchement, ou rendez-vous dans la section montrant une solution possible")