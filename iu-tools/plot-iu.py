#!/usr/bin/env python3
# SPDX-License-Identifier: copyleft-next-0.3.1
#
# Histogram plotting and comparison tool for blkalgn and nvmeiuwaf.

import argparse
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def load_json_data(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)
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


def plot_histograms(args):
    data1 = load_json_data(args.json_input1)
    data2 = load_json_data(args.json_input2) if args.json_input2 else None
    legend1 = args.legend1
    legend2 = args.legend2
    output_file = args.output
    theme = "dark_background"
    color1 = args.color1
    color2 = args.color2
    if args.theme:
        theme = args.theme

    plt.style.use(theme)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

    def plot_histogram(ax, data1, data2, title, xlabel, ylabel, color1, color2):
        keys = sorted(set(data1.keys()).union(set(data2.keys() if data2 else [])))
        formatted_keys = [format_size(k) for k in keys]
        values1 = [data1.get(k, 0) for k in keys]
        values2 = [data2.get(k, 0) for k in keys] if data2 else None

        bar_width = 0.35
        index = range(len(keys))

        ax.bar(index, values1, bar_width, label=legend1, color=color1)
        if values2:
            ax.bar(
                [i + bar_width for i in index],
                values2,
                bar_width,
                label=legend2,
                color=color2,
            )

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_xticks([i + bar_width / 2 for i in index])
        ax.set_xticklabels(formatted_keys, rotation=45)

        ax.yaxis.set_major_locator(
            ticker.MultipleLocator(max(values1 + (values2 if values2 else [])) // 5)
        )
        ax.yaxis.set_minor_locator(
            ticker.MultipleLocator(max(values1 + (values2 if values2 else [])) // 10)
        )

        ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        ax.legend()

    if "Block size" in data1:
        plot_histogram(
            ax1,
            data1["Block size"],
            data2["Block size"] if data2 and "Block size" in data2 else None,
            "Block Size Distribution",
            "Block Size",
            "Count",
            color1,
            color2,
        )

    if "Algn size" in data1:
        plot_histogram(
            ax2,
            data1["Algn size"],
            data2["Algn size"] if data2 and "Algn size" in data2 else None,
            "Alignment Size Distribution",
            "Alignment Size",
            "Count",
            color1,
            color2,
        )

    plt.tight_layout()
    plt.savefig(output_file)
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Histogram plotting tool for blkalgn and nvmeiuwaf JSON output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("json_input1", type=str, help="Path to primary JSON input file")
    parser.add_argument(
        "json_input2",
        type=str,
        nargs="?",
        help="Path to secondary JSON input file (optional)",
    )
    parser.add_argument(
        "--legend1",
        type=str,
        default="JSON Input 1",
        help="Legend for primary JSON input file",
    )
    parser.add_argument(
        "--legend2",
        type=str,
        default="JSON Input 2",
        help="Legend for secondary JSON input file",
    )
    parser.add_argument(
        "--color1", type=str, default="green", help="Color for primary JSON input file"
    )
    parser.add_argument(
        "--color2", type=str, default="red", help="Color for secondary JSON input file"
    )
    parser.add_argument(
        "--list-themes", action="store_true", help="List available plot themes"
    )
    parser.add_argument(
        "--theme",
        type=str,
        default="dark_background",
        help="Plot theme (default: dark_background)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="iu-alignment.png",
        help="Output file name (default: iu-alignment.png)",
    )
    args = parser.parse_args()
    if args.list_themes:
        print(plt.style.available)
        return

    plot_histograms(args)


if __name__ == "__main__":
    main()
