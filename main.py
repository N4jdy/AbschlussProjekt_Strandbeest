import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import time

def laenge_berechnung(x_vec_anf, winkel_a, winkel, radius):

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

    #drüber stimmt alles
    x_komponente = radius * np.cos(winkel)
    y_komponente = radius * np.sin(winkel)

    x_komponente_anfang = radius * np.cos(winkel_a)
    y_komponente_anfang = radius * np.sin(winkel_a)

    verschiebung_x = x_komponente - x_komponente_anfang
    verschiebung_y = y_komponente - y_komponente_anfang
    #print(verschiebung_x)
    #print(verschiebung_y)

    x_vec_a = x_vec_anf.copy() # Ansonsten wird x_vec_anf direkt verändert
    x_vec_a[4] = x_vec_a[4] + verschiebung_x
    x_vec_a[5] = x_vec_a[5] + verschiebung_y 
    #print(x_vec_a)

    laenge_mat = A_matrix @ x_vec_a
    laenge_vec = np.array([
        np.sqrt(laenge_mat[0]**2 + laenge_mat[1]**2), 
        np.sqrt(laenge_mat[2]**2 + laenge_mat[3]**2)
    ])
    #print(laenge_mat)
    #print(laenge_vec)

    Fehler = laenge_vec - laenge_vector
    print(f" Gerechneter Fehler: {Fehler}")

    return Fehler

def bestimmung_radius(x1, y1, x2, y2):
    coord1 = np.array([x1, y1])
    coord2 = np.array([x2, y2])

    # Euklidische Distanz berechnen
    distance = np.linalg.norm(coord1 - coord2)

    print(distance)
    return(distance)


# Startvektor
x_vec  = np.array([0, 0, 10, 35, -25.0, 10.0])
radius = bestimmung_radius(-25.0, 10.0, -30.0, 0.0)

# Zum Überprüfen:
winkel_anf = np.arctan(2)
winkel = winkel_anf + np.deg2rad(10)
laenge_berechnung(x_vec, winkel_anf, winkel, radius)

# Schleife für konstanten Drehwinkel
# if button is pressed: -> Bsp für Aufruf
'''cons_rot_winkel = False
winkel_rot = 0
while cons_rot_winkel:
    winkel_anf = np.arctan(2)
    winkel_rot += 1
    if winkel_rot == 360:
        winkel_rot = 0
    winkel = winkel_anf + np.deg2rad(winkel_rot)
    laenge_berechnung(x_vec, winkel_anf, winkel, radius)
    time.sleep(2)
    '''
# oder so:
'''for winkel in np.linspace(0, 2*np.pi, 360):  # 1°-Schritte
    laenge_berechnung(x_vec, winkel_anf, winkel, radius)
    time.sleep(2)
    '''



