import streamlit as st
import numpy as np
from funktionen import laenge_glieder_berechnung, bestimmung_radius, fehler_funktion, plot_koord_kr_bewegung, bestimmung_anfangswinkel
from ui import erstellung_seite
import time


def ui():
    erstellung_seite()


def mechanism():
    # Startvektor
    p0 = np.array([0.0, 0.0])
    p1 = np.array([10.0, 35.0])
    p2 = np.array([-25.0, 10.0])
    c = np.array([-30.0, 0.0])
    x_vec = np.array([p0[0], p0[1], p1[0], p1[1], p2[0], p2[1]])  
    radius = bestimmung_radius(c[0], c[1], p2[0], p2[1])
    winkel_anf = bestimmung_anfangswinkel(c[0], c[1], p2[0], p2[1])

    # Zum Überprüfen:
    #winkel_anf = np.arctan(2)
    #winkel = winkel_anf + np.deg2rad(10)
    #laenge_glieder_berechnung(x_vec, winkel_anf, winkel, radius)
    #fehler_funktion(x_vec, winkel_anf, winkel, radius)

    # Liste zum Speichern der Werte für Plot Überprüfung Bewegung
    bewegung_p2_x = []
    bewegung_p2_y = []
    fehler_x = []
    fehler_y = []

    # Schleife für konstanten Drehwinkel
    animated = True
    if animated:
        for winkel_rot in np.linspace(0, 2*np.pi, 60):  # 1°-Schritte
            #time.sleep(1)
            winkel = winkel_anf + winkel_rot
            if winkel > 2*np.pi:
                winkel = winkel - 2*np.pi
            #print(f"Winkel: {np.rad2deg(winkel)}")
            fehler = fehler_funktion(x_vec, winkel_anf, winkel, radius)
            fehler_x.append(fehler[2])
            fehler_y.append(fehler[3])
            #print(fehler_funktion(x_vec, winkel_anf, winkel, radius))            

            # Zum Überprüfen Kreisbewegung:
            '''koord_kr_bewegung = laenge_glieder_berechnung(x_vec, winkel_anf, winkel, radius, True)
            # True damit Koordinaten der Bewegung von p2 zurückgegeben werden
            bewegung_p2_x.append(koord_kr_bewegung[4])
            bewegung_p2_y.append(koord_kr_bewegung[5])
    
    plot_koord_kr_bewegung(bewegung_p2_x, bewegung_p2_y, 1)'''
    #plot_koord_kr_bewegung(fehler_x, fehler_y, 2)


if __name__ == "__main__":
    #ui()
    mechanism()