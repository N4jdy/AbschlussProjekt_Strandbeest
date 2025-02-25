import streamlit as st
import csv
import math
import matplotlib.pyplot as plt
import numpy as np

from klassen import Mechanism
from ui import css, create_animation, punkte_darstellen, punkte_verwalten, stangen_darstellen, stangen_verwalten, visualisierung, erstelle_stueckliste
from zusatz_funktionen import write_csv_file, plot_csv, get_achsenlimits, gif_to_mp4
from db_connector import DatabaseConnector

def load_database():
   
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
    
    # Prüfen, dass y-Koordinaten von Pivot und Driver identisch sind
    pivot_y = None
    driver_y = None
    for p in db_data["points"]:
        if p.get("pivot") is True: 
            pivot_y = p.get("coords", [None, None])[1] 
        if p.get("driver") is True:
            driver_y = p.get("coords", [None, None])[1]
    if pivot_y != driver_y:
        return False, "Pivot und Driver müssen die gleiche Y-Koordinate haben!"


    # Prüfen, ob der Driver mit dem Pivot verbunden ist
    connected = any((pivot_name in link and driver_name in link) for link in link_points)
    if not connected:
        return False, "Driver ist nicht direkt mit dem Pivot oder über eine Kette verbunden!"
    
    # Prüfen, dass Pivot fest ist
    for p in db_data["points"]:
        if p.get("pivot", False) and not p.get("fixed", False):
            return False, f"Ungültige Konfiguration: Da Punkt {p['name']} der Pivot ist, darf er keine Freiheitsgrade haben und muss deshalb fest sein!"
            
    
    # Prüfen, ob alle Verbindungen sinnvoll sind
    for link in link_points:
        start, end = link
        if start == end:
            return False, f"Ungültige Verbindung: Punkt {start} ist mit sich selbst verbunden!"
        if start not in point_names or end not in point_names:
            return False, f"Ungültige Verbindung: Einer der Punkte ({start}, {end}) existiert nicht!"
    
    # Prüfen, dass kein Punkt gleichzeitig Driver oder Pivot und Schubkurbel ist
    for p in db_data["points"]:
        if p.get("driver", False) or p.get("pivot", False):
            if p.get("slide_x", False) or p.get("slide_y", False):
                return False, f"Ungültige Konfiguration: Punkt {p['name']} kann nicht gleichzeitig Driver/Pivot und eine Schubkurbel sein!"
    
    for p in db_data["points"]:
        if p.get("slide_x", True) and p.get("slide_y", True):
            return False, f"Ungültige Konfiguration: Punkt {p['name']} kann nicht gleichzeitig Schubkurbel in X und Y Richtung sein!"
    
    # Prüfen, dass mindestens ein weiteres fixiertes Gelenk (außer dem Pivot) existiert
    fixed_gelenke = [p["name"] for p in db_data["points"] if p.get("fixed", False) and not p.get("pivot", False)]
    if len(fixed_gelenke) == 0:
        return False, "Ungültige Konfiguration: Es muss mindestens ein weiteres fixiertes Gelenk (außer dem Pivot) vorhanden sein!"
    
    #Prüfen, ob alle Punkte mit anderen verbunden sind
    point_connections = {p: 0 for p in point_names}
    for start, end in link_points:
        point_connections[start] += 1
        point_connections[end] += 1

    unconnected_points = [p for p, count in point_connections.items() if count == 0]
    if unconnected_points:
        return False, f"Ungültige Konfiguration: Die folgenden Punkte sind nicht mit anderen verbunden: {', '.join(unconnected_points)}"
    
    # Prüfen, dass kein Punkt gleichzeitig fixiert und Schubkurbel ist
    for p in db_data["points"]:
        if p.get("fixed", False) and (p.get("slide_x", False) or p.get("slide_y", False)):
            return False, f"Ungültige Konfiguration: Punkt {p['name']} kann nicht gleichzeitig fixiert und eine Schubkurbel sein!"
    
    # Prüfen, dass kein Punkt gleichzeitig Driver und fixiert ist
    for p in db_data["points"]:
        if p.get("driver", False) and p.get("fixed", False):
            return False, f"Ungültige Konfiguration: Punkt {p['name']} ist als Treiber definiert, aber auch fixiert!"
    
    # Prüfen, dass kein Punkt gleichzeitig Schubkurbel in X und Y Richtung ist
    for p in db_data["points"]:
        if (p.get("slide_x", False) or p.get("slide_y", False)) and any(p["name"] in link for link in link_points):
            return False, f"Ungültige Konfiguration: Punkt {p['name']} kann nicht gleichzeitig eine Schubkurbel und mit einer anderen Verbindung gekoppelt sein!"
        
    # Prüfen, dass mindestens eine Verbindung existiert
    if not link_points:
        return False, "Ungültige Konfiguration: Der Mechanismus muss mindestens eine Verbindung enthalten!"

    return True, "Mechanismus ist valide."


