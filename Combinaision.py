import os
import pandas as pd
from math import sqrt
import numpy as np
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt

def extract_columns_data(file_path):
    try:
        df = pd.read_excel(file_path)
        columns_data = {col: df[col].tolist() for col in df.columns}
        return columns_data
    except Exception as e:
        print(f"Error reading the file {file_path}: {e}")
        return None

def calculate_correct_incorrect(predictions):
    correct = sum(1 for pred in predictions if pred == 1)
    incorrect = sum(1 for pred in predictions if pred == 0)
    return [correct, incorrect]

def average_correct_species_position(L):
    zeros = L.count(0)
    ones = L.count(1)
    twos = L.count(2)
    threes = L.count(3)
    fours = L.count(4)
    fives = L.count(5)
    avg = (5 * ones + 4 * twos + 3 * threes + 2 * fours + fives) / (ones + twos + threes + fours + fives + zeros)
    return avg, len(L)

def compute_statistics(data):
    avg = np.mean(data)
    std_var = np.std(data)
    ci_low = avg - 1.96 * std_var
    ci_high = avg + 1.96 * std_var
    return avg, std_var, (ci_low, ci_high)

def wald_confidence_interval(x):
    z = 1.96
    p = sum(1 for i in x if i == 1) / len(x)
    return (p - z * sqrt(p * (1 - p) / len(x)), p + z * sqrt(p * (1 - p) / len(x)))

# Main script
data_folder_path = "./data"
excel_files = [os.path.join(data_folder_path, f) for f in os.listdir(data_folder_path) if f.endswith('.xlsx')]

species_results = []
genus_results = []
wald_species_intervals = []
wald_genus_intervals = []
overall_species_averages = []
G_column_stats = []
H_column_stats = []

if not excel_files:
    print("No Excel files found in the folder.")
else:
    for file_path in excel_files:
        columns_data = extract_columns_data(file_path)
        if columns_data:
            L = [columns_data[col] for col in columns_data]
            SpeciesFirst = [int(bool(i)) for i in L[2]]
            GenusFirst = [int(bool(i)) for i in L[3]]
            CorrectSpeciesPosition = [int(i) for i in L[4]]
            G_column = [float(i) for i in L[6]]
            H_column = [float(i) for i in L[7]]

            G_avg, G_std, _ = compute_statistics(G_column)
            H_avg, H_std, _ = compute_statistics(H_column)
            G_column_stats.append((G_avg, G_std))
            H_column_stats.append((H_avg, H_std))

            species_results.append(calculate_correct_incorrect(SpeciesFirst))
            genus_results.append(calculate_correct_incorrect(GenusFirst))

            sf_wald = wald_confidence_interval(SpeciesFirst)
            gf_wald = wald_confidence_interval(GenusFirst)
            cs_avg, _ = average_correct_species_position(CorrectSpeciesPosition)
            wald_species_intervals.append(sf_wald)
            wald_genus_intervals.append(gf_wald)
            overall_species_averages.append(cs_avg)

# Ensure consistent plotting
file_names = [os.path.basename(file_path) for file_path in excel_files]
if len(file_names) != len(species_results):
    file_names = file_names[:len(species_results)]

# Visualization: Combined Average and Standard Deviation for G and Confidence Level for True Species (if applicable)s
fig, ax_avg = plt.subplots()
bar_width = 0.35
x = np.arange(len(file_names))

# Plot G column averages with error bars (standard deviation)
ax_avg.bar(x - bar_width/2, [stat[0] for stat in G_column_stats], bar_width, yerr=[stat[1] for stat in G_column_stats], capsize=5, label='Confidence Level of First Species Recommendation', color='blue', alpha=0.7)

# Plot H column averages with error bars (standard deviation)
ax_avg.bar(x + bar_width/2, [stat[0] for stat in H_column_stats], bar_width, yerr=[stat[1] for stat in H_column_stats], capsize=5, label='Confidence Level of True Species if Suggested', color='orange', alpha=0.7)

ax_avg.set_title('Average and Standard Deviation for G and H Columns')
ax_avg.set_xlabel('Files')
ax_avg.set_ylabel('Average Value')
ax_avg.set_xticks(x)
ax_avg.set_xticklabels(file_names, rotation=45, ha='right')
ax_avg.legend()
plt.tight_layout()
plt.show()

# Plotting existing graphs
x_species = np.arange(len(species_results))
fig, ax_species = plt.subplots()
ax_species.bar(x_species - 0.2, [correct for correct, _ in species_results], width=0.4, label='Correct', color='green')
ax_species.bar(x_species + 0.2, [correct + incorrect for correct, incorrect in species_results], width=0.4, label='Total', color='gray')
ax_species.set_title('Species Classification Results')
ax_species.set_xticks(x_species)
ax_species.set_xticklabels(file_names, rotation=45, ha='right')
ax_species.legend()
plt.tight_layout()
plt.show()

x_genus = np.arange(len(genus_results))
fig, ax_genus = plt.subplots()
ax_genus.bar(x_genus - 0.2, [correct for correct, _ in genus_results], width=0.4, label='Correct', color='green')
ax_genus.bar(x_genus + 0.2, [correct + incorrect for correct, incorrect in genus_results], width=0.4, label='Total', color='gray')
ax_genus.set_title('Genus Classification Results')
ax_genus.set_xticks(x_genus)
ax_genus.set_xticklabels(file_names, rotation=45, ha='right')
ax_genus.legend()
plt.tight_layout()
plt.show()

fig, ax = plt.subplots()
ax.boxplot([[low, high] for low, high in wald_species_intervals], positions=range(len(file_names)), patch_artist=True)
ax.set_title('Wald Confidence Intervals for Species')
ax.set_xticks(range(len(file_names)))
ax.set_xticklabels(file_names, rotation=45, ha='right')
plt.tight_layout()
plt.show()

fig, ax = plt.subplots()
ax.boxplot([[low, high] for low, high in wald_genus_intervals], positions=range(len(file_names)), patch_artist=True)
ax.set_title('Wald Confidence Intervals for Genus')
ax.set_xticks(range(len(file_names)))
ax.set_xticklabels(file_names, rotation=45, ha='right')
plt.tight_layout()
plt.show()

fig, ax_avg = plt.subplots()
ax_avg.bar(range(len(file_names)), overall_species_averages, color='green')
ax_avg.set_title('Average Scores for Species per File')
ax_avg.set_xticks(range(len(file_names)))
ax_avg.set_xticklabels(file_names, rotation=45, ha='right')
plt.tight_layout()
plt.show()
