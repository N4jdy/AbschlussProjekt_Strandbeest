import numpy as np

class Point:
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