def main(pivot_name, driver_name):
    """
    Hauptprogramm: Lädt Daten, erstellt die Mechanism-Simulation und erstellt die Animation.
    """

    db_data = load_database()

   
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
    csv_filename = "Visualisierung_Daten/sim_output.csv"
    write_csv_file(all_steps, point_names_sorted, csv_filename)

    alim = get_achsenlimits(csv_filename)
    x_lim= (alim[0], alim[1])
    y_lim= (alim[2], alim[3])

    #Plotte csv:
    plot_csv("Visualisierung_Daten/sim_output.csv", x_lim, y_lim)
    
    #Plotte Längenfehler:
    def plot_length_errors(mech, output_path="Visualisierung_Daten/laengenfehler.png"):
       
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
    
    overlay = False
    if st.session_state.overlay:
        overlay = True
    # Animation erstellen
    ani = create_animation(
        all_steps=all_steps,
        links=links,
        point_index_map=point_index_map,
        radius=circle_radius,
        circle_center=circle_center,
        xlim=x_lim,
        ylim=y_lim,
        point_names=point_names_sorted,
        overlay = overlay,
        csv_filename = csv_filename
    )

    output_file = "Visualisierung_Daten/mehrgelenk_animation.gif"
    ani.save(output_file, writer="imagemagick", fps=10)
    gif_to_mp4(output_file)



if __name__ == "__main__":
    # Erstellen Seite
    st.set_page_config(
        page_title="Strandbeest-Simulation",
        page_icon="⚙️",
        layout="wide"
    )
    css()
    col = st.columns([1, 1])

    with col[0]:
        st.header("Eingabe der Parameter", divider="red")
        punkte_darstellen()
        
        if "bear_pun" not in st.session_state:
            st.session_state.bear_pun = False

        # Toggle-Button: Speichert den Zustand automatisch
        if st.button("Punkte löschen/hinzufügen", key="toggle_bear_pun"):
            st.session_state.bear_pun = not st.session_state.bear_pun

        if st.session_state.bear_pun:
            st.caption("Zum Ausblenden noch mal drücken")
            punkte_verwalten()

        driver_name = next((p["name"] for p in load_database()["points"] if p["driver"]), None)
        pivot_name = next((p["name"] for p in load_database()["points"] if p["pivot"]), None)

        stangen_darstellen()
        if "bear_sta" not in st.session_state:
            st.session_state.bear_sta = False
        if st.button("Stangen löschen/hinzufügen", key="toggle_bear_sta"):
            st.session_state.bear_sta = not st.session_state.bear_sta
        if st.session_state.bear_sta:
            st.caption("Zum Ausblenden noch mal drücken")
            stangen_verwalten()


        st.subheader("Valid-Check ✅", divider="orange") 
        if st.button("Mechanismus überprüfen", key="validate"):
            is_valid, message = validate_mechanism(pivot_name, driver_name)
            if is_valid:
                st.success(message)
            else:
                st.error(message)
        

        st.subheader("Stückliste", divider="orange") 
        if st.button("Stückliste erstellen", key="create_bom"):
            erstelle_stueckliste()

        
    with col[1]:
        st.header("Visualisierung", divider="gray")
        with st.form("Berechnung"):
            st.caption("Zum Visualisieren des Modells, mit den neu eingegebenen Parametern bitte auf den folgenden Knopf drücken. Außerdem sollte während des Ladens kein weiterer Knopf gedrückt werden, ansonsten funktioniert die Aktualisierung nicht:")
            if st.form_submit_button("Berechnung starten"):
                is_valid, message = validate_mechanism(pivot_name, driver_name)
                if is_valid:
                    with st.spinner("Bitte warten..."):
                        main(pivot_name, driver_name)
                    st.success("Visualisierung wurde erfolgreich aktualisiert")     
                else:
                    st.error("Simulation kann nicht gestartet werden: " + message)
            
        # Wählen ob mit oder ohne overlay
        with st.form("Overlay"):
            st.caption("Folgenden Knopf drücken wenn man gerne eine Animation mit Overlay hätte:\n(Hinzufügen von Namen der Punkte und Bahnkuven auf die Visualisierung)")
            if "overlay" not in st.session_state:
                st.session_state.overlay = False
            if st.form_submit_button("Overlay"):
                st.session_state.overlay = not st.session_state.overlay
                st.caption("Achtung: Berechnung noch mal ausführen für Visualisierung!")
            if st.session_state.overlay:
                st.caption("Status: Animation mit Overlay")
            if not st.session_state.overlay:
                st.caption("Status: Animation ohne Overlay")
        
        visualisierung()