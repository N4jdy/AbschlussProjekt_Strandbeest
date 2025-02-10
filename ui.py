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
    # Animation erstellen
    fig, ax = plt.subplots()
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    ax.set_title("Bewegung der Viergelenkkette")
    ax.set_aspect('equal')
    
    line1, = ax.plot([], [], 'ro-', lw=2, label="Link 1")
    line2, = ax.plot([], [], 'bo-', lw=2, label="Link 2")
    circle = plt.Circle((c[0], c[1]), radius, color='r', fill=False)
    ax.add_artist(circle)
    ax.legend()
    
    def update(frame):
        p1 = p1_list[frame]
        p2 = p2_list[frame]
        line1.set_data([p0[0], p1[0]], [p0[1], p1[1]])
        line2.set_data([p1[0], p2[0]], [p1[1], p2[1]])
        return line1, line2
    
    ani = FuncAnimation(fig, update, frames=len(p1_list), interval=100)
    return ani