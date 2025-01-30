import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

x_vec  = np.array([0, 0, 10, 35, -25.0, 10.0])

radius = 10

winkel_a = np.arctan(2)

winkel = winkel_a + np.deg2rad(10)


def laenge_berechnung(x_vec_a, winkel_a, winkel, radius):

    x_vector = x_vec_a.copy()

    A_matrix = np.array([[1, 0, -1, 0, 0, 0], [0, 1, 0, -1, 0, 0], [0, 0, 1, 0, -1, 0], [0, 0, 0, 1, 0, -1]])

    laenge_matrix = A_matrix @ x_vector
    laenge_vector = np.array([[np.sqrt(laenge_matrix[0]**2 + laenge_matrix[1]**2)], [np.sqrt(laenge_matrix[2]**2 + laenge_matrix[3]**2)]])

    x_komponente = radius * np.cos(winkel)
    y_komponente = radius * np.sin(winkel)

    x_komponente_anfang = radius * np.cos(winkel_a)
    y_komponente_anfang = radius * np.sin(winkel_a)

    verschiebung_x = x_komponente - x_komponente_anfang
    verschiebung_y = y_komponente - y_komponente_anfang

    #print(verschiebung_x)
    #print(verschiebung_y)

    x_vec_a[4] = x_vec_a[4] + verschiebung_x
    x_vec_a[5] = x_vec_a[5] + verschiebung_y 
    #print(x_vec_a)

    laenge_mat = A_matrix @ x_vec
    #print(laenge_mat)

    laenge_vec = np.array([[np.sqrt(laenge_mat[0]**2 + laenge_mat[1]**2)], [np.sqrt(laenge_mat[2]**2 + laenge_mat[3]**2)]])

    #print(laenge_vec)

    #print(laenge_vector)

    Fehler = laenge_vec - laenge_vector
    print(f" Gerechneter Fehler: {Fehler}")

    return Fehler

laenge_berechnung(x_vec, winkel_a, winkel, radius)


