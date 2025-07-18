import laspy
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
import csv
import re


input_folder = "/mnt/c/Users/Kilian/Documents/LeafH2O/measurements/250522/leaves/"
output_folder = "/mnt/c/Users/Kilian/Documents/LeafH2O/measurements/250522/results/00_processed_abs"
os.makedirs(output_folder, exist_ok=True)

# Define a Gaussian function
def gaussian(x, amp, mu, sigma):
    return amp * np.exp(-(x - mu)**2 / (2 * sigma**2))

results = []

# Walk through the input folder and subfolders
for root, dirs, files in os.walk(input_folder):
    # Remove any subdirectories with 'back' in their name (case-insensitive)
    dirs[:] = [d for d in dirs if "back" not in d.lower()]
    # Skip folders with 'back' in their name (case-insensitive)
    if "back" in os.path.basename(root).lower():
        continue
    for file in files:
        if file.lower().endswith('.las'):
            file_path = os.path.join(root, file)
            try:
                # Check if the immediate parent directory of the file is named "abs"
                if os.path.basename(root) != "abs":
                    continue

                las = laspy.read(file_path)
                intensity = np.array(las.Intensity_corr)
                # Compute histogram
                counts, bin_edges = np.histogram(intensity, bins=50)
                bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

                # Initial guess for parameters: amplitude, mean, stddev
                init_guess = [counts.max(), bin_centers[np.argmax(counts)], np.std(intensity)]

                # Fit the Gaussian
                popt, pcov = curve_fit(gaussian, bin_centers, counts, p0=init_guess)

                x_fit = np.linspace(bin_centers.min(), bin_centers.max(), 500)
                y_fit = gaussian(x_fit, *popt)

                x_max = x_fit[np.argmax(y_fit)]

                # Save plot
                plt.figure()
                plt.hist(intensity, bins=50, alpha=0.6, label='Histogram')
                plt.plot(x_fit, y_fit, 'r-', label='Gaussian fit')
                plt.xlabel('Corrected Intensity')
                plt.ylabel('Count')
                plt.title(f'Gaussian Fit for {os.path.basename(file)}')
                plt.legend()
                plot_path = os.path.join(output_folder, os.path.splitext(os.path.basename(file))[0] + ".png")
                plt.savefig(plot_path)
                plt.close()

                # Extract measurement number from basename (e.g., 'M1_...' -> 1)
                basename = os.path.basename(file)
                match = re.search(r'M(\d+)', basename, re.IGNORECASE)
                measurement = int(match.group(1)) if match else ''
                # Extract distance (e.g., '10m' or '27m') from filename
                distance_match = re.search(r'(10m|27m)', basename, re.IGNORECASE)
                distance = distance_match.group(1) if distance_match else ''
                # Store result with measurement and distance
                results.append([os.path.basename(file), measurement, distance, x_max])
                print(f"{file} is processed")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

# Write results to CSV
csv_path = os.path.join(output_folder, "abs_x_max.csv")
with open(csv_path, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['basename', 'measurement', 'distance', 'x_max'])
    writer.writerows(results)
