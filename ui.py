import streamlit as st
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv

from klassen import Point, Link
from zusatz_funktionen import plot_csv

def css():
    st.markdown("""
        <style>
        /* Dein CSS */
        </style>
    """, unsafe_allow_html=True)


def punkte_darstellen():
    st.subheader("Punkte", divider="orange")
    point_list = Point.find_all()
    
    punkte_daten = [
        {
            "Name": point.name, 
            "X-Koordinate": point.x, 
            "Y-Koordinate": point.y, 
            "Fixiert": point.fixed,
            "Driver": point.driver, 
            "Pivot": point.pivot,
            "Schubführung_X": point.slide_x,
            "Schubführung_Y": point.slide_y 
        }
        for point in point_list
    ]
    
    edited_punkte_daten = st.data_editor(
        punkte_daten,
        column_config={
            "Driver": st.column_config.Column(
                help="'Driver' dreht sich um 'Pivot', ist ein Drehgelenk",
            ),
            "Pivot": st.column_config.Column(
                help="'Pivot' dreht sich um 'Driver', ist ein festes Gelenk",
            ),
            "Schubführung_X": st.column_config.Column(
                help="Erlaubt Bewegung nur entlang der x-Achse"
            ),
            "Schubführung_Y": st.column_config.Column(
                help="Erlaubt Bewegung nur entlang der y-Achse"
            )

        },
        disabled=["Name"], 
    )
    
    driver_selected = [entry["Driver"] for entry in edited_punkte_daten]
    pivot_selected = [entry["Pivot"] for entry in edited_punkte_daten]


    if st.button("Änderungen speichern", key="save_changes"):
        if sum(driver_selected) > 1 or sum(pivot_selected) > 1:
            st.error("Es darf jeweils nur einen Driver und Pivot geben")
        else:
            for edited, point in zip(edited_punkte_daten, point_list):
                point.set_coords(edited["X-Koordinate"], edited["Y-Koordinate"])
                point.fixed = edited["Fixiert"]
                point.driver = edited["Driver"]
                point.pivot = edited["Pivot"]
                point.slide_x = edited["Schubführung_X"]
                point.slide_y = edited["Schubführung_Y"]  
                point.store_data()
            st.success("Änderungen gespeichert!")

def punkte_verwalten():
    # Punkt löschen
    st.subheader("Punkt löschen")
    point_list = Point.find_all()
    punkt_namen = [p.name for p in point_list]
    punkt_zu_loeschen = st.selectbox("Punkt auswählen", punkt_namen, index=None, placeholder="Wähle einen Punkt...")

    if st.button("Punkt löschen", key="delete_point"):
        if punkt_zu_loeschen:
            zu_loeschender_punkt = Point.find_by_attribute("name", punkt_zu_loeschen)
            if zu_loeschender_punkt:
                zu_loeschender_punkt[0].delete()
                st.success(f"Punkt '{punkt_zu_loeschen}' gelöscht!")
            else:
                st.error("Punkt nicht gefunden!")
        else:
            st.error("Bitte einen Punkt auswählen!")

    st.subheader("Neuen Punkt erstellen")
    neuer_punkt_name = st.text_input("Name des neuen Punktes")
    neuer_x = st.number_input("Position auf x-Achse", value=0.0)
    neuer_y = st.number_input("Position auf y-Achse", value=0.0)
    ist_fixiert = st.checkbox("Punkt fixieren?")
    ist_schubgeführt_X = st.checkbox("Bewegung nur in x-Richtung zulassen?")
    ist_schubgeführt_Y = st.checkbox("Bewegung nur in y-Richtung zulassen?")
    
    if st.button("Punkt speichern", key="save_point"):
        if neuer_punkt_name:
            if Point.find_by_attribute("name", neuer_punkt_name):
                st.error("Ein Punkt mit diesem Namen existiert bereits!")
            else:
                neuer_punkt = Point(neuer_punkt_name, neuer_x, neuer_y, ist_fixiert, slide_x=ist_schubgeführt_X, slide_y=ist_schubgeführt_Y)
                neuer_punkt.store_data()
                st.success(f"Neuer Punkt '{neuer_punkt_name}' gespeichert!")
        else:
            st.error("Bitte einen Namen für den Punkt eingeben!")


