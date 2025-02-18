# mechanism.py
import numpy as np
from scipy.optimize import least_squares
import scipy.signal

class Mechanism:
    def __init__(self, config):
        self.config = config
        
        # 1) Punkte vorbereiten
        self.points_config = config["points"]
        self.links_config = config["links"]
        self.drivers_config = config["drivers"]
        self.sim_config = config["simulation"]
        self.opt_config = config["optimization"]
        
        # Mapping: pointName -> index im x-Array
        self.point_index = {}
        all_names = list(self.points_config.keys())
        for i, name in enumerate(all_names):
            self.point_index[name] = i
        
        # Initiales x_0 anlegen
        x_list = []
        for name in all_names:
            x_val, y_val = self.points_config[name]["coords"]
            x_list += [x_val, y_val]
        self.x0 = np.array(x_list, dtype=float)
        
        # 2) Link-Längen berechnen
        self.link_lengths = []
        for link in self.links_config:
            s_name = link["start"]
            e_name = link["end"]
            i_s = self.point_index[s_name]
            i_e = self.point_index[e_name]
            
            xs = self.x0[2*i_s]
            ys = self.x0[2*i_s + 1]
            xe = self.x0[2*i_e]
            ye = self.x0[2*i_e + 1]
            
            dist = np.sqrt((xe - xs)**2 + (ye - ys)**2)
            self.link_lengths.append(dist)
        
        # Ergebnis-Speicher
        self.history = []
    
    def _constraints(self, x, driver_positions=None):
        """
        Baut den Fehlervektor aus:
          - Link-Längen
          - Fixpunkte
          - Driver-Constraints
        """
        errors = []
        
        # 1) Link-Längen
        for idx, link in enumerate(self.links_config):
            length = self.link_lengths[idx]
            s_name = link["start"]
            e_name = link["end"]
            i_s = self.point_index[s_name]
            i_e = self.point_index[e_name]
            
            xs = x[2*i_s]
            ys = x[2*i_s + 1]
            xe = x[2*i_e]
            ye = x[2*i_e + 1]
            
            current_dist = np.sqrt((xe - xs)**2 + (ye - ys)**2)
            errors.append(current_dist - length)
        
        # 2) Fixierte Punkte
        for name, info in self.points_config.items():
            if info.get("fixed", False):
                i_pt = self.point_index[name]
                x_fixed = info["coords"][0]
                y_fixed = info["coords"][1]
                errors.append(x[2*i_pt]     - x_fixed)
                errors.append(x[2*i_pt + 1] - y_fixed)
        
        # 3) Driver
        if driver_positions is not None:
            # driver_positions = { "p2": (x2,y2), "p3":(x3,y3), ... }
            for d_name, d_pos in driver_positions.items():
                i_d = self.point_index[d_name]
                errors.append(x[2*i_d]     - d_pos[0])
                errors.append(x[2*i_d + 1] - d_pos[1])
        
        return np.array(errors)

    def _get_driver_positions(self, angle_rad):
        """
        Liest self.drivers_config und errechnet (x,y) für jeden Driver 
        basierend auf angle_rad, falls z.B. 'type': 'circle' oder 'line'.
        
        Gibt dict { "pointName": (x_val,y_val), ... } zurück.
        """
        driver_positions = {}
        
        for d in self.drivers_config:
            p_name = d["point"]
            d_type = d["type"]
            
            if d_type == "circle":
                # "center": [...], "radius": ...
                cx, cy = d["center"]
                r = d["radius"]
                # angle_rad variiert je Zeitschritt
                x_driver = cx + r * np.cos(angle_rad)
                y_driver = cy + r * np.sin(angle_rad)
                driver_positions[p_name] = (x_driver, y_driver)
            
        
        return driver_positions
    
    def run_simulation(self):
        """
        Hauptschleife über Winkel steps => berechne x(t) per least_squares
        """
        current_x = self.x0.copy()
        
        start_deg = self.sim_config["startAngle"]
        end_deg   = self.sim_config["endAngle"]
        step_deg  = self.sim_config["stepAngle"]
        
        angles = np.arange(start_deg, end_deg+1, step_deg)
        
        for alpha_deg in angles:
            alpha_rad = np.deg2rad(alpha_deg)
            
            # 1) Treiber-Positionen für diesen Zeitschritt holen
            driver_pos = self._get_driver_positions(alpha_rad)
            
            # 2) Bounds definieren
            max_jump = self.opt_config.get("maxJump", 5.0)
            lb = current_x - max_jump
            ub = current_x + max_jump
            
            # 3) least_squares
            result = least_squares(
                fun=self._constraints,
                x0=current_x,
                args=(driver_pos,),
                bounds=(lb, ub)
            )
            current_x = result.x
            
            # 4) abspeichern
            self.history.append(current_x.copy())
        
        # 5) Glätten (optional)
        arr_history = np.array(self.history)  # shape: (Steps, 2*N)
        w = self.opt_config["smoothWindow"]
        p = self.opt_config["smoothPolyorder"]
        for col in range(arr_history.shape[1]):
            arr_history[:,col] = scipy.signal.savgol_filter(arr_history[:,col], w, p)
        self.history = arr_history
        
    
    def get_history(self):
        return self.history
