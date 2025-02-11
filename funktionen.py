import numpy as np
from scipy.optimize import least_squares, minimize
import matplotlib.pyplot as plt
import csv

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
        writer.writerow(["x1", "y1", "x2", "y2"])
        for i in range(len(data[0])):
            writer.writerow([data[0][i][0], data[0][i][1], data[1][i][0], data[1][i][1]])

def plot_csv(filename):
    # Funktion zum Plotten der CSV-Datei
    with open(filename, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Überspringe die Kopfzeile
        data = list(csv_reader)
        x1 = []
        y1 = []
        x2 = []
        y2 = []
        for row in data:
            if len(row) < 4:
                continue  # Überspringe unvollständige Zeilen
            x1.append(float(row[0]))
            y1.append(float(row[1]))
            x2.append(float(row[2]))
            y2.append(float(row[3]))
        # Plot 1
        plt.plot(x1, y1, 'b-', label='Bahnkurve p1', linewidth=1)
        plt.plot(x1[0], y1[0], 'bo', label='Startpunkt', markersize=4) 
        # Plot 2
        plt.plot(x2, y2, 'r-', label='Bahnkurve p2', linewidth=1)
        plt.plot(x2[0], y2[0], 'ro', label='Startpunkt', markersize=4)
        plt.axis('equal')
        plt.title('Bahnkurve')
        plt.xlabel('x-Achse')
        plt.ylabel('y-Achse')
        plt.legend(loc='best')
        plt.savefig('Bahnkurve.png')  # Speichert es als Bild

    plt.close()  # Schließt die aktuelles Figur

    # Bild anzeigen
    '''
    tab = True
    if tab:
        from PIL import Image
        img = Image.open('Bahnkurve.png')
        img.show()
    '''
