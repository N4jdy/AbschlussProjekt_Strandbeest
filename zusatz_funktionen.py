import csv

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

def plot_csv(filename):
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
    
    plt.axis('equal')
    plt.title('Bahnkurven aller Punkte')
    plt.xlabel('x-Achse')
    plt.ylabel('y-Achse')
    plt.legend(loc='best')
    plt.savefig('Visualisierung_Daten/Bahnkurve.png')
    plt.close()
    
