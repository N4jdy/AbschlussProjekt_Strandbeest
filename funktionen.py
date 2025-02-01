import numpy as np
from scipy.optimize import least_squares
import matplotlib.pyplot as plt

def laenge_glieder_berechnung(x_vec_anf, winkel_a, winkel, radius, koord = False):

    A_matrix = np.array([[1, 0, -1, 0, 0, 0], 
                         [0, 1, 0, -1, 0, 0], 
                         [0, 0, 1, 0, -1, 0], 
                         [0, 0, 0, 1, 0, -1]])
    
    # Startpunkt
    x_vector = x_vec_anf.copy()
    laenge_matrix = A_matrix @ x_vector
    laenge_vector = np.array([
            np.sqrt(laenge_matrix[0]**2 + laenge_matrix[1]**2), 
            np.sqrt(laenge_matrix[2]**2 + laenge_matrix[3]**2)
        ])
    #print(laenge_vector)

    x_vec = winkelfunktion(x_vec_anf, winkel_a, winkel, radius)
    if koord:
        return x_vec

    laenge_mat = A_matrix @ x_vec
    laenge_vec = np.array([
        np.sqrt(laenge_mat[0]**2 + laenge_mat[1]**2), 
        np.sqrt(laenge_mat[2]**2 + laenge_mat[3]**2)
    ])
    #print(laenge_mat)
    #print(laenge_vec)

    Fehler = laenge_vec - laenge_vector
    #print(f" Gerechneter Fehler: {Fehler}")

    return Fehler

def bestimmung_radius(x1, y1, x2, y2):
    coord1 = np.array([x1, y1])
    coord2 = np.array([x2, y2])

    # Euklidische Distanz berechnen
    distance = np.linalg.norm(coord1 - coord2)

    #print(f"Radius = {distance}")
    return(distance)

def bestimmung_anfangswinkel(x1, y1, x2, y2):
    coord1 = np.array([x1, y1])
    coord2 = np.array([x2, y2])

    # Winkel berechnen
    angle = np.arctan2(coord2[1] - coord1[1], coord2[0] - coord1[0])

    #print(f"Anfangswinkel = {np.rad2deg(angle)}")
    return(angle)

def winkelfunktion(x_vec_anf, winkel_a, winkel, radius):
    # Berechne die Differenz der Kreispositionen:
    delta_x = radius * (np.cos(winkel) - np.cos(winkel_a))
    delta_y = radius * (np.sin(winkel) - np.sin(winkel_a))
    
    # Kopiere den Eingangsvektor, um diesen nicht zu verändern:
    x_vec_a = x_vec_anf.copy()
    
    # Aktualisiere die Koordinaten (Index 4: x, Index 5: y)
    x_vec_a[4] += delta_x
    x_vec_a[5] += delta_y
    
    return x_vec_a

def plot_koord_kr_bewegung(bewegung_p2_x, bewegung_p2_y, art_von_plot):
    # Kreisbewegung plotten zum überprüfen
    xpoints = np.array(bewegung_p2_x)
    ypoints = np.array(bewegung_p2_y)
    if art_von_plot == 1:
        plt.plot(xpoints, ypoints, 'r-', label='Kreisbewegung', linewidth=1)
        plt.plot(xpoints[0], ypoints[0], 'ro', label='Startpunkt', markersize=4) 
        plt.axis('equal')
        plt.title('Kreisbewegung(p2)')
        plt.xlabel('x-Achse')
        plt.ylabel('y-Achse')
        plt.legend(loc='upper left')
        plt.savefig('Kreisbewegung.png')  # Speichert es als Bild
    if art_von_plot == 2:
        plt.plot(xpoints, ypoints, 'r-', label='Fehler', linewidth=1)
        plt.plot(xpoints[0], ypoints[0], 'ro', label='Startpunkt', markersize=4) 
        plt.axis('equal')
        plt.title('Fehlerbewegung(p1)???')
        plt.xlabel('x-Achse')
        plt.ylabel('y-Achse')
        plt.legend(loc='upper right')
        plt.savefig('Fehlerbewegung.png')
    
    plt.close()  # Schließt die aktuelle Figur

    # Bild anzeigen
    tab = True
    if tab:
        from PIL import Image
        if art_von_plot == 1:
            img = Image.open('Kreisbewegung.png')
        if art_von_plot == 2:
            img = Image.open('Fehlerbewegung.png')
        img.show()

def fehler_funktion(x_vec, winkel_anf, winkel, radius):
    result = least_squares(lambda x: laenge_glieder_berechnung(x, winkel_anf, winkel, radius), x_vec, method='trf') 
    #print("Optimierter Vektor:", result.x)
    #print("Optimierter Fehler:", result.fun)
    return result.x