def stangen_darstellen():
    st.subheader("Stangen", divider="orange")
    link_list = Link.find_all()

    # Daten für die Tabelle vorbereiten
    stangen_daten = [
        {"Name der Stange": link.name, "Startpunkt": link.start_point.name, "Endpunkt": link.end_point.name}
        for link in link_list
    ]

    # Bearbeitbare Tabelle anzeigen
    edited_stangen_daten = st.data_editor(
        stangen_daten,
        disabled=["Name der Stange"],
    )

    # Änderungen speichern
    if st.button("Änderungen speichern", key="save_link_changes"):
        for edited, link in zip(edited_stangen_daten, link_list):
            link.start_point = Point.find_by_attribute("name", edited["Startpunkt"])[0]
            link.end_point = Point.find_by_attribute("name", edited["Endpunkt"])[0]
            link.store_data()
        st.success("Änderungen gespeichert!")


def stangen_verwalten():
    st.subheader("Stangen verwalten")
    link_list = Link.find_all()

    # Neue Stange erstellen
    st.text("Neue Stange erstellen")
    punkt_namen = [p.name for p in Point.find_all()]
    start_punkt = st.selectbox("Startpunkt wählen", punkt_namen, index=None, placeholder="Wähle einen Startpunkt...")
    end_punkt = st.selectbox("Endpunkt wählen", punkt_namen, index=None, placeholder="Wähle einen Endpunkt...")
    neue_stange_name = st.text_input("Name der neuen Stange")

    if st.button("Neue Stange speichern", key="save_link"):
        if start_punkt and end_punkt and neue_stange_name:
            start = Point.find_by_attribute("name", start_punkt)
            end = Point.find_by_attribute("name", end_punkt)

            if not start or not end:
                st.error("Einer der gewählten Punkte existiert nicht!")
            elif Link.find_by_attribute("name", neue_stange_name):
                st.error("Eine Stange mit diesem Namen existiert bereits!")
            else:
                neue_stange = Link(neue_stange_name, start[0], end[0])
                neue_stange.store_data()
                st.success(f"Neue Stange '{neue_stange_name}' gespeichert!")
        else:
            st.error("Bitte alle Felder ausfüllen!")

    # Stange löschen
    st.text("Stange löschen")
    stange_namen = [l.name for l in link_list]
    stange_zu_loeschen = st.selectbox("Stange auswählen", stange_namen, index=None, placeholder="Wähle eine Stange...")

    if st.button("Stange löschen", key="delete_link"):
        if stange_zu_loeschen:
            zu_loeschende_stange = Link.find_by_attribute("name", stange_zu_loeschen)
            if zu_loeschende_stange:
                zu_loeschende_stange[0].delete()
                st.success(f"Stange '{stange_zu_loeschen}' gelöscht!")
            else:
                st.error("Stange nicht gefunden!")
        else:
            st.error("Bitte eine Stange auswählen!")


