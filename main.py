import streamlit as st
import csv
import math
import matplotlib.pyplot as plt
import numpy as np

from klassen import Mechanism
from ui import css, create_animation, punkte_darstellen, neuer_punkt_hinzufügen, stangen_darstellen, stangen_verwalten
from zusatz_funktionen import write_csv_file, plot_csv, get_achsenlimits, gif_to_mp4
from zusatz_funktionen import write_csv_file, plot_csv, get_achsenlimits, gif_to_mp4
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

    #Schreibe csv:
    dateipfad = "Visualisierung_Daten/sim_output.csv"
    write_csv_file(all_steps, point_names_sorted, dateipfad)

    # Achsenlimits: links min, rechts max
    alim = get_achsenlimits(dateipfad)
    x_lim= (alim[0], alim[1])
    y_lim= (alim[2], alim[3])

    #Plotte csv:
    plot_csv("Visualisierung_Daten/sim_output.csv", x_lim, y_lim)
    
    #Plotte Längenfehler:
    def plot_length_errors(mech, output_path="Visualisierung_Daten/laengenfehler.png"):
        """
        Erstellt eine Visualisierung des Längenfehlers aller Glieder als Funktion des Winkels.
        """
        angles = np.arange(mech.sim_config["startAngle"], mech.sim_config["endAngle"] + 1, mech.sim_config["stepAngle"])
        errors = np.array(mech.length_errors).T  # Transponiere für bessere Plottung

        link_names = [link.name for link in mech.links]

        plt.figure(figsize=(8, 5))
        for i, error_values in enumerate(errors):
            plt.plot(angles, error_values, label=link_names[i])
        
        plt.xlabel("Winkel θ (Grad)")
        plt.ylabel("Längenfehler (Einheit Länge)")
        plt.title("Längenfehler aller Glieder als Funktion von θ")
        plt.legend(loc = "lower left")
        plt.grid(True)
        plt.savefig(output_path)
        plt.close()
    
    plot_length_errors(mech)
    
    # Animation erstellen
    ani = create_animation(
        all_steps=all_steps,
        links=links,
        point_index_map=point_index_map,
        radius=circle_radius,
        circle_center=circle_center,
        xlim=x_lim,
        ylim=y_lim,
        point_names=point_names_sorted
    )

    output_file = "Visualisierung_Daten/mehrgelenk_animation.gif"
    ani.save(output_file, writer="imagemagick", fps=10)



if __name__ == "__main__":
    # Erstellen Seite
    st.set_page_config(layout="wide")
    css()
    col = st.columns([1, 1])

    with col[0]:
        st.header("Eingabe der Parameter", divider="red")
        punkte_darstellen()
        neuer_punkt_hinzufügen()

        driver_name = next((p["name"] for p in load_database()["points"] if p["driver"]), None)
        pivot_name = next((p["name"] for p in load_database()["points"] if p["pivot"]), None)
        driver_name = next((p["name"] for p in load_database()["points"] if p["driver"]), None)
        pivot_name = next((p["name"] for p in load_database()["points"] if p["pivot"]), None)

        stangen_darstellen()
        stangen_verwalten()


         

        st.subheader("Valid-Check ✅", divider="orange") 
        if st.button("Mechanismus überprüfen", key="validate"):
            is_valid, message = validate_mechanism(pivot_name, driver_name)
            if is_valid:
                st.success(message)
            else:
                st.error(message)
        

        st.subheader("Stückliste", divider="orange") 
        st.button("Stückliste erstellen", key="create_bom")

        

        


    with col[1]:
        st.header("Visualisierung", divider="gray")
        if st.button("Berechnung starten"):
            is_valid, message = validate_mechanism(pivot_name, driver_name)
            if is_valid:
                main(pivot_name, driver_name)
                path_curve_file = "Visualisierung_Daten/bahnkurve.png"
                st.image(path_curve_file, caption="Bahnkurven des Mechanismus")

                            
                st.image("Visualisierung_Daten/laengenfehler.png", caption="Längenfehler als Funktion von θ")

                
                gif_file = "Visualisierung_Daten/mehrgelenk_animation.gif"
                output_file = gif_to_mp4(gif_file)
                #st.video(output_file, caption="Animation der Mehrgelenkkette mit mehreren Treibern")
                st.video(output_file)
                
            else:
                st.error("Simulation kann nicht gestartet werden: " + message)