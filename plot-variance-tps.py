#!/usr/bin/python3
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from scipy.stats import norm

def extract_tps(filename):
    tps_values = []
    with open(filename, 'r') as file:
        for line in file:
            match = re.search(r'tps: (\d+\.\d+)', line)
            if match:
                tps_values.append(float(match.group(1)))
    return tps_values

def analyze_tps(tps_values):
    mean_tps = np.mean(tps_values)
    median_tps = np.median(tps_values)
    std_tps = np.std(tps_values)
    variance_tps = np.var(tps_values)
    return mean_tps, median_tps, std_tps, variance_tps

def print_statistics(label, tps_values):
    mean_tps, median_tps, std_tps, variance_tps = analyze_tps(tps_values)
    print(f'{label} Statistics:')
    print(f'Mean TPS: {mean_tps:.2f}')
    print(f'Median TPS: {median_tps:.2f}')
    print(f'Standard Deviation of TPS: {std_tps:.2f}')
    print(f'Variance of TPS: {variance_tps:.2f}\n')

def plot_histograms(tps_values1, tps_values2, legend1, legend2, color1, color2):
    plt.figure(figsize=(10, 6))
    bins = np.linspace(min(min(tps_values1), min(tps_values2)), max(max(tps_values1), max(tps_values2)), 30)
    plt.hist(tps_values1, bins=bins, alpha=0.5, color=color1, edgecolor='black', label=legend1)
    if tps_values2:
        plt.hist(tps_values2, bins=bins, alpha=0.5, color=color2, edgecolor='black', label=legend2)
    plt.title('Distribution of TPS Values')
    plt.xlabel('Transactions Per Second (TPS)')
    plt.ylabel('Frequency')
    plt.legend(loc='best')
    plt.grid(True)
    plt.savefig('histogram.png')
    plt.show()

def plot_box_plots(tps_values1, tps_values2, legend1, legend2, color1, color2):
    data = []
    labels = []
    data.append(tps_values1)
    labels.append(legend1)
    if tps_values2:
        data.append(tps_values2)
        labels.append(legend2)
    plt.figure(figsize=(10, 6))
    box = plt.boxplot(data, labels=labels, patch_artist=True)
    colors = [color1, color2]
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    plt.title('Box Plot of TPS Values')
    plt.ylabel('Transactions Per Second (TPS)')
    plt.grid(True)
    plt.savefig('box_plot.png')
    plt.show()

def plot_density_plots(tps_values1, tps_values2, legend1, legend2, color1, color2):
    plt.figure(figsize=(10, 6))
    sns.kdeplot(tps_values1, shade=True, label=legend1, color=color1)
    if tps_values2:
        sns.kdeplot(tps_values2, shade=True, label=legend2, color=color2)
    plt.title('Density Plot of TPS Values')
    plt.xlabel('Transactions Per Second (TPS)')
    plt.ylabel('Density')
    plt.legend(loc='best')
    plt.grid(True)
    plt.savefig('density_plot.png')
    plt.show()

def plot_combined_hist_density(tps_values1, tps_values2, legend1, legend2, color1, color2):
    plt.figure(figsize=(10, 6))
    bins = np.linspace(min(min(tps_values1), min(tps_values2)), max(max(tps_values1), max(tps_values2)), 30)
    plt.hist(tps_values1, bins=bins, alpha=0.3, color=color1, edgecolor='black', label=f'Histogram {legend1}', density=True)
    if tps_values2:
        plt.hist(tps_values2, bins=bins, alpha=0.3, color=color2, edgecolor='black', label=f'Histogram {legend2}', density=True)
    sns.kdeplot(tps_values1, shade=False, label=f'Density {legend1}', color=color1)
    if tps_values2:
        sns.kdeplot(tps_values2, shade=False, label=f'Density {legend2}', color=color2)
    plt.title('Combined Histogram and Density Plot of TPS Values')
    plt.xlabel('Transactions Per Second (TPS)')
    plt.ylabel('Frequency/Density')
    plt.legend(loc='best')
    plt.grid(True)
    plt.savefig('combined_hist_density.png')
    plt.show()

def plot_bell_curve(tps_values1, tps_values2, legend1, legend2, color1, color2):
    plt.figure(figsize=(10, 6))
    mean1, std1 = np.mean(tps_values1), np.std(tps_values1)
    x1 = np.linspace(mean1 - 3*std1, mean1 + 3*std1, 100)
    plt.plot(x1, norm.pdf(x1, mean1, std1) * 100, label=f'Bell Curve {legend1}', color=color1)  # Multiplying by 100 for percentage

    if tps_values2:
        mean2, std2 = np.mean(tps_values2), np.std(tps_values2)
        x2 = np.linspace(mean2 - 3*std2, mean2 + 3*std2, 100)
        plt.plot(x2, norm.pdf(x2, mean2, std2) * 100, label=f'Bell Curve {legend2}', color=color2)  # Multiplying by 100 for percentage

    plt.title('Bell Curve (Normal Distribution) of TPS Values')
    plt.xlabel('Transactions Per Second (TPS)')
    plt.ylabel('Probability Density (%)')
    plt.legend(loc='best')
    plt.grid(True)
    plt.savefig('bell_curve.png')
    plt.show()