def create_animation(
    all_steps: np.ndarray,
    links: list = None,
    point_index_map: dict = None,
    radius: float = None,
    circle_center: tuple = None,
    xlim=(-100, 0),
    ylim=(-50, 50),
    point_names: list = None,
    overlay: bool = False,
    csv_filename: str = None,
):
    """
    Erstellt eine Animation der Bewegung eines Mehrgelenksystems.

    Parameter:
    - all_steps: np.ndarray mit Shape (AnzahlFrames, 2*N), enthält die Koordinaten der Punkte in jedem Frame.
    - links: Liste von Dictionaries mit {"start": "pX", "end": "pY"} für die Verbindungen zwischen Punkten.
    - point_index_map: Dictionary, das Punktnamen "pX" auf Indizes im Koordinatenvektor abbildet.
    - radius, circle_center: Falls ein Kreis gezeichnet werden soll (optional).
    - xlim, ylim: Achsenbegrenzungen.
    - point_names: Liste von Namen für Punkte, die über den Punkten angezeigt werden sollen.
    - overlay: Bool, ob Labels Kreis und Bahnkurve gezeichnet werden sollen.
    - csv_filename: beinhaltet Werte für die Bahnkurve

    Rückgabe:
    - Eine `FuncAnimation`-Instanz, die die Bewegung animiert.
    """
    
    fig, ax = plt.subplots()
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_aspect('equal')
    ax.set_title("Bewegung der Mehrgelenkkette")

    # Scatterplot für Punkte
    scatter = ax.scatter([], [], c='blue')

    # Falls CSV-Daten verwendet werden, laden & plotten
    if overlay:
        with open(csv_filename, mode='r') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  
            rows = list(csv_reader)
        num_cols = len(header)
        cols = [[] for _ in range(num_cols)]
        for row in rows:
            if len(row) < num_cols:
                continue
            for c in range(num_cols):
                cols[c].append(float(row[c]))
        first_curve = True
        for i in range(0, num_cols, 2):
            x_vals = cols[i]
            y_vals = cols[i+1]
            ax.plot(x_vals, y_vals, c='green', alpha=0.6, linestyle="-", linewidth=1.5, 
                    label="Bahnkurve" if first_curve else None)
            first_curve = False
    
    # Punkt-Beschriftungen
    point_labels = []
    if overlay and point_names:
        for name in point_names:
            text = ax.text(0, 0, name, fontsize=9, ha='left', va='bottom', color='green',
                           bbox=dict(facecolor='none', alpha=0.6, edgecolor='none'))
            point_labels.append(text)

    # Kreis zeichnen (optional)
    if overlay is False and radius is not None and circle_center is not None:
        circle = plt.Circle(circle_center, radius, color='r', fill=False)
        ax.add_artist(circle)

    # Falls du Glieder (Links) zeichnen willst:
    lines = []
    if links and point_index_map:
        for _ in links:
            line_obj, = ax.plot([], [], 'k-', lw=2)
            lines.append(line_obj)

    def init():
        scatter.set_offsets(np.empty((0, 2)))
        for ln in lines:
            ln.set_data([], [])
        for text in point_labels:
            text.set_position((-1000, -1000))
        return [scatter, *lines, *point_labels]

    def update(frame_index):
        coords = all_steps[frame_index]  # => (2*N,)
        nPoints = coords.shape[0] // 2

        # 1) Scatter aktualisieren
        xy_pairs = []
        for i in range(nPoints):
            x_i = coords[2*i]
            y_i = coords[2*i + 1]
            xy_pairs.append([x_i, y_i])
        scatter.set_offsets(xy_pairs)

        # 2) Lines aktualisieren
        if links and point_index_map:
            for ln_obj, link_info in zip(lines, links):
                start_name = link_info["start"]
                end_name   = link_info["end"]
                
                i_start = point_index_map[start_name]
                i_end   = point_index_map[end_name]

                x_s = coords[2*i_start]
                y_s = coords[2*i_start + 1]
                x_e = coords[2*i_end]
                y_e = coords[2*i_end + 1]

                ln_obj.set_data([x_s, x_e], [y_s, y_e])
        
        for i, text in enumerate(point_labels):
            x_i = coords[2*i]
            y_i = coords[2*i + 1] + 2
            text.set_position((x_i, y_i))

        return [scatter, *lines, *point_labels]

    ani = FuncAnimation(
        fig, 
        update, 
        frames=len(all_steps), 
        init_func=init, 
        interval=100, 
        blit=True
    )

    #plt.legend()
    return ani


def visualisierung():
    #tab1, tab2, tab3, tab4, tab5 = st.tabs(["Animation(.gif)","Animation(.mp4)","Bahnkurven","Animation mit Bahnkurve","Längenfehler"])
    tab1, tab2, tab3, tab5 = st.tabs(["Animation(.gif)","Animation(.mp4)","Bahnkurven","Längenfehler"])
    with tab1:
        gif_path = "Visualisierung_Daten/mehrgelenk_animation.gif"
        st.image(gif_path, caption="Animation der Mehrgelenkkette mit mehreren Treibern")

        with open(gif_path, "rb") as gif_file:
            gif_bytes = gif_file.read()
            st.download_button(label="📥 GIF herunterladen (.gif)", data=gif_bytes, file_name="mehrgelenk_animation.gif", mime="image/gif")
    with tab2:
        video_path = "Visualisierung_Daten/Animation.mp4"
        #st.video(video_path, caption="Animation der Mehrgelenkkette mit mehreren Treibern")
        st.video(video_path)
        
        with open(video_path, "rb") as video_file:
            video_bytes = video_file.read()
            st.download_button(label="📥 Video herunterladen (.mp4)", data=video_bytes, file_name="Animation.mp4", mime="video/mp4")

        '''
        # HTML & JavaScript für Video-Steuerung ohne eingebaute Controls
        video_html = f"""
            <style>
                .video-container {{
                    text-align: center;
                }}
                video {{
                    width: 500px;
                    border: 2px solid #ccc;
                    border-radius: 10px;
                }}
                .controls {{
                    display: flex;
                    justify-content: center;
                    margin-top: 10px;
                }}
                .controls button {{
                    margin: 5px;
                    padding: 10px;
                    font-size: 16px;
                    cursor: pointer;
                }}
            </style>

            <div class="video-container">
                <video id="customVideo" width="700">
                    <source src="{video_path}" type="video/mp4">
                    Dein Browser unterstützt dieses Videoformat nicht.
                </video>
                
                <div class="controls">
                    <button onclick="document.getElementById('customVideo').currentTime -= 5">⏪ 5s zurück</button>
                    <button onclick="document.getElementById('customVideo').play()">▶ Play</button>
                    <button onclick="document.getElementById('customVideo').pause()">⏸ Pause</button>
                    <button onclick="document.getElementById('customVideo').currentTime += 5">⏩ 5s vor</button>
                </div>
            </div>
        """

        # In Streamlit als HTML einbinden
        st.components.v1.html(video_html, height=500)
        '''
    
    with tab3:
        path_curve_file = "Visualisierung_Daten/Bahnkurve.png"
        st.image(path_curve_file, caption="Bahnkurven des Mechanismus")

    #with tab4:
        #st.text("noch machen")
    
    with tab5:
        st.image("Visualisierung_Daten/laengenfehler.png", caption="Längenfehler als Funktion von θ")

