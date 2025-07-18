import pandas as pd
import glob
import os
import re
import matplotlib.pyplot as plt
import math

# # Only include result CSVs, not the water content file
# csv_files = [
#     f for f in glob.glob(r"C:\Users\Kilian\Documents\LeafH2O\measurements\250522\results\*.csv")
#     if "leaf_water_content" not in os.path.basename(f).lower()
# ]
# dfs = [pd.read_csv(f) for f in csv_files]
# df = pd.concat(dfs, ignore_index=True)

# def parse_filename(fname):
#     base = os.path.basename(fname)
#     match = re.match(r"(\d+)Meas_(\d+m).*_(\w+)\\.las", base)
#     if match:
#         meas, dist, leaf = match.groups()
#         return meas, dist, leaf
#     parts = base.split('_')
#     if len(parts) >= 3:
#         if parts[0].endswith('Meas'):
#             meas_num = parts[0][:-4] if parts[0][:-4].isdigit() else parts[0]
#         else:
#             meas_num = parts[0]
#         return meas_num, parts[1], parts[-1].replace('.las', '')
#     return None, None, None

# df[['measurement', 'distance', 'leaf_kind']] = df['filename'].apply(
#     lambda x: pd.Series(parse_filename(x))
# )

# pivot = df.pivot_table(
#     index=['leaf_kind', 'measurement'],
#     columns='distance',
#     values='mean_intensity_corr'
# ).reset_index()

# pivot.to_csv('combined_by_leaf_and_distance.csv', index=False)


###### ADD leaf water content file ######

refl_data = pd.read_csv("combined_by_leaf_and_distance.csv")

# Read the CSV, skipping the first 4 rows (adjust if needed)
lwc = pd.read_csv(
    r'C:\Users\Kilian\Documents\LeafH2O\measurements\250522\leaf_water_content.csv',
    sep=';',
    skiprows=4,
    header=None)

# The file has 11 columns, so set 11 column names
lwc.columns = [
    'leaf_kind', 'before1', 'after1', 'before2', 'before3', 'after_end1', 'after_end2', 'leaf_area', 'empty1', 'empty2', 'empty3'
]

lwc["leaf_kind"] = lwc["leaf_kind"].str.lower().str.replace(" ", "")

leaf_kind_mapping = {
    "linde1": "lindei",
    "linde2": "lindeii",
    "linde3": "lindeiii",
    "ahorn-gross": "ahorngross"
}

refl_data["leaf_kind"] = refl_data["leaf_kind"].replace(leaf_kind_mapping)
lwc["leaf_kind"] = lwc["leaf_kind"].replace(leaf_kind_mapping)

# Merge refl_data and lwc on leaf_kind
merged = pd.merge(refl_data, lwc, on="leaf_kind", how="left")


def get_weight(row):
    meas = str(row['measurement'])
    col = f'before{meas}'
    return row.get(col, None)

merged['weight'] = merged.apply(get_weight, axis=1)

merged['weight'] = merged['weight'].astype(str).str.replace(',', '.').str.replace(' ', '')
merged['weight'] = pd.to_numeric(merged['weight'], errors='coerce')
merged['leaf_area'] = merged['leaf_area'].astype(str).str.replace(',', '.').str.replace(' ', '')
merged['leaf_area'] = pd.to_numeric(merged['leaf_area'], errors='coerce')

merged["wc"] = merged["weight"] / merged["leaf_area"]


valid_leaf_kinds = merged.groupby('leaf_kind')['measurement'].nunique()
valid_leaf_kinds = valid_leaf_kinds[valid_leaf_kinds > 2].index
filtered = merged[merged['leaf_kind'].isin(valid_leaf_kinds)]

# Use filtered DataFrame for plotting
leaf_kinds = filtered['leaf_kind'].unique()
num_leaf_kinds = len(leaf_kinds)

ncols = 2
nrows = (num_leaf_kinds + 1) // ncols  # Ensures enough rows for all leaf kinds
fig, axes = plt.subplots(nrows, ncols, figsize=(12, 4 * nrows), sharex=True)
axes = axes.flatten()

if num_leaf_kinds == 1:
    axes = [axes]  # Ensure axes is iterable

distances = ['10m', '27m']
colors = {'10m': 'g', '27m': 'r'}
markers = {'10m': 'o', '27m': 's'}

for ax, leaf in zip(axes, leaf_kinds):
    data = filtered[filtered['leaf_kind'] == leaf]
    ax2 = ax.twinx()
    # Plot reflectance for 10m and 27m
    ax.plot(data['measurement'], data['10m'], color='g', marker='o', label='Reflectance 10m')
    ax.plot(data['measurement'], data['27m'], color='r', marker='s', label='Reflectance 27m')
    # Plot water content (same for both, but dashed lines for distinction)
    ax2.plot(data['measurement'], data['wc'], color='g', marker='o', linestyle='--', label='WC 10m')
    ax2.plot(data['measurement'], data['wc'], color='r', marker='s', linestyle='--', label='WC 27m')
    ax.set_title(f'Leaf Kind: {leaf}')
    ax.set_ylabel('Reflectance')
    ax2.set_ylabel('Water Content')
    ax.set_xlabel('Measurement')
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')

for i in range(len(leaf_kinds), len(axes)):
    fig.delaxes(axes[i])

# plt.tight_layout()
# plt.show()

corr_10m_27m = filtered[['10m', '27m']].corr().iloc[0, 1]
print(f"Correlation between 10m and 27m reflectance (only leaf kinds with 3 measurements): {corr_10m_27m:.3f}")

# corr_matrix = filtered[['10m', '27m', 'wc', 'weight']].corr()
# corr_matrix = filtered[['10m', '27m', 'wc', 'weight']].corr(method='spearman')
corr_matrix = filtered[['10m', '27m', 'wc', 'weight']].corr(method='kendall')
print("Correlation matrix for 10m, 27m, wc, and weight (only leaf kinds with 3 measurements):")
print(corr_matrix)

import seaborn as sns
import matplotlib.pyplot as plt

sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title("Correlation Matrix (3 measurements only)")
plt.show()

# Correlation per leaf_kind for all three methods
cols = ['10m', '27m', 'wc', 'weight']
methods = ['pearson', 'spearman', 'kendall']

for method in methods:
    print(f"\n=== Correlation method: {method.title()} ===")
    for leaf in filtered['leaf_kind'].unique():
        data = filtered[filtered['leaf_kind'] == leaf]
        if len(data) > 1:
            corr = data[cols].corr(method=method)
            print(f"\nCorrelation matrix for leaf_kind '{leaf}':")
            print(corr)
        else:
            print(f"\nNot enough data for leaf_kind '{leaf}' to compute correlation.")