def plot_combined_hist_bell_curve(tps_values1, tps_values2, legend1, legend2, color1, color2):
    fig, ax1 = plt.subplots(figsize=(10, 6))

    bins = np.linspace(min(min(tps_values1), min(tps_values2)), max(max(tps_values1), max(tps_values2)), 30)
    ax1.hist(tps_values1, bins=bins, alpha=0.5, color=color1, edgecolor='black', label=legend1)
    if tps_values2:
        ax1.hist(tps_values2, bins=bins, alpha=0.5, color=color2, edgecolor='black', label=legend2)

    ax1.set_xlabel('Transactions Per Second (TPS)')
    ax1.set_ylabel('Frequency')
    ax1.legend(loc='upper left')
    ax1.grid(True)

    ax2 = ax1.twinx()
    mean1, std1 = np.mean(tps_values1), np.std(tps_values1)
    x1 = np.linspace(mean1 - 3*std1, mean1 + 3*std1, 100)
    ax2.plot(x1, norm.pdf(x1, mean1, std1) * 100, label=f'Bell Curve {legend1}', color=color1, linestyle='dashed')
    ax2.axvline(mean1, color=color1, linestyle='dotted', linewidth=2)
    ax2.axvline(mean1 - std1, color=color1, linestyle='dotted', linewidth=1)
    ax2.axvline(mean1 + std1, color=color1, linestyle='dotted', linewidth=1)

    if tps_values2:
        mean2, std2 = np.mean(tps_values2), np.std(tps_values2)
        x2 = np.linspace(mean2 - 3*std2, mean2 + 3*std2, 100)
        ax2.plot(x2, norm.pdf(x2, mean2, std2) * 100, label=f'Bell Curve {legend2}', color=color2, linestyle='dashed')
        ax2.axvline(mean2, color=color2, linestyle='dotted', linewidth=2)
        ax2.axvline(mean2 - std2, color=color2, linestyle='dotted', linewidth=1)
        ax2.axvline(mean2 + std2, color=color2, linestyle='dotted', linewidth=1)

    ax2.set_ylabel('Probability Density (%)')
    ax2.legend(loc='upper right')

    plt.title('Combined Histogram and Bell Curve of TPS Values')
    plt.savefig('combined_hist_bell_curve.png')
    plt.show()

def plot_variance_bars(variance1, variance2, legend1, legend2, color1, color2):
    plt.figure(figsize=(10, 6))
    labels = [legend1, legend2]
    variances = [variance1, variance2]
    colors = [color1, color2]

    plt.bar(labels, variances, color=colors)
    plt.title('Variance of TPS Values')
    plt.ylabel('Variance')
    plt.savefig('variance_bar.png')
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Analyze and compare TPS values from sysbench output files.')
    parser.add_argument('file1', help='First TPS file')
    parser.add_argument('legend1', help='Legend for the first TPS file')
    parser.add_argument('file2', nargs='?', default=None, help='Second TPS file (optional)')
    parser.add_argument('legend2', nargs='?', default=None, help='Legend for the second TPS file (optional)')
    parser.add_argument('--color1', default='cyan', help='Color for the first dataset (default: cyan)')
    parser.add_argument('--color2', default='orange', help='Color for the second dataset (default: orange)')

    args = parser.parse_args()

    plt.style.use('dark_background')  # Set the dark theme

    tps_values1 = extract_tps(args.file1)
    tps_values2 = extract_tps(args.file2) if args.file2 else None

    print_statistics(args.legend1, tps_values1)
    if tps_values2:
        print_statistics(args.legend2, tps_values2)

    plot_histograms(tps_values1, tps_values2, args.legend1, args.legend2 if args.legend2 else '', args.color1, args.color2)
    plot_box_plots(tps_values1, tps_values2, args.legend1, args.legend2 if args.legend2 else '', args.color1, args.color2)
    plot_density_plots(tps_values1, tps_values2, args.legend1, args.legend2 if args.legend2 else '', args.color1, args.color2)
    plot_combined_hist_density(tps_values1, tps_values2, args.legend1, args.legend2 if args.legend2 else '', args.color1, args.color2)
    plot_bell_curve(tps_values1, tps_values2, args.legend1, args.legend2 if args.legend2 else '', args.color1, args.color2)
    plot_combined_hist_bell_curve(tps_values1, tps_values2, args.legend1, args.legend2 if args.legend2 else '', args.color1, args.color2)

    # Plot variance bars
    _, _, _, variance1 = analyze_tps(tps_values1)
    if tps_values2:
        _, _, _, variance2 = analyze_tps(tps_values2)
        plot_variance_bars(variance1, variance2, args.legend1, args.legend2, args.color1, args.color2)
    else:
        plot_variance_bars(variance1, 0, args.legend1, '', args.color1, 'black')  # Use black for the second bar if there's only one dataset

if __name__ == '__main__':
    main()
