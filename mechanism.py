import numpy as np
from scipy.optimize import least_squares
import scipy.signal

from db_connector import DatabaseConnector
from point import Point
from link import Link

class Mechanism:
    def __init__(self, pivot_name, driver_name):
        db = DatabaseConnector()
        self.points_config = db.get_table("points").all()
        self.links_config = db.get_table("links").all()

        # Treiber werden dynamisch berechnet (nicht aus database.json)
        self.drivers_config = []

        self.sim_config = {
            "startAngle": 0,
            "endAngle": 360,
            "stepAngle": 3
        }

        self.opt_config = {
            "maxJump": 1.0,
            "smoothWindow": 5,
            "smoothPolyorder": 2
        }

        self.points = {}
        for p_info in self.points_config:
            name, coords, fixed = p_info["name"], p_info["coords"], p_info.get("fixed", False)
            self.points[name] = Point(name=name, x=coords[0], y=coords[1], fixed=fixed)

        self.links = []
        for link_info in self.links_config:
            s_name, e_name = link_info["start"], link_info["end"]
            self.links.append(Link(self.points[s_name], self.points[e_name]))

        self.history = []

        
        self.setup_drivers(pivot_name, driver_name)
    
    def _constraints(self, x, driver_positions=None):
        """
        Definiert die Nebenbedingungen für die Optimierung.
        Stellt sicher, dass Längen und feste Punkte eingehalten werden.
        """
        point_names_sorted = sorted(self.points.keys())

        # Setze die Punktpositionen basierend auf dem Optimierungsvektor x
        for i, p_name in enumerate(point_names_sorted):
            px = x[2 * i]
            py = x[2 * i + 1]
            self.points[p_name].set_coords(px, py)

        errors = []

        # Überprüfe die Längenbedingungen der Links
        for link_obj in self.links:
            errors.append(link_obj.length_error())

        # Überprüfe feste Punkte
        for p_name in point_names_sorted:
            pt = self.points[p_name]
            if pt.fixed:
                x_fixed, y_fixed = next(p["coords"] for p in self.points_config if p["name"] == p_name)
                errors.append(pt.x - x_fixed)
                errors.append(pt.y - y_fixed)

        # Überprüfe Treiberpositionen
        if driver_positions is not None:
            for d_name, d_pos in driver_positions.items():
                pt = self.points[d_name]
                errors.append(pt.x - d_pos[0])
                errors.append(pt.y - d_pos[1])

        # Debug: Zeigt die ersten Fehlerwerte für jede Iteration
        print(f"Constraints Errors: {errors[:5]} ...")

        return np.array(errors)


    def setup_drivers(self, pivot_name, driver_name):
        """
        Berechnet dynamisch die Treiber-Konfiguration, indem ein Punkt (driver_name)
        auf einer Kreisbahn um einen anderen Punkt (pivot_name) bewegt wird.
        """
        pivot = next((p for p in self.points_config if p["name"] == pivot_name), None)
        driver = next((p for p in self.points_config if p["name"] == driver_name), None)

        if not pivot or not driver:
            raise ValueError(f"❌ Fehler: Punkte {pivot_name} oder {driver_name} nicht in database.json gefunden!")

        pivot_coords = pivot["coords"]
        driver_coords = driver["coords"]

        dx = driver_coords[0] - pivot_coords[0]
        dy = driver_coords[1] - pivot_coords[1]
        radius = np.sqrt(dx**2 + dy**2)

        self.drivers_config = [{
            "point": driver_name,
            "type": "circle",
            "center": pivot_coords,
            "radius": radius
        }]

        print(f"✅ Driver erstellt: {self.drivers_config}")

    def _get_driver_positions(self, angle_rad):
        """
        Berechnet die Positionen der Treiber basierend auf dem aktuellen Winkel.
        """
        driver_positions = {}

        if not self.drivers_config:
            print("❌ FEHLER: Keine Treiber vorhanden! Mechanismus kann sich nicht bewegen.")
            return driver_positions

        for d in self.drivers_config:
            p_name = d["point"]
            d_type = d["type"]
            if d_type == "circle":
                cx, cy = d["center"]
                r = d["radius"]
                x_driver = cx + r * np.cos(angle_rad)
                y_driver = cy + r * np.sin(angle_rad)
                driver_positions[p_name] = (x_driver, y_driver)

        print(f"Treiber bei Winkel {angle_rad:.2f} rad -> {driver_positions}")

        return driver_positions

    def run_simulation(self):
        """
        Führt die Simulation durch und speichert die Ergebnisse.
        """
        point_names_sorted = sorted(self.points.keys())
        x0_list = []
        for p_name in point_names_sorted:
            pt = self.points[p_name]
            x0_list.append(pt.x)
            x0_list.append(pt.y)
        current_x = np.array(x0_list, dtype=float)

        start_deg, end_deg, step_deg = self.sim_config["startAngle"], self.sim_config["endAngle"], self.sim_config["stepAngle"]
        angles = np.arange(start_deg, end_deg + 1, step_deg)

        for alpha_deg in angles:
            alpha_rad = np.deg2rad(alpha_deg)

            # Treiberpositionen berechnen
            driver_pos = self._get_driver_positions(alpha_rad)

            # Grenzen für die Optimierung setzen
            max_jump = self.opt_config["maxJump"]
            lb, ub = current_x - max_jump, current_x + max_jump

            # Optimierung durchführen
            result = least_squares(
                fun=self._constraints,
                x0=current_x,
                args=(driver_pos,),
                bounds=(lb, ub)
            )
            current_x = result.x

            print(f"Iteration {alpha_deg}°: {current_x[:5]} ...")  # Zeigt die ersten 5 Koordinaten

            # Simulationsergebnisse speichern
            self.history.append(current_x.copy())

        # Glätten der Ergebnisse
        arr_history = np.array(self.history)
        w, p = self.opt_config["smoothWindow"], self.opt_config["smoothPolyorder"]
        for col in range(arr_history.shape[1]):
            arr_history[:, col] = scipy.signal.savgol_filter(arr_history[:, col], w, p)

        self.history = arr_history

    def get_history(self):
        return self.history
