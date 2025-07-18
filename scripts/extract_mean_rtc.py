import laspy
import numpy as np
import os
import csv
import sys
import re

def extract_intensity_mean_from_las(file_path):
    las = laspy.read(file_path)
    intensity = np.array(las.Intensity_corr)  # Convert to NumPy array
    intensity_mean = np.mean(intensity)
    intensity_median = np.median(intensity)
    return intensity_mean, intensity_median

def find_las_files_in_rtc_folders(root_dir):
    las_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Only process folders named exactly 'rtc'
        if os.path.basename(dirpath) == "rtc":
            for filename in filenames:
                if filename.lower().endswith('.las'):
                    las_files.append(os.path.join(dirpath, filename))
    return las_files

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_mean.py <root_directory> <output_csv>")
        sys.exit(1)
    root_dir = sys.argv[1]
    output_csv = sys.argv[2]

    las_files = find_las_files_in_rtc_folders(root_dir)
    results = []

    for file_path in las_files:
        try:
            mean, median = extract_intensity_mean_from_las(file_path)
            # Extract measurement number from basename (e.g., '1Meas_...' or '1Mes_...' -> 1)
            basename = os.path.basename(file_path)
            match = re.match(r"(\d+)[Mm](?:eas|es)", basename, re.IGNORECASE)
            measurement = int(match.group(1)) if match else ''
            # Extract distance (e.g., '10m' or '27m') from filename
            distance_match = re.search(r'(10m|27m)', basename, re.IGNORECASE)
            distance = distance_match.group(1) if distance_match else ''
            results.append([file_path, measurement, distance, float(mean), float(median)])
            print(f"Processed: {file_path} | Mean Intensity_corr: {mean:.3f}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['filename', 'measurement', 'distance', 'mean_intensity_corr', "median_intensity_corr"])
        writer.writerows(results)

    print(f"Results saved to {output_csv}")
