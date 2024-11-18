import math
import random
import json
import pandas as pd

from flask import Flask, jsonify, request

from flask_cors import CORS

from main import musee_clusters

app = Flask(import_name=__name__)
CORS(app)

scene = set()

def couleur(r, v, b):
    return {"r": r, "v": v, "b": b}


# =============================================================================================
# La base de données Musée
# =============================================================================================


class Tableau:
    def __init__(self, prefixe, valeur):
        self.cle = valeur['id']
        self.peintre = valeur['peintre']
        self.nom = valeur['nom']
        self.annee = valeur['date']
        self.hauteur = valeur['longueur']
        self.largeur = valeur['largeur']
        # self.tags = valeur[6]
        self.url = prefixe + self.cle + ".jpg"


# =============================================================================================
# Représentation 3d
# =============================================================================================


class Acteur:
    def __init__(self, nom, leType):
        self.json = {"op": "CREATE", "id": nom, "type": leType, "components": []}

    def add(self, comp):
        self.json["components"].append(comp)
        return self

    def addS(self, to_add):
        self.json["components"] = self.json["components"] + to_add
        return self

    def toJSON(self):
        return self.json


class Scene:
    def __init__(self):
        self.scene = {}  # contient tous les acteurs
        self.assets = {}

    def actors(self):
        return list(self.scene.keys())

    def actor(self, nom, leType):
        a = Acteur(nom, leType)
        self.scene[nom] = a
        return a

    def getActor(self, nom):
        return self.scene[nom]

    def jsonify(self):
        acteurs = list(self.scene.values())
        return [x.toJSON() for x in acteurs]


# Les incarnations
# ================


def poster(nom, largeur, hauteur, url):
    return {
        "type": "poster",
        "data": {"name": nom, "largeur": largeur, "hauteur": hauteur, "tableau": url},
    }


def sphere(nom, diametre, materiau):
    return {
        "type": "sphere",
        "data": {"name": nom, "diameter": diametre, "material": materiau},
    }


def box(nom, largeur, hauteur, epaisseur, materiau):
    return {
        "type": "box",
        "data": {
            "name": nom,
            "width": largeur,
            "height": hauteur,
            "depth": epaisseur,
            "material": materiau,
        },
    }


def wall(nom, largeur, hauteur, epaisseur, materiau):
    return {
        "type": "wall",
        "data": {
            "name": nom,
            "width": largeur,
            "height": hauteur,
            "depth": epaisseur,
            "material": materiau,
        },
    }


def porte(nom, largeur, hauteur, epaisseur):
    return {
        "type": "porte",
        "data": {"name": nom, "width": largeur, "height": hauteur, "depth": epaisseur},
    }


def title(nom, titre):
    return {"type": "titre", "data": {"name": nom, "titre": titre}}


# Le graphe de scène
# ==================


def position(x, y, z):
    return {"type": "position", "data": {"x": x, "y": y, "z": z}}


def rotation(x, y, z):
    return {"type": "rotation", "data": {"x": x, "y": y, "z": z}}


def anchoredTo(parent):
    return {"type": "anchoredTo", "data": {"parent": parent}}


# ===========================================================================


def rejectedByAll(d):
    return {"type": "repulsion", "data": {"range": d}}


def friction(k):
    return {"type": "frottement", "data": {"k": k}}


def attractedBy(acteur):
    return {"type": "attraction", "data": {"attractedBy": acteur}}


# ===========================================================================


@app.route("/assets")
def assets():
    materiaux = {}

    materiaux["rouge"] = {"color": [1, 0, 0]}
    materiaux["vert"] = {"color": [0, 1, 0]}
    materiaux["bleu"] = {"color": [0, 0, 1]}
    materiaux["blanc"] = {
        "color": [1, 1, 1],
        "texture": "./assets/textures/murs/dante.jpg",
        "uScale": 1,
        "vScale": 1,
    }
    materiaux["murBriques"] = {
        "color": [1, 1, 1],
        "texture": "./assets/textures/murs/briques.jpg",
        "uScale": 2,
        "vScale": 1,
    }
    materiaux["murBleu"] = {
        "color": [1, 1, 1],
        "texture": "./assets/textures/murs/bleuCanard.jpg",
        "uScale": 2,
        "vScale": 1,
    }
    materiaux["parquet"] = {
        "color": [1, 1, 1],
        "texture": "./assets/textures/sol/parquet.jpg",
        "uScale": 2,
        "vScale": 2,
    }

    print(">>> ASSETS OK")

    return jsonify(materiaux)



tableaux_data = []

@app.route("/init")
def init():

    scene = Scene()
    prefixe = "../client/assets/expo_kg/"

    df = pd.read_csv("tableaux.csv")
    for _, row in df.iterrows():
        tableaux_data.append(Tableau(prefixe, row))

    print(tableaux_data)
    dx = 10
    dz = 10

    scene.actor("toit", "actor").add(box("toit", 50, 0.1, 50, "blanc")).add(
        position(25, 3, 25)
    )

    for i in range(0, 5):
        for j in range(0, 5):
            x = i * dx
            z = j * dz
            suffixe = str(i) + "-" + str(j)
            nomSalle = "salle-" + suffixe
            scene.actor(nomSalle, "actor").add(sphere(nomSalle, 0.2, "vert")).add(
                position(x, 0, z)
            )
            nomMurH = "H-" + suffixe
            scene.actor(nomMurH, "actor").add(wall(nomMurH, 8, 3, 0.1, "murBleu")).add(
                position(i * dx + dx / 2, 0, j * dz + dz / 2)
            )
            nomMurV = "V-" + suffixe
            scene.actor(nomMurV, "actor").add(wall(nomMurV, 8, 3, 0.1, "murBleu")).add(
                position(i * dx + dx / 2, 0, j * dz + dz / 2)
            ).add(rotation(0, math.pi / 2, 0))


    print(scene.actors())
    return jsonify(scene.jsonify())


@app.route("/salle/")
def onSalle():

    i = request.args.get("I", default=0, type=int)
    j = request.args.get("J", default=0, type=int)
    print("CHANGEMENT DE SALLE : i=", i, " - j=", j)

    scene = Scene()

    walls = [
        [-3, 1.5, 4.8, 0],
        [3, 1.5, 4.8, 0],
        [4.8, 1.5, 3, math.pi / 2],
        [4.8, 1.5, -3, math.pi / 2],
        [3, 1.5, -4.8, math.pi],
        [-3, 1.5, -4.8, math.pi],
        [-4.8, 1.5, -3, -math.pi / 2],
        [-4.8, 1.5, 3, -math.pi / 2],
    ]

    if(musee_clusters != []):
        tableau_a_afficher = None
        print("Cluster actuel : ", musee_clusters[0])
        for e in musee_clusters[0]:
            for tableau in tableaux_data:
                if tableau.cle == e :
                    tableau_a_afficher = tableau
                    break

            mur = walls.pop(random.randrange(len(walls)))
            scene.actor(tableau.cle, "actor").add(
                poster(
                    tableau.cle,
                    tableau.largeur / 100,
                    tableau.hauteur / 100,
                    tableau.url,
                )
            ).add(anchoredTo("salle-" + str(i) + "-" + str(j))).add(
                position(mur[0], mur[1], mur[2])
            ).add(rotation(0, mur[3], 0))
            print("Tableau affiché : ",tableau.cle)
        
        musee_clusters.pop(0)

    return jsonify(scene.jsonify())

if __name__ == "__main__":
    app.run(debug=True)