def erstelle_stueckliste():
    point_list = Point.find_all()
    link_list = Link.find_all()

    fixed_counter = 0
    check_driver = 0
    schub_counter = 0
    for point in point_list:
        if point.get_fixed():
            fixed_counter += 1
        elif point.get_driver():
            check_driver += 1
        elif point.get_x_schub() or point.get_y_schub():
            schub_counter += 1
    
    anzahl_gelenke = len(point_list) - fixed_counter - check_driver - schub_counter
    
    # Daten für die Tabelle vorbereiten
    df_gelenke = pd.DataFrame(
        {
            "Menge": [anzahl_gelenke],
            "Bezeichnung": ["Gelenk"],
            "Länge (mm)": ["-"],  # Nur bei Gestänge
            "Radius (mm)": ["-"]   # Nur bei Antrieb
        }
    )

    # Tabelle erstellen und anzeigen
    combined_df = df_gelenke
    
    radius = 0
    pivot_coord = None
    driver_coord = None
    for point in point_list: 
        if point.get_pivot():
            pivot_coord = point.coords()
        if point.get_driver(): 
            driver_coord = point.coords()
    dx = driver_coord[0] - pivot_coord[0]
    dy = driver_coord[1] - pivot_coord[1]
    radius = np.sqrt(dx**2 + dy**2)

    if check_driver != 0:
        df_drehgelenk = pd.DataFrame(
            {
                "Menge": [1],
                "Bezeichnung": ["Drehgelenk"],
                "Länge (mm)": ["-"],  # Nur bei Gestänge
                "Radius (mm)": ["-"]   # Nur bei Antrieb
            }
        )
        combined_df = pd.concat([combined_df, df_drehgelenk], ignore_index=True)
        
    if check_driver != 0:
        df_antrieb = pd.DataFrame(
            {
                "Menge": [1],
                "Bezeichnung": ["Antrieb"],
                "Länge (mm)": ["-"],  # Nur bei Gestänge
                "Radius (mm)": [radius]   # Nur bei Antrieb
            }
        )
        combined_df = pd.concat([combined_df, df_antrieb], ignore_index=True)

    if fixed_counter != 0:
        df_festgelenk = pd.DataFrame(
            {
                "Menge": [fixed_counter],
                "Bezeichnung": ["Festgelenk"],
                "Länge (mm)": ["-"],  # Nur bei Gestänge
                "Radius (mm)": ["-"]   # Nur bei Antrieb
            }
        )
        combined_df = pd.concat([combined_df, df_festgelenk], ignore_index=True)

    if schub_counter != 0:
        df_schubgelenk = pd.DataFrame(
            {
                "Menge": [schub_counter],
                "Bezeichnung": ["Schubgelenk"],
                "Länge (mm)": ["-"],  # Nur bei Gestänge
                "Radius (mm)": ["-"]   # Nur bei Antrieb
            }
        )
        combined_df = pd.concat([combined_df, df_schubgelenk], ignore_index=True)

    # Daten für Gestänge vorbereiten
    gestänge_mengen = [1] * len(link_list)  # Anzahl der Gestänge
    gestänge_bezeichnungen = [f"Stange ({link.name})" for link in link_list]  # Name für jedes Gestänge
    gestänge_längen = [link.current_length() for link in link_list] # Längen der Gestänge

    df_gestänge = pd.DataFrame(
        {
            "Menge": gestänge_mengen,
            "Bezeichnung": gestänge_bezeichnungen,
            "Länge (mm)": gestänge_längen,
            "Radius (mm)": ["-"] * len(link_list)  # Nur bei Antrieb
        }
    )

    combined_df = pd.concat([combined_df, df_gestänge], ignore_index=True)

    # Die gesamte Tabelle anzeigen
    st.table(combined_df)

    # Als .csv herunterladen
    csv = combined_df.to_csv(index=False).encode("utf-8")
    st.download_button(label="📥 Stückliste herunterladen(.csv)", data=csv, file_name="stueckliste_strandbeest.csv", mime="text/csv")
