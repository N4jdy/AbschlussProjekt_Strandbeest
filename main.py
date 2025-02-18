import streamlit as st
import json
from mechanism import Mechanism
from ui import css, create_animation  # z.B. die erweiterte Version für Links + Punkte

def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    st.set_page_config(layout="wide")
    css()

    config = load_config("config.json")
    mech = Mechanism(config)
    mech.run_simulation()
    
    all_steps = mech.get_history()  # shape (nFrames, 2*N)

    # Damit wir die Links zeichnen können, brauchen wir das "links"-Array
    # und die "point_index"-Map aus der Mechanism-Klasse:
    links = config["links"]
    point_index_map = mech.point_index  # z.B. { "p0":0, "p1":1, ...}
    
    # Falls du den Kreis noch sichtbar machen willst:
    circle_center = None
    circle_radius = None
    for dconf in config["drivers"]:
        if dconf["type"] == "circle":
            circle_center = dconf["center"]
            circle_radius = dconf["radius"]
            break

    # Erzeuge Animation
    ani = create_animation(
        all_steps=all_steps,
        links=links,
        point_index_map=point_index_map,
        radius=circle_radius,
        circle_center=circle_center,
        xlim=(-150, 50),
        ylim=(-150, 50)
    )
    
    # Speichere das GIF
    output_file = "mehrgelenk_animation.gif"
    ani.save(output_file, writer="imagemagick", fps=10)
    
    st.image(output_file, caption="Animation der Mehrgelenkkette mit mehreren Treibern")

if __name__ == "__main__":
    main()
