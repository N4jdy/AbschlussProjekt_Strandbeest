import streamlit as st
import csv
import math
import matplotlib.pyplot as plt
import numpy as np

from klassen import Mechanism
from ui import css, create_animation, punkte_darstellen, neuer_punkt_hinzufügen, stangen_darstellen, stangen_verwalten
from zusatz_funktionen import write_csv_file, plot_csv
from db_connector import DatabaseConnector

def load_database():
    """
    Lädt alle relevanten Daten aus database.json
    """
    db = DatabaseConnector()
    return {
        "points": db.get_table("points").all(), 
        "links": db.get_table("links").all()  
    }

def validate_mechanism(pivot_name, driver_name):
    
    db_data = load_database()
    point_names = [p["name"] for p in db_data["points"]]
    link_points = [(l["start"], l["end"]) for l in db_data["links"]]

    # Prüfen, ob Pivot und Driver existieren
    if pivot_name not in point_names or driver_name not in point_names:
        return False, "Pivot oder Driver Punkt existiert nicht!"
    
    if pivot_name == driver_name:
        return False, "Pivot und Driver Punkt sind identisch"

    # Prüfen, ob der Driver mit dem Pivot verbunden ist
    connected = any((pivot_name in link and driver_name in link) for link in link_points)
    if not connected:
        return False, "Driver ist nicht direkt mit dem Pivot oder über eine Kette verbunden!"
    
    # Prüfen, ob alle Verbindungen sinnvoll sind
    for link in link_points:
        start, end = link
        if start == end:
            return False, f"Ungültige Verbindung: Punkt {start} ist mit sich selbst verbunden!"
        if start not in point_names or end not in point_names:
            return False, f"Ungültige Verbindung: Einer der Punkte ({start}, {end}) existiert nicht!"
    
    return True, "Mechanismus ist valide."



def main(pivot_name, driver_name):
    """
    Hauptprogramm: Lädt Daten, erstellt die Mechanism-Simulation und erstellt die Animation.
    """
    # Lade alle Tabellen aus der Datenbank
    db_data = load_database()

    # Mechanismus mit den gewählten Punkten initialisieren
    mech = Mechanism(pivot_name, driver_name)
    mech.run_simulation()

    all_steps_list = mech.get_history()
    all_steps = np.array(all_steps_list)

    point_names_sorted = sorted([p["name"] for p in db_data["points"]])
    point_index_map = {name: i for i, name in enumerate(point_names_sorted)}

    links = db_data["links"]

    # Kreisbahn-Daten aus Mechanism abrufen
    if mech.drivers_config:
        circle_center = mech.drivers_config[0]["center"]
        circle_radius = mech.drivers_config[0]["radius"]
    else:
        circle_center, circle_radius = None, None

    # Animation erstellen
    ani = create_animation(
        all_steps=all_steps,
        links=links,
        point_index_map=point_index_map,
        radius=circle_radius,
        circle_center=circle_center,
        xlim=(-150, 50),
        ylim=(-150, 50)
    )

    output_file = "Visualisierung_Daten/mehrgelenk_animation.gif"
    ani.save(output_file, writer="imagemagick", fps=10)
    
    write_csv_file(all_steps, point_names_sorted, "Visualisierung_Daten/sim_output.csv")
    plot_csv("Visualisierung_Daten/sim_output.csv")

if __name__ == "__main__":
    # Erstellen Seite
    st.set_page_config(layout="wide")
    css()
    col = st.columns([1, 1])

    with col[0]:
        st.header("Eingabe der Parameter", divider="red")
        punkte_darstellen()
        neuer_punkt_hinzufügen()

        st.subheader("Mechanismus Einstellungen")
        punkt_namen = [p["name"] for p in load_database()["points"]]
        pivot_name = st.selectbox("Pivot Punkt wählen", punkt_namen, index=0)
        driver_name = st.selectbox("Driver Punkt wählen", punkt_namen, index=1)

        stangen_darstellen()
        stangen_verwalten()

        

        st.subheader("Valid-Check ✅") 

        if st.button("Mechanismus überprüfen"):
            is_valid, message = validate_mechanism(pivot_name, driver_name)
            if is_valid:
                st.success(message)
            else:
                st.error(message)

    with col[1]:
        st.header("Visualisierung", divider="gray")
        if st.button("Berechnung starten"):
            is_valid, message = validate_mechanism(pivot_name, driver_name)
            if is_valid:
                main(pivot_name, driver_name)
                output_file = "Visualisierung_Daten/mehrgelenk_animation.gif"
                st.image(output_file, caption="Animation der Mehrgelenkkette mit mehreren Treibern")

                path_curve_file = "Visualisierung_Daten/bahnkurve.png"
                st.image(path_curve_file, caption="Bahnkurve des Mechanismus")
            else:
                st.error("Simulation kann nicht gestartet werden: " + message)
