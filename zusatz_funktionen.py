import csv
import moviepy as mp
import pandas as pd

def write_csv_file(all_steps, point_names, filename):
    num_frames, num_coords = all_steps.shape  
    num_points = len(point_names)

    header = []
    for p in point_names:
        header.append(f"x_{p}")
        header.append(f"y_{p}")

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  
        
        for t in range(num_frames):
            row_data = []
            for i in range(num_points):
                x_val = all_steps[t, 2*i]
                y_val = all_steps[t, 2*i+1]
                row_data.append(x_val)
                row_data.append(y_val)
            writer.writerow(row_data)


import matplotlib.pyplot as plt

def plot_csv(filename, xlim, ylim):
    """
    Liest eine CSV (z.B. aus write_csv_file geschrieben) und plottet
    die Bahnen aller Punkte in einem Diagramm.
    """
    with open(filename, mode='r') as file:
        csv_reader = csv.reader(file)
        
        header = next(csv_reader)  
        
        rows = list(csv_reader)
    
    num_cols = len(header)
    cols = [[] for _ in range(num_cols)]
    
    for row in rows:
        if len(row) < num_cols:
            continue
        for c in range(num_cols):
            cols[c].append(float(row[c]))
    
    plt.figure(figsize=(8, 6))

   
    for i in range(0, num_cols, 2):
        
        x_vals = cols[i]
        y_vals = cols[i+1]
        
        label_name = header[i].replace("x_", "")
        
        # Plot der Bahn
        plt.plot(x_vals, y_vals, '-', label=f'Bahnkurve {label_name}')
        # Startpunkt als Marker
        plt.plot(x_vals[0], y_vals[0], 'o', markersize=4)

    plt.xlim(xlim)
    plt.ylim(ylim)
    
    plt.axis('equal')
    plt.title('Bahnkurven aller Punkte')
    plt.xlabel('x-Achse')
    plt.ylabel('y-Achse')
    plt.legend(loc='best')
    plt.savefig('Visualisierung_Daten/Bahnkurve.png')
    plt.close()

def get_achsenlimits(dateipfad):
    data = pd.read_csv(dateipfad)

    x_min = float('inf')
    x_max = float('-inf')
    y_min = float('inf')
    y_max = float('-inf')

    # Durchlaufen der Spalten und Aktualisieren der Achsenlimits
    for column in data.columns:
        if 'x_' in column:  # Überprüfen, ob die Spalte X-Koordinaten enthält
            x_min = min(x_min, data[column].min())
            x_max = max(x_max, data[column].max())
        elif 'y_' in column:  # Überprüfen, ob die Spalte Y-Koordinaten enthält
            y_min = min(y_min, data[column].min())
            y_max = max(y_max, data[column].max())

    x_min -= 10
    x_max += 10
    y_min -= 10
    y_max += 10

    return [x_min, x_max, y_min, y_max]

    
def gif_to_mp4(gif):
    video_path = "Visualisierung_Daten/Animation.mp4"

    # Konvertiere GIF in MP4
    clip = mp.VideoFileClip(gif)
    clip.write_videofile(video_path, codec="libx264", fps=clip.fps)

    return video_path
