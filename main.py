import streamlit as st
import csv
import math
import matplotlib.pyplot as plt
import numpy as np

from mechanism import Mechanism
from ui import css, create_animation
from write_csv import write_csv_file, plot_csv
from db_connector import DatabaseConnector

def load_database():
    """
    Lädt alle relevanten Daten aus database.json
    """
    db = DatabaseConnector()
    return {
        "points": db.get_table("points").all(),  # ✅ Holt Punkte richtig
        "links": db.get_table("links").all()  # ✅ Holt Verbindungen richtig (drivers nicht mehr nötig)
    }

def main():
    """
    Hauptprogramm: Lädt Daten, erstellt die Mechanism-Simulation und zeigt die Animation.
    """
    st.set_page_config(layout="wide")
    css()

    # Lade alle Tabellen aus der Datenbank
    db_data = load_database()

    # Definiere hier den Pivot (Fixpunkt) und den Driver (Bewegungspunkt)
    pivot_name = "p2"  # Beispielhafter Fixpunkt
    driver_name = "p1"  # Beispielhafter beweglicher Punkt

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

    output_file = "mehrgelenk_animation.gif"
    ani.save(output_file, writer="imagemagick", fps=10)
    st.image(output_file, caption="Animation der Mehrgelenkkette mit mehreren Treibern")

    write_csv_file(all_steps, point_names_sorted, "sim_output.csv")
    plot_csv("sim_output.csv")

if __name__ == "__main__":
    main()
