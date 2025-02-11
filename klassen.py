import numpy as np

# Gelenk
class Punkt:
    def __init__(self, x, y, art):
        self.x = x
        self.y = y
        self.art = art # Gelenk, Drehgelenk oder Festpunkt
        self.setze_freiheitsgrade(art)

    
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

    def __repr__(self):
        return f"Punkt(x={self.x}, y={self.y}, art={self.art})"

# Stange
class Glied:
    def __init__(self, p1, p2):
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
