#!/usr/bin/env python3
# SPDX-License-Identifier: copyleft-next-0.3.1
#
# 3D Histogram plotting and comparison tool for blkalgn and nvmeiuwaf.

import argparse
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgba

def load_json_data(json_file):
    print(f"Loading data from {json_file}")
    with open(json_file, 'r') as f:
        data = json.load(f)
    print(f"Data loaded from {json_file}")
    return data

def format_size(size):
    """Convert size from log2 scale to human-readable format."""
    size = int(size)
    if size < 10:
        return f"{1 << size} bytes"
    elif size < 20:
        return f"{1 << (size - 10)}K"
    elif size < 30:
        return f"{1 << (size - 20)}M"
    else:
        return f"{1 << (size - 30)}G"

def get_all_keys(datasets, key_type):
    all_keys = set()
    for data, _, _ in datasets:
        for key in data.get(key_type, {}).keys():
            if key.isdigit():
                all_keys.add(int(key))
    return sorted(all_keys)

def plot_3d_histograms(datasets, legends, colors, output_file, theme='dark_background'):
    plt.style.use(theme)
    fig = plt.figure(figsize=(14, 7))

    def plot_3d_histogram(ax, datasets, key_type, title, xlabel, ylabel, zlabel, all_keys, max_value):
        formatted_keys = [format_size(k) for k in all_keys]
        xpos = np.arange(len(all_keys))
        ypos = np.zeros(len(all_keys))
        bar_width = 0.15

        print(f"Plotting 3D histogram for: {title}")
        print(f"All keys: {all_keys}")
        print(f"Max value: {max_value}")

        for i, (data, legend, color) in enumerate(datasets):
            print(f"Processing dataset: {legend}")
            values = np.array([data.get(key_type, {}).get(str(k), 0) if isinstance(data.get(key_type, {}).get(str(k), 0), (int, float)) else 0 for k in all_keys])
            print(f"Values: {values}")
            alpha_values = np.clip((max_value - values) / max_value, 0.1, 1.0) if max_value != 0 else np.ones_like(values)
            rgba_colors = [to_rgba(color, alpha=alpha) for alpha in alpha_values]
            zpos = np.zeros(len(all_keys)) + i
            for j, value in enumerate(values):
                if value == 0 and all_keys[j] < (1 << 14):  # Handle IOs smaller than 16K
                    print(f"Filling missing value at {all_keys[j]} with grey bar")
                    ax.bar3d(xpos[j] + i * bar_width, zpos[j], ypos[j], bar_width, 1, 1, color='grey', alpha=0.5, shade=True)
                else:
                    print(f"Plotting value {value} at {all_keys[j]} with color {rgba_colors[j]}")
                    ax.bar3d(xpos[j] + i * bar_width, zpos[j], ypos[j], bar_width, 1, value, color=rgba_colors[j], shade=True)

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(zlabel)
        ax.set_zlabel(ylabel)
        ax.set_xticks(xpos + bar_width * (len(datasets) - 1) / 2)
        ax.set_xticklabels(formatted_keys, rotation=45)
        ax.set_yticks(range(len(datasets)))
        ax.set_yticklabels([legend for _, legend, _ in datasets])

        ax.set_zlim(0, max_value)
        # Create custom legend handles
        custom_handles = [mpatches.Patch(color=color, label=legend) for _, legend, color in datasets]
        ax.legend(handles=custom_handles)

    all_keys_blk = get_all_keys(datasets, "Block size")
    all_keys_algn = get_all_keys(datasets, "Algn size")

    max_value_blk = max(
        (max((data.get("Block size", {}).get(str(k), 0) for k in all_keys_blk if isinstance(data.get("Block size", {}).get(str(k), 0), (int, float))), default=0))
        for data, _, _ in datasets
    )

    max_value_algn = max(
        (max((data.get("Algn size", {}).get(str(k), 0) for k in all_keys_algn if isinstance(data.get("Algn size", {}).get(str(k), 0), (int, float))), default=0))
        for data, _, _ in datasets
    )

    ax1 = fig.add_subplot(121, projection='3d')
    ax1.view_init(elev=20, azim=-60)  # Adjust the elevation and azimuth angles
    datasets_blk_size = [(data, legend, color) for data, legend, color in datasets]
    if datasets_blk_size:
        print("Plotting Block Size Distribution")
        plot_3d_histogram(ax1, datasets_blk_size, "Block size",
                          "Block Size Distribution", "Block Size", "Count", "Dataset", all_keys_blk, max_value_blk)

    ax2 = fig.add_subplot(122, projection='3d')
    ax2.view_init(elev=20, azim=-60)  # Adjust the elevation and azimuth angles
    datasets_blk_algn = [(data, legend, color) for data, legend, color in datasets]
    if datasets_blk_algn:
        print("Plotting Alignment Size Distribution")
        plot_3d_histogram(ax2, datasets_blk_algn, "Algn size",
                          "Alignment Size Distribution", "Alignment Size", "Count", "Dataset", all_keys_algn, max_value_algn)

    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")
    plt.show()

def main():
    parser = argparse.ArgumentParser(
        description="3D Histogram plotting tool for blkalgn and nvmeiuwaf JSON output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    for i in range(1, 7):
        parser.add_argument(
            f"--json{i}",
            type=str,
            help=f"Path to JSON input file {i}"
        )
        parser.add_argument(
            f"--legend{i}",
            type=str,
            default=f"JSON Input {i}",
            help=f"Legend for JSON input file {i}"
        )
        parser.add_argument(
            f"--color{i}",
            type=str,
            default=None,
            help=f"Color for JSON input file {i}"
        )
    parser.add_argument(
        "--list-themes", action='store_true', help="List available plot themes"
    )
    parser.add_argument(
        "--theme",
        type=str,
        default='dark_background',
        help="Plot theme (default: dark_background)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default='iu-alignment.png',
        help="Output file name (default: iu-alignment.png)"
    )
    args = parser.parse_args()
    if args.list_themes:
        print(plt.style.available)
        return

    datasets = []
    default_colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow']

    for i in range(1, 7):
        json_file = getattr(args, f'json{i}')
        if json_file:
            print(f"Loading JSON input {i}")
            data = load_json_data(json_file)
            color = getattr(args, f'color{i}') or default_colors[i - 1]
            datasets.append((data, getattr(args, f'legend{i}'), color))

    if not datasets:
        print("No JSON input files provided.")
        return

    legends = [legend for _, legend, _ in datasets]
    colors = [color for _, _, color in datasets]

    plot_3d_histograms(datasets, legends, colors, args.output, args.theme)

if __name__ == "__main__":
    main()
