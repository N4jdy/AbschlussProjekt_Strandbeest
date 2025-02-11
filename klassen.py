import numpy as np

# Gelenk
class Punkt:
    def __init__(self, x, y, starrer_punkt = False, mittelpunkt_kreisbahn = False):
        self.x = x
        self.y = y
        self.starrer_punkt = starrer_punkt
        self.mittelpunkt_kreisbahn = mittelpunkt_kreisbahn

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
    
    def setze_starrer_punkt(self, starrer_punkt):
        self.starrer_punkt = starrer_punkt
    
    def setze_mittelpunkt_kreisbahn(self, mittelpunkt_kreisbahn):
        self.mittelpunkt_kreisbahn = mittelpunkt_kreisbahn

    def __repr__(self):
        return f"Punkt(x={self.x}, y={self.y}, starrer_punkt={self.starrer_punkt})"

# Stange
class Glieder:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.art = "Glied" # Glied, Gestell oder Kurbel 

    def bestimme_art(self):
        if self.p1.starrer_punkt and self.p2.starrer_punkt:
            self.art = "Gestell"
        elif self.p1.mittelpunkt_kreisbahn or self.p2.mittelpunkt_kreisbahn:
            self.art = "Kurbel"
    
    def __repr__(self):
        return f"Glieder(p1={self.p1}, p2={self.p2}, art={self.art})"
