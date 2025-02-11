import streamlit as st
import numpy as np
from funktionen import laenge_glieder_berechnung, write_csv_file, plot_csv
from ui import css, create_animation
from klassen import Punkt
from scipy.optimize import least_squares
import scipy.signal

# Mechanismus-Berechnung mit stabilisierter Least Squares Methode
def mechanism():
    # Startvektor
    p0 = Punkt(0.0, 0.0, True)  # Startpunkt
    p1 = Punkt(10.0, 35.0)  # Initialwerte für p1
    p2 = Punkt(-25.0, 10.0)  # Initialwerte für p2
    c = Punkt(-30.0, 0.0, True, True)  # Mittelpunkt der Kreisbahn
    radius = p2.distanz_zu(c)
    winkel_anf = c.winkel_zu(p2)
    
    # Berechnung der ursprünglichen Stablängen
    l1 = p1.distanz_zu(p0)
    l2 = p2.distanz_zu(p1)
    
    optimierte_p1 = []
    optimierte_p2 = []
    winkel_schritte = np.arange(0, 361, 7)  # 7-Grad-Schritte
    vorheriges_p1 = p1.get_coordinates()

    def fehler_funktion(p1_var, winkel, p2_var, vorheriges_p1):
        fehler = laenge_glieder_berechnung(np.hstack((p0.get_coordinates(), p1_var, p2_var)), winkel_anf, winkel, radius, rueckgabe=0)
        l1_neu = np.linalg.norm(p1_var - p0.get_coordinates())
        l2_neu = np.linalg.norm(p2_var - p1_var)
        positionsänderung = np.linalg.norm(p1_var - vorheriges_p1)**2  # Strafterm für abrupte Änderungen
        return np.sum(fehler**2) + (l1_neu - l1)**2 + (l2_neu - l2)**2 + 0.5 * positionsänderung
    
    for winkel in winkel_schritte:
        winkel_rad = winkel_anf + np.deg2rad(winkel)
        
        # p2 bewegt sich entlang der Kreisbahn
        p2_x = c.x + radius * np.cos(winkel_rad)
        p2_y = c.y + radius * np.sin(winkel_rad)
        p2_neu = np.array([p2_x, p2_y])
        
        # Stabilisierte Least Squares Optimierung
        bounds = ([vorheriges_p1[0] - 5, vorheriges_p1[1] - 5], [vorheriges_p1[0] + 5, vorheriges_p1[1] + 5])  # Verhindert zu große Sprünge
        result = least_squares(fehler_funktion, vorheriges_p1, args=(winkel_rad, p2_neu, vorheriges_p1), bounds=bounds)
        p1_opti = result.x
        
        optimierte_p1.append(p1_opti)
        optimierte_p2.append(p2_neu)
        vorheriges_p1 = p1_opti.copy()
        
        #print(f"Winkel: {winkel}° ->  Optimierte p1: {p1_opti}")
    
    # Sanfte Glättung der Ergebnisse
    optimierte_p1 = scipy.signal.savgol_filter(np.array(optimierte_p1), 15, 3, axis=0)

    # csv erstellen
    Bahnkurve = np.array([optimierte_p1, optimierte_p2])
    write_csv_file(Bahnkurve, "Bahnkurve.csv")
    # csv plotten
    plot_csv("Bahnkurve.csv")

    return p0, optimierte_p1, optimierte_p2, c, radius, winkel_anf



# Hauptprogramm
p0, p1_opti_list, p2_opti_list, c, radius, winkel_anf = mechanism()

# Erstellen Seite
st.set_page_config(layout="wide")
css()
col = st.columns([1, 1])

with col[0]:
    st.header("Eingabe der Parameter", divider="red")
    st.subheader("Punkte")
    option = st.selectbox(
        "Punkt auswählen",
        ("p0", "p1", "p2", "c"),
        index=None,
        placeholder="Wähle eienen Punkt aus...",
    )
    st.number_input("x-Achse")
    st.number_input("y-Achse")
    st.button("Absenden")
    st.write(f"Radius =", radius)

    st.subheader("Stangen")


with col[1]:
    st.header("Visualisierung", divider="gray")
    ani = create_animation(p0, p1_opti_list, p2_opti_list, c, radius, winkel_anf)

    # Temporäre Datei speichern
    output_file = "viergelenkkette_animation.gif"
    ani.save(output_file, writer="imagemagick", fps=10)

    # Optimierte Parameter anzeigen
    #st.write(f"Optimierte Koordinaten für p1: {p1_opti_list}")

    # Animation anzeigen
    st.image(output_file, caption="Animation der Viergelenkkette mit optimierten Parametern")
