import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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