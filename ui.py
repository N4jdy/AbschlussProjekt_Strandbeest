import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from klassen import Punkt
from funktionen import lade_elemente


# Punkte laden
elemente = lade_elemente("dictionary.json")

def css():
    st.markdown("""
        <style>
        /* Linke Spalte mit Border */
        div[data-testid="column"]:nth-of-type(1) {
            border: 2px solid red;      /* Roter Rand */
            border-radius: 10px;        /* Abgerundete Ecken */
            padding: 20px;              /* Innenabstand */
            background-color: #f9f9f9;  /* Leicht grauer Hintergrund */
        }
        </style>
    """, unsafe_allow_html=True)


def setze_punkte():
    st.subheader("Punkte")
    option = st.selectbox(
        "Punkt auswählen",
        list(elemente["Punkte"].keys()),  # Die Namen der Punkte anzeigen
        index=None,
        placeholder="Wähle einen Punkt aus..."
    )
    
    # Standardwerte, wenn kein Punkt ausgewählt ist
    if option:
        ausgewählter_punkt = elemente["Punkte"][option]
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
    if st.button("Absenden", disabled=not felder_aktiv):
        ausgewählter_punkt.set_coordinates(neuer_x, neuer_y)
        st.success(f"Koordinaten von {option} aktualisiert: x = {neuer_x}, y = {neuer_y}")


def neuer_punkt_hinzufügen():
    st.subheader("Neuen Punkt erstellen")
    name = st.text_input("Name des Punktes")
    x = st.number_input("x-Wert", value=0)
    y = st.number_input("y-Wert", value=0)
    art = st.selectbox("Art des Punktes", ["Gelenk", "Kurbel", "Gestell"])

    if st.button("Punkt hinzufügen"):
        if name in elemente["Punkte"]:
            st.error("Ein Punkt mit diesem Namen existiert bereits.")
        else:
            elemente["Punkte"][name] = Punkt(x, y, art)
            st.success(f"Punkt '{name}' hinzugefügt!")


def setze_stangen():
    st.subheader("Stangen")

    # Daten für die Tabelle vorbereiten
    stangen_daten = [
        {"Name der Stange": name, "Punkt 1": punkt1_name, "Punkt 2": punkt2_name}
        for name, glied in elemente["Glieder"].items()
        for punkt1_name, punkt1 in elemente["Punkte"].items() if punkt1 == glied.p1
        for punkt2_name, punkt2 in elemente["Punkte"].items() if punkt2 == glied.p2
    ]

    # Bearbeitbare Tabelle anzeigen
    edited_stangen_daten = st.data_editor(stangen_daten)

    # Änderungen speichern
    if st.button("Änderungen speichern"):
        for row in edited_stangen_daten:
            name = row["Name der Stange"]
            punkt1_name = row["Punkt 1"]
            punkt2_name = row["Punkt 2"]
            elemente["Glieder"][name].p1 = elemente["Punkte"][punkt1_name]
            elemente["Glieder"][name].p2 = elemente["Punkte"][punkt2_name]
        st.success("Änderungen gespeichert!")


def neue_stange_hinzufügen():
    st.subheader("Neue Stange hinzufügen")

def create_animation(p0, p1_list, p2_list, c, radius, winkel_anf):
    # Alle Punkte sammeln
    all_x = [p0.x] + [p[0] for p in p1_list] + [p[0] for p in p2_list] + [c.x]
    all_y = [p0.y] + [p[1] for p in p1_list] + [p[1] for p in p2_list] + [c.y]
    
    # Grenzen des Koordinatensystems berechnen
    x_min, x_max = min(all_x) - 10, max(all_x) + 10
    y_min, y_max = min(all_y) - 10, max(all_y) + 10
    
    # Animation erstellen
    fig, ax = plt.subplots()
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_title("Bewegung der Viergelenkkette")
    ax.set_aspect('equal')
    
    line1, = ax.plot([], [], 'ro-', lw=2, label="Link 1")
    line2, = ax.plot([], [], 'bo-', lw=2, label="Link 2")
    circle = plt.Circle((c.x, c.y), radius, color='r', fill=False)
    ax.add_artist(circle)
    ax.legend(loc='best')
    
    def update(frame):
        p1 = p1_list[frame]
        p2 = p2_list[frame]
        line1.set_data([p0.x, p1[0]], [p0.y, p1[1]])
        line2.set_data([p1[0], p2[0]], [p1[1], p2[1]])
        return line1, line2
    
    ani = FuncAnimation(fig, update, frames=len(p1_list), interval=100)
    return ani