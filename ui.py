# ui.py
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from klassen import Point, Link

def css():
    st.markdown("""
        <style>
        /* Dein CSS */
        </style>
    """, unsafe_allow_html=True)

import streamlit as st

def punkte_darstellen():
    st.subheader("Punkte")
    Point_list = Point.find_all()

    option = st.selectbox(
        "Punkt auswählen",
        [p.name for p in Point_list],  # Die Namen der Punkte anzeigen
        index=None,
        placeholder="Wähle einen Punkt aus..."
    )

    # Standardwerte, wenn kein Punkt ausgewählt ist
    if option:
        ausgewählter_punkt = next(p for p in Point_list if p.name == option)
        x_wert = ausgewählter_punkt.x
        y_wert = ausgewählter_punkt.y
        felder_aktiv = True
    else:
        x_wert = 0
        y_wert = 0
        felder_aktiv = False

    # Eingabefelder immer anzeigen, aber deaktivieren, wenn kein Punkt ausgewählt ist
    neuer_x = st.number_input("Position auf x-Achse", value=x_wert, disabled=not felder_aktiv)
    neuer_y = st.number_input("Position auf y-Achse", value=y_wert, disabled=not felder_aktiv)

    # Absenden-Button ebenfalls deaktivieren, wenn kein Punkt ausgewählt ist
    if st.button("Änderung speichern", disabled=not felder_aktiv):
        if option:
            ausgewählter_punkt.set_coords(neuer_x, neuer_y)
            ausgewählter_punkt.store_data()
            st.success(f"Änderungen für '{option}' gespeichert!")


def neuer_punkt_hinzufügen():
    st.subheader("Neuen Punkt erstellen")


def stangen_darstellen():
    st.subheader("Stangen")
    link_list = Link.find_all()

    # Daten für die Tabelle vorbereiten
    stangen_daten = [
        {"Name der Stange": link.name, "Startpunkt": link.start_point.name, "Endpunkt": link.end_point.name}
        for link in link_list
    ]

    # Höhe Tabelle berechnen:
    heigth_table = 0
    for link in link_list:
        heigth_table += 1
    heigth_table *= 45

    # Bearbeitbare Tabelle anzeigen
    edited_stangen_daten = st.data_editor(
        stangen_daten,
        disabled=["Name der Stange"],  # Name ist nicht bearbeitbar
        height = heigth_table,
        num_rows="dynamic"
    )

    # Änderungen speichern
    if st.button("Änderungen speichern"):
        for edited, link in zip(edited_stangen_daten, link_list):
            link.start_point = Point.find_by_attribute("name", edited["Startpunkt"])[0]
            link.end_point = Point.find_by_attribute("name", edited["Endpunkt"])[0]
            link.store_data()
        st.success("Änderungen gespeichert!")


def create_animation(
    all_steps: np.ndarray,
    links: list = None,
    point_index_map: dict = None,
    radius: float = None,
    circle_center: tuple = None,
    xlim=(-100, 0),
    ylim=(-50, 50)
):
    """
    all_steps: shape (AnzahlFrames, 2*N)
    links: Liste { "start": "pX", "end":"pY" } => optional
    point_index_map: { "p0": 0, "p1":1, ...} => Index im Koordinatenvektor
    radius, circle_center: falls du noch einen Kreis plotten willst
    xlim, ylim: Achsenbegrenzung
    """
    fig, ax = plt.subplots()
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_aspect('equal')
    ax.set_title("Bewegung der Mehrgelenkkette")

    # Punkte als Scatter
    scatter = ax.scatter([], [], c='blue')

    # Kreis (optional)
    if radius is not None and circle_center is not None:
        circle = plt.Circle((circle_center[0], circle_center[1]),
                            radius, color='r', fill=False)
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
        return [scatter, *lines]

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

        return [scatter, *lines]

    ani = FuncAnimation(
        fig, update,
        frames=len(all_steps),
        init_func=init,
        interval=100,
        blit=True
    )
    return ani
