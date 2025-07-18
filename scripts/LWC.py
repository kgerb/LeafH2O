import pandas as pd
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np


def read_excel_rows_to_arrays(file_path):
    try:
        # Excel-Datei einlesen und die ersten zwei Zeilen ignorieren
        df = pd.read_excel(file_path, skiprows=2)
        
        # Zeilen als Arrays speichern
        rows_as_arrays = {f"Zeile {index+1}": row.to_numpy() for index, row in df.iterrows()}
        
        # Ausgabe der Zeilen
        for row_name, array in rows_as_arrays.items():
            print(f"{row_name}:")
            print(array)
            print("----")
        
        return rows_as_arrays
    except Exception as e:
        print(f"Fehler beim Einlesen der Excel-Datei: {e}")
        return None

# Beispielaufruf
# Ersetze 'deine_datei.xlsx' durch den Pfad zu deiner Excel-Datei
arrays = read_excel_rows_to_arrays("/mnt/c/Users/Kilian/Documents/LeafH2O/measurements/250522/leaf_water_content.xlsx")


# Prüfen, ob arrays erfolgreich erstellt wurden
if arrays:
    Meas = np.array(['1.Measurment (before)', '1.Measurment (after)', '2.Measurment', '3.Measurment'])
    
    # Iteration über die Zeilen
    for row_name, array in arrays.items():
        try:
            # Name aus der ersten Spalte extrahieren
            name = array[0]
            
            # Berechnungen durchführen
            wet_before = (array[1] - array[6]) / array[7]
            wet_after = (array[2] - array[6]) / array[7]
            first_meas = (wet_before + wet_after)/2
            sec_meas = (array[3] - array[6]) / array[7]
            third_meas = (array[4] - array[6]) / array[7]
            
            # Daten für das Plotten vorbereiten
            y_data = [name, first_meas, sec_meas, third_meas]
            pd.DataFrame([y_data]).to_csv("/mnt/c/Users/Kilian/Documents/LeafH2O/measurements/250522/results/leaf_water_content_calc.csv", mode='a', header=False, index=False)
            
            
            print(y_data)
            # Plotten
            #plt.plot(Meas, y_data, label=name, ls='--', marker = 'o', markersize = 10)
        except Exception as e:
            pass
            # print(f"Fehler beim Verarbeiten von {row_name}: {e}")
    
    # Diagramm anzeigen
    # plt.ylabel('Leaf water content [g/cm^2]')
    # plt.xticks(rotation=45) 
    # #plt.yscale('log')
    # plt.legend()
    # plt.tight_layout()
    # plt.show()