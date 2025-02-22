import os
from tinydb import TinyDB, Query
import numpy as np
from scipy.optimize import least_squares
import scipy.signal

from db_connector import DatabaseConnector

# Gelenk/Punkt
class Point:
    # Database connection
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')
    db_connector = TinyDB(db_path).table('points')

    def __init__(self, name, x, y, fixed=False):
        self.name = name
        self.x = x
        self.y = y
        self.fixed = fixed

    def coords(self):
        """Gibt die aktuellen Koordinaten als (x,y)-Tuple zurück."""
        return (self.x, self.y)

    def set_coords(self, x, y):
        """Setzt neue Koordinaten (wird beim Optimieren aktualisiert)."""
        self.x = x
        self.y = y

    def __str__(self):
        return f"Punkt(name={self.name}, x={self.x}, y={self.y}, fixed={self.fixed})"
    
    def __repr__(self):
        return self.__str__()

    def store_data(self):
        print(f"Storing data for {self.name}...")
        DeviceQuery = Query()
        result = self.db_connector.search(DeviceQuery.name == self.name)
        if result:
            self.db_connector.update({
                'coords' : [
                    self.x,
                    self.y
                ]
            }, DeviceQuery.name == self.name)
            print(f"Data for '{self.name}' updated.")
        else:
            self.db_connector.insert({
                'name': self.name,
                'coords' : [
                    self.x,
                    self.y
                ],
                'fixed': self.fixed
            })
            print(f"Data for '{self.name}' inserted.")
    
    def delete(self):
        print(f"Deleting data for {self.name}...")
        DeviceQuery = Query()
        result = self.db_connector.search(DeviceQuery.name == self.name)
        if result:
            self.db_connector.remove(DeviceQuery.name == self.name)
            print(f"Data for '{self.name}' deleted.")
        else:
            print(f"Data for '{self.name}' not found.")

    @classmethod
    def find_by_attribute(cls, by_attribute: str, attribute_value: str, num_to_return=1):
        DeviceQuery = Query()
        result = cls.db_connector.search(DeviceQuery[by_attribute] == attribute_value)
        if result:
            data = result[:num_to_return]
            return [cls(d['name'], d['coords'][0], d['coords'][1], d['fixed']) for d in data]
        return []

    @classmethod
    def find_all(cls) -> list:
        results = cls.db_connector.all()
        return [cls(d['name'], d['coords'][0], d['coords'][1], d['fixed']) for d in results]


# Stange/Glied
class Link:
    # Database connection
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')
    db_connector = TinyDB(db_path).table('links')

    def __init__(self, name, start_point, end_point):
        self.name = name  # Name der Stange
        self.start_point = start_point  # Referenz auf ein Point-Objekt
        self.end_point = end_point      # Referenz auf ein Point-Objekt
        # Anfangs-Länge aus den aktuellen Koordinaten bestimmen
        dx = end_point.x - start_point.x
        dy = end_point.y - start_point.y
        self.length = np.sqrt(dx*dx + dy*dy)

    def current_length(self):
        """Berechnet die aktuelle Länge basierend auf den Punkt-Koordinaten."""
        dx = self.end_point.x - self.start_point.x
        dy = self.end_point.y - self.start_point.y
        return np.sqrt(dx*dx + dy*dy)

    def length_error(self):
        """
        Liefert den Unterschied zwischen aktueller Länge und gespeicherter Soll-Länge.
        Kann man direkt in die Fehlerfunktion einbauen.
        """
        return self.current_length() - self.length
    
    def __str__(self):
        return f"Stange(name={self.name}, Startpunkt={self.start_point}, Endpunkt={self.end_point})"
    
    def __repr__(self):
        return self.__str__()
    
    def store_data(self):
        print(f"Storing data for {self.name}...")
        DeviceQuery = Query()
        result = self.db_connector.search(DeviceQuery.name == self.name)
        if result:
            self.db_connector.update({
                'start': self.start_point.name,    # Speichern des Namens des Startpunkts
                'end': self.end_point.name         # Speichern des Namens des Endpunkts
            }, DeviceQuery.name == self.name)
            print(f"Data for '{self.name}' updated.")
        else:
            self.db_connector.insert({
                'name': self.name,
                'start': self.start_point.name,
                'end': self.end_point.name 
            })
            print(f"Data for '{self.name}' inserted.")
        
    def delete(self):
        print(f"Deleting data for {self.name}...")
        DeviceQuery = Query()
        result = self.db_connector.search(DeviceQuery.name == self.name)
        if result:
            self.db_connector.remove(DeviceQuery.name == self.name)
            print(f"Data for '{self.name}' deleted.")
        else:
            print(f"Data for '{self.name}' not found.")
    
    @classmethod
    def find_by_attribute(cls, by_attribute: str, attribute_value: str, num_to_return=1):
        DeviceQuery = Query()
        result = cls.db_connector.search(DeviceQuery[by_attribute] == attribute_value)
        if result:
            data = result[:num_to_return]
            return [cls(d['name'], Point.find_by_attribute("name", d['start'])[0], Point.find_by_attribute("name", d['end'])[0]) for d in data]
        return []

    @classmethod
    def find_all(cls) -> list:
        results = cls.db_connector.all()
        return [
            cls(d['name'], Point.find_by_attribute("name", d['start'])[0], Point.find_by_attribute("name", d['end'])[0])
            for d in results
        ]
    

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
            self.links.append(Link(link_info["name"], self.points[s_name], self.points[e_name]))

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

        

        return np.array(errors)


    def setup_drivers(self, pivot_name, driver_name):
        """
        Berechnet dynamisch die Treiber-Konfiguration, indem ein Punkt (driver_name)
        auf einer Kreisbahn um einen anderen Punkt (pivot_name) bewegt wird.
        """
        pivot = next((p for p in self.points_config if p["name"] == pivot_name), None)
        driver = next((p for p in self.points_config if p["name"] == driver_name), None)

        if not pivot or not driver:
            raise ValueError(f" Fehler: Punkte {pivot_name} oder {driver_name} nicht in database.json gefunden!")

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

        print(f"Driver erstellt: {self.drivers_config}")

    def _get_driver_positions(self, angle_rad):
        """
        Berechnet die Positionen der Treiber basierend auf dem aktuellen Winkel.
        """
        driver_positions = {}

        if not self.drivers_config:
            print(" FEHLER: Keine Treiber vorhanden! Mechanismus kann sich nicht bewegen.")
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

