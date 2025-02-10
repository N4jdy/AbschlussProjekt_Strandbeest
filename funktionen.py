import numpy as np
from scipy.optimize import least_squares, minimize
import matplotlib.pyplot as plt
import csv

def bestimmung_radius(x1, y1, x2, y2):
    coord1 = np.array([x1, y1])
    coord2 = np.array([x2, y2])

    # Euklidische Distanz berechnen
    radius_length = np.linalg.norm(coord1 - coord2)

    #print(f"Radius = {radius_length}")
    return(radius_length)

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

def laenge_glieder_berechnung(x_vec_anf, winkel_a, winkel, radius, rueckgabe = 0):
    # 0 = Fehler, 1 = Koordinaten, 2 = Längenvektor

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
    if rueckgabe == 2:
        return laenge_vector

    x_vec = winkelfunktion(x_vec_anf, winkel_a, winkel, radius)
    if rueckgabe == 1:
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

def write_csv_file(data, filename):
    # Funktion zum Schreiben der CSV-Datei
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["x", "y"])
        for row in data:
            writer.writerow(row)

"""
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
        plt.plot(xpoints, ypoints, 'r-', label='Fehlerbewegung', linewidth=1)
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

def fehler_funktion_prototyp(x_vec, winkel_anf, winkel, radius):
    result = least_squares(lambda x: laenge_glieder_berechnung(x, winkel_anf, winkel, radius), x_vec, method='trf') 
    #print("Optimierter Vektor:", result.x)
    #print("Optimierter Fehler:", result.fun)
    return result.x

def fehler_funktion(x_vec_anf, winkel_anf, winkel, radius):
    x_vec_gleich = x_vec_anf.copy()
    x_vec_changed = x_vec_anf.copy()
    con_len = laenge_glieder_berechnung(x_vec_gleich, winkel_anf, winkel, radius, 2)
    p2_pos = laenge_glieder_berechnung(x_vec_gleich, winkel_anf, winkel, radius, 1)

    def constraints(x):
        p1 = x
        p2 = x_vec_changed[4:6]  # p2 bleibt fest
        p2[0] = p2_pos[4]
        p2[1] = p2_pos[5]
        dist_p1_p2 = np.linalg.norm(p1 - p2) - con_len[1]
        dist_p0_p2 = np.linalg.norm(x_vec_changed[:2] - p2) - con_len[0]  # p0 bleibt fest
        return [dist_p1_p2, dist_p0_p2]

    def objective(x):
        x_vec_opt = x_vec_changed.copy()
        x_vec_opt[2:4] = x  # Nur p1 wird optimiert
        return np.sum(laenge_glieder_berechnung(x_vec_opt, winkel_anf, winkel, radius)**2)

    cons = [{'type': 'eq', 'fun': lambda x: constraints(x)[0]},
            {'type': 'eq', 'fun': lambda x: constraints(x)[1]}]

    # Verwenden Sie die Methode 'trust-constr' für eine stabilere Optimierung
    result = minimize(objective, x_vec_changed[2:4], method='trust-constr', constraints=cons)
    x_vec_changed[2:4] = result.x  # Aktualisiere p1 im ursprünglichen Vektor
    #print("Optimierter Vektor:", x_vec_changed)
    return x_vec_changed
"""