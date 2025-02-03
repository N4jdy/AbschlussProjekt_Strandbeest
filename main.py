import streamlit as st
import numpy as np
from funktionen import laenge_glieder_berechnung, bestimmung_radius, bestimmung_anfangswinkel
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.optimize import least_squares
import scipy.signal

# Mechanismus-Berechnung mit stabilisierter Least Squares Methode
def mechanism():
    # Startvektor
    p0 = np.array([0.0, 0.0])
    p1 = np.array([10.0, 35.0])  # Initialwerte für p1
    p2 = np.array([-25.0, 10.0])  # Initialwerte für p2
    c = np.array([-30.0, 0.0])  # Mittelpunkt der Kreisbahn
    radius = bestimmung_radius(c[0], c[1], p2[0], p2[1])
    winkel_anf = bestimmung_anfangswinkel(c[0], c[1], p2[0], p2[1])
    
    # Berechnung der ursprünglichen Stablängen
    l1 = np.linalg.norm(p1 - p0)
    l2 = np.linalg.norm(p2 - p1)
    
    optimierte_p1 = []
    optimierte_p2 = []
    winkel_schritte = np.arange(0, 361, 1)  # 1-Grad-Schritte
    vorheriges_p1 = p1.copy()
    
    def fehler_funktion(p1_var, winkel, p2_var, vorheriges_p1):
        fehler = laenge_glieder_berechnung(np.hstack((p0, p1_var, p2_var)), winkel_anf, winkel, radius, rueckgabe=0)
        l1_neu = np.linalg.norm(p1_var - p0)
        l2_neu = np.linalg.norm(p2_var - p1_var)
        positionsänderung = np.linalg.norm(p1_var - vorheriges_p1)**2  # Strafterm für abrupte Änderungen
        return np.sum(fehler**2) + (l1_neu - l1)**2 + (l2_neu - l2)**2 + 0.5 * positionsänderung
    
    for winkel in winkel_schritte:
        winkel_rad = winkel_anf + np.deg2rad(winkel)
        
        # p2 bewegt sich entlang der Kreisbahn
        p2_x = c[0] + radius * np.cos(winkel_rad)
        p2_y = c[1] + radius * np.sin(winkel_rad)
        p2_neu = np.array([p2_x, p2_y])
        
        # Stabilisierte Least Squares Optimierung
        bounds = ([vorheriges_p1[0] - 5, vorheriges_p1[1] - 5], [vorheriges_p1[0] + 5, vorheriges_p1[1] + 5])  # Verhindert zu große Sprünge
        result = least_squares(fehler_funktion, vorheriges_p1, args=(winkel_rad, p2_neu, vorheriges_p1), bounds=bounds)
        p1_opti = result.x
        
        optimierte_p1.append(p1_opti)
        optimierte_p2.append(p2_neu)
        vorheriges_p1 = p1_opti.copy()
        
        print(f"Winkel: {winkel}° ->  Optimierte p1: {p1_opti}")
    
    # Sanfte Glättung der Ergebnisse
    optimierte_p1 = scipy.signal.savgol_filter(np.array(optimierte_p1), 15, 3, axis=0)
    return p0, optimierte_p1, optimierte_p2, c, radius, winkel_anf

# Animation erstellen
def create_animation(p0, p1_list, p2_list, c, radius, winkel_anf):
    fig, ax = plt.subplots()
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    ax.set_title("Bewegung der Viergelenkkette")
    ax.set_aspect('equal')
    
    line1, = ax.plot([], [], 'ro-', lw=2, label="Link 1")
    line2, = ax.plot([], [], 'bo-', lw=2, label="Link 2")
    circle = plt.Circle((c[0], c[1]), radius, color='r', fill=False)
    ax.add_artist(circle)
    ax.legend()
    
    def update(frame):
        p1 = p1_list[frame]
        p2 = p2_list[frame]
        line1.set_data([p0[0], p1[0]], [p0[1], p1[1]])
        line2.set_data([p1[0], p2[0]], [p1[1], p2[1]])
        return line1, line2
    
    ani = FuncAnimation(fig, update, frames=len(p1_list), interval=100)
    return ani

# Hauptprogramm
st.title("Visualisierung der Viergelenkkette mit optimierten Parametern")
p0, p1_opti_list, p2_opti_list, c, radius, winkel_anf = mechanism()
ani = create_animation(p0, p1_opti_list, p2_opti_list, c, radius, winkel_anf)

# Temporäre Datei speichern
output_file = "viergelenkkette_animation.gif"
ani.save(output_file, writer="imagemagick", fps=10)

# Optimierte Parameter anzeigen
st.write(f"Optimierte Koordinaten für p1: {p1_opti_list}")

# Animation anzeigen
st.image(output_file, caption="Animation der Viergelenkkette mit optimierten Parametern")
