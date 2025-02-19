import streamlit as st
import json
import csv
import math
import matplotlib.pyplot as plt
import numpy as np

from mechanism import Mechanism
from ui import css, create_animation
from write_csv import write_csv_file, plot_csv


def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)

def setup_circle_driver(config, pivot_name="p2", driver_name="p1"):
   
    pivot_coords = config["points"][pivot_name]["coords"]   
    driver_coords = config["points"][driver_name]["coords"]  

    dx = driver_coords[0] - pivot_coords[0]
    dy = driver_coords[1] - pivot_coords[1]
    radius = math.sqrt(dx*dx + dy*dy)


    config["drivers"] = [
        {
            "point": driver_name,
            "type": "circle",
            "center": pivot_coords,
            "radius": radius
        }
    ]

    return config

def main():
    st.set_page_config(layout="wide")
    css()

    
    config = load_config("config.json")

    
    config = setup_circle_driver(config, pivot_name="p2", driver_name="p1")

    
    mech = Mechanism(config)
    mech.run_simulation()

    
    all_steps_list = mech.get_history()  

    
    all_steps = np.array(all_steps_list)  

    point_names_sorted = sorted(mech.points.keys())
    point_index_map = { name: i for i, name in enumerate(point_names_sorted) }

    
    links = config["links"]


    circle_center = None
    circle_radius = None
    for dconf in config["drivers"]:
        if dconf["type"] == "circle":
            circle_center = dconf["center"]
            circle_radius = dconf["radius"]
            break

    
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
