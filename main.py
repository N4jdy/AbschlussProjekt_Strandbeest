import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from funktionen import laenge_berechnung, bestimmung_radius, fehler_funktion
from ui import erstellung_seite
import time


def ui():
    erstellung_seite()


def mechanism():
    # Startvektor
    x_vec  = np.array([0, 0, 10, 35, -25.0, 10.0])
    radius = bestimmung_radius(-25.0, 10.0, -30.0, 0.0)
    winkel_anf = np.arctan(2)

    # Zum Überprüfen:
    #winkel = winkel_anf + np.deg2rad(10)
    #laenge_berechnung(x_vec, winkel_anf, winkel, radius)
    #fehler_funktion(x_vec, winkel_anf, winkel, radius)

    # Schleife für konstanten Drehwinkel
    animated = False
    if animated:
        for winkel in np.linspace(0, 2*np.pi, 360):  # 1°-Schritte
            laenge_berechnung(x_vec, winkel_anf, winkel, radius)
            time.sleep(2)


if __name__ == "__main__":
    #ui()
    mechanism()