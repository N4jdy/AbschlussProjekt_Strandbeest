import os
from tinydb import TinyDB, Query
import numpy as np

# Gelenk
class Punkt:
    # Database connection
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dictionary.json')
    db_connector = TinyDB(db_path).table('Punkte')

    # Constructor
    def __init__(self, name, x, y, art):
        self.name = name
        self.x = x
        self.y = y
        self.art = art # Gelenk, Drehgelenk oder Festpunkt
        self.setze_freiheitsgrade(art)

    def __str__(self):
        return f"Punkt(name={self.name}, x={self.x}, y={self.y}, art={self.art})"
    
    def __repr__(self):
        return self.__str__()
    
    def setze_freiheitsgrade(self, art):
        if art == "Gelenk":
            self.starrer_punkt = False
            self.mittelpunkt_kreisbahn = False
        elif art == "Drehgelenk":
            self.starrer_punkt = True
            self.mittelpunkt_kreisbahn = True
        elif art == "Festpunkt":
            self.starrer_punkt = True
            self.mittelpunkt_kreisbahn = False

    def get_coordinates(self):
        return np.array([self.x, self.y])

    def set_coordinates(self, x, y):
        self.x = x
        self.y = y

    # Neue Bestimme Radius Funktion
    def distanz_zu(self, other): 
        distanz = np.linalg.norm(self.get_coordinates() - other.get_coordinates())
        return distanz

    # Neue Bestimme Anfangswinkel Funktion
    def winkel_zu(self, other):
        delta = other.get_coordinates() - self.get_coordinates()
        winkel = np.arctan2(delta[1], delta[0])
        return winkel
    
    def store_data(self):
        print(f"Storing data for {self.name}...")
        DeviceQuery = Query()
        result = self.db_connector.search(DeviceQuery.name == self.name)
        if result:
            self.db_connector.update({
                'x': self.x,
                'y': self.y,
                'art': self.art
            }, DeviceQuery.name == self.name)
            print(f"Data for '{self.name}' updated.")
        else:
            self.db_connector.insert({
                'name': self.name,
                'x': self.x,
                'y': self.y,
                'art': self.art
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
            return [cls(d['name'], d['x'], d['y'], d['art']) for d in data]
        return []

    @classmethod
    def find_all(cls) -> list:
        results = cls.db_connector.all()
        return [cls(d['name'], d['x'], d['y'], d['art']) for d in results]
    

# Stange
class Glied:
    # Database connection
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dictionary.json')
    db_connector = TinyDB(db_path).table('Glieder')

    def __init__(self, name, p1, p2):
        self.name = name
        self.p1 = p1
        self.p2 = p2
        self.länge = p1.distanz_zu(p2)
        self.bestimme_art() # Glied, Gestell oder Kurbel 

    def bestimme_art(self):
        if self.p1.starrer_punkt and self.p2.starrer_punkt:
            self.art = "Gestell"
        elif self.p1.mittelpunkt_kreisbahn or self.p2.mittelpunkt_kreisbahn:
            self.art = "Kurbel"
        elif self.p1.mittelpunkt_kreisbahn and self.p2.mittelpunkt_kreisbahn:
            return "Fehler: Zwei Drehgelenke können nicht verbunden werden"
        else:
            self.art = "Glied"
    
    def __repr__(self):
        return f"Glieder(p1={self.p1}, p2={self.p2}, art={self.art})"
    
    def store_data(self):
        print(f"Storing data for {self.name}...")
        DeviceQuery = Query()
        result = Punkt.find_by_name(self.p1.name)
        if result:
            Punkt.db_connector.update({
                'p1': self.p1.name,
                'p2': self.p2.name
            }, DeviceQuery.name == self.name)
            print(f"Data for '{self.name}' updated.")
        else:
            Punkt.db_connector.insert({
                'name': self.name,
                'p1': self.p1.name,
                'p2': self.p2.name
            })
            print(f"Data for '{self.name}' inserted.")
        
    def delete(self):
        print(f"Deleting data for {self.name}...")
        DeviceQuery = Query()
        result = Punkt.find_by_name(self.name)
        if result:
            Punkt.db_connector.remove(DeviceQuery.name == self.name)
            print(f"Data for '{self.name}' deleted.")
        else:
            print(f"Data for '{self.name}' not found.")
    
    @classmethod
    def find_by_attribute(cls, by_attribute: str, attribute_value: str, num_to_return=1):
        DeviceQuery = Query()
        result = cls.db_connector.search(DeviceQuery[by_attribute] == attribute_value)
        if result:
            data = result[:num_to_return]
            return [cls(d['name'], d['p1'], d['p2']) for d in data]
        return []

    @classmethod
    def find_all(cls) -> list:
        results = cls.db_connector.all()
        return [cls(d['name'], d['p1'], d['p2']) for d in results]
