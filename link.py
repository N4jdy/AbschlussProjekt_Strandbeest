import numpy as np

class Link:
    def __init__(self, start_point, end_point):
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
