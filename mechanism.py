# mechanism.py
import numpy as np
from scipy.optimize import least_squares
import scipy.signal

from point import Point
from link import Link

class Mechanism:
    def __init__(self, config):
        self.config = config

        self.points_config = config["points"]   
        self.links_config = config["links"]   
        self.drivers_config = config["drivers"]
        self.sim_config = config["simulation"]
        self.opt_config = config["optimization"]

        
        self.points = {}
        for p_name, p_info in self.points_config.items():
            x_val, y_val = p_info["coords"]
            fixed = p_info.get("fixed", False)
            self.points[p_name] = Point(name=p_name, x=x_val, y=y_val, fixed=fixed)

        
        self.links = []
        for link_info in self.links_config:
            s_name = link_info["start"]
            e_name = link_info["end"]
            start_pt = self.points[s_name]
            end_pt   = self.points[e_name]
            link_obj = Link(start_pt, end_pt)
            self.links.append(link_obj)

        
        self.history = []

    def _constraints(self, x, driver_positions=None):
        point_names_sorted = sorted(self.points.keys())

        
        for i, p_name in enumerate(point_names_sorted):
            px = x[2*i]
            py = x[2*i+1]
            self.points[p_name].set_coords(px, py)

        errors = []

        
        for link_obj in self.links:
            errors.append(link_obj.length_error())

        
        for p_name in point_names_sorted:
            pt = self.points[p_name]
            if pt.fixed:
                x_fixed, y_fixed = self.points_config[p_name]["coords"]
                errors.append(pt.x - x_fixed)
                errors.append(pt.y - y_fixed)

        
        if driver_positions is not None:
            for d_name, d_pos in driver_positions.items():
                pt = self.points[d_name]
                errors.append(pt.x - d_pos[0])
                errors.append(pt.y - d_pos[1])

        return np.array(errors)

    def _get_driver_positions(self, angle_rad):
        driver_positions = {}
        for d in self.drivers_config:
            p_name = d["point"]
            d_type = d["type"]
            if d_type == "circle":
                cx, cy = d["center"]
                r = d["radius"]
                x_driver = cx + r * np.cos(angle_rad)
                y_driver = cy + r * np.sin(angle_rad)
                driver_positions[p_name] = (x_driver, y_driver)
        return driver_positions

    def run_simulation(self):
        point_names_sorted = sorted(self.points.keys())
        x0_list = []
        for p_name in point_names_sorted:
            pt = self.points[p_name]
            x0_list.append(pt.x)
            x0_list.append(pt.y)
        current_x = np.array(x0_list, dtype=float)

        start_deg = self.sim_config["startAngle"]
        end_deg   = self.sim_config["endAngle"]
        step_deg  = self.sim_config["stepAngle"]
        angles = np.arange(start_deg, end_deg+1, step_deg)

        for alpha_deg in angles:
            alpha_rad = np.deg2rad(alpha_deg)
            
            driver_pos = self._get_driver_positions(alpha_rad)

            
            max_jump = self.opt_config.get("maxJump", 2.0)
            lb = current_x - max_jump
            ub = current_x + max_jump

            
            result = least_squares(
                fun=self._constraints,
                x0=current_x,
                args=(driver_pos,),
                bounds=(lb, ub)
            )
            current_x = result.x

            
            self.history.append(current_x.copy())

        
        arr_history = np.array(self.history)  
        w = self.opt_config["smoothWindow"]
        p = self.opt_config["smoothPolyorder"]
        for col in range(arr_history.shape[1]):
            arr_history[:, col] = scipy.signal.savgol_filter(
                arr_history[:, col], w, p
            )
        self.history = arr_history

    def get_history(self):
        return self.history
