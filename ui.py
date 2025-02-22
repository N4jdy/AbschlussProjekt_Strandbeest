import streamlit as st
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




def punkte_darstellen():
    st.subheader("Punkte", divider="orange")
    point_list = Point.find_all()

    # Daten für die Tabelle vorbereiten
    punkte_daten = [
        {
            "Name": point.name, 
            "X-Koordinate": point.x, 
            "Y-Koordinate": point.y, 
            "Fixiert": point.fixed,
            "Driver": point.driver, 
            "Pivot": point.pivot
        }
        for i, point in enumerate(point_list)
    ]

    # Bearbeitbare Tabelle anzeigen
    edited_punkte_daten = st.data_editor(
        punkte_daten,
        column_config={
            "Driver": st.column_config.Column(
                help="'Driver' dreht sich um 'Pivot', ist ein Drehgelenk",
            ),
            "Pivot": st.column_config.Column(
                help="'Pivot' dreht sich um 'Driver', ist ein festes Gelenk",
            ),
        },
        disabled=["Name"], 
    )

    driver_selected = [entry["Driver"] for entry in edited_punkte_daten]
    pivot_selected = [entry["Pivot"] for entry in edited_punkte_daten]

    # Änderungen speichern
    if st.button("Änderungen speichern", key="save_changes"):
        if sum(driver_selected) > 1 or sum(pivot_selected) > 1:
            st.error("Es darf nur 1en Driver und 1en Pivot geben")
        else:
            for edited, point in zip(edited_punkte_daten, point_list):
                point.set_coords(edited["X-Koordinate"], edited["Y-Koordinate"])
                point.fixed = edited["Fixiert"]
                point.driver = edited["Driver"]
                point.pivot = edited["Pivot"]
                point.store_data()
            st.success("Änderungen gespeichert!")

    # Punkt löschen
    st.subheader("Punkt löschen")
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


def neuer_punkt_hinzufügen():
    st.subheader("Neuen Punkt erstellen")
    neuer_punkt_name = st.text_input("Name des neuen Punktes")
    neuer_x = st.number_input("Position auf x-Achse", value=0.0)
    neuer_y = st.number_input("Position auf y-Achse", value=0.0)
    ist_fixiert = st.checkbox("Punkt fixieren?")

    if st.button("Punkt speichern", key="save_point"):
        if neuer_punkt_name:
            if Point.find_by_attribute("name", neuer_punkt_name):
                st.error("Ein Punkt mit diesem Namen existiert bereits!")
            else:
                neuer_punkt = Point(neuer_punkt_name, neuer_x, neuer_y, ist_fixiert)
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
    if st.button("Änderungen speichern", ):
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
