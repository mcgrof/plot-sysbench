#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import re
import argparse
from concurrent.futures import ThreadPoolExecutor

# Function to parse a line and extract time and TPS
def parse_line(line):
    match = re.search(r'\[\s*(\d+)s\s*\].*?tps:\s*([\d.]+)', line)
    if match:
        time_in_seconds = int(match.group(1))
        tps = float(match.group(2))
        return time_in_seconds, tps
    return None

# Function to read and parse sysbench output file
def read_sysbench_output(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(parse_line, lines))

    return [result for result in results if result is not None]

# Function to list available matplotlib themes
def list_themes():
    print("Available matplotlib themes:")
    for style in plt.style.available:
        print(style)

# Main function
def main():
    parser = argparse.ArgumentParser(description='Compare sysbench outputs.')
    parser.add_argument('files', type=str, nargs='*', help='Sysbench output files')
    parser.add_argument('--legends', type=str, nargs='*', default=[], help='Legends for the files')
    parser.add_argument('--title', type=str, default='Transactions Per Second (TPS) Over Time', help='Title')
    parser.add_argument('--ylabel', type=str, default='TPS', help='Y axis label')
    parser.add_argument('--output', type=str, default='a_vs_b.png', help='Filename output')
    parser.add_argument('--theme', type=str, default='dark_background', help='Matplotlib theme to use')
    parser.add_argument('--list-themes', action='store_true', help='List available matplotlib themes')
    parser.add_argument('--report-interval', type=int, default=1, help='Time interval in seconds for reporting')
    parser.add_argument("--show", action="store_true", help="Show plots")

    args = parser.parse_args()

    if args.list_themes:
        list_themes()
        return

    colors = [
        "w*",  # White stars
        "r*",  # Red stars
        "g*",  # Green stars
        "b*",  # Blue stars
        "c*",  # Cyan stars
        "m*",  # Magenta stars
        "y*",  # Yellow stars
        "w^",  # White triangles
        "r^",  # Red triangles
        "g^",  # Green triangles
        "b^",  # Blue triangles
        "c^",  # Cyan triangles
        "m^",  # Magenta triangles
        "y^",  # Yellow triangles
        "wo",  # White circles
        "ro",  # Red circles
        "go",  # Green circles
        "bo",  # Blue circles
        "co",  # Cyan circles
        "mo",  # Magenta circles
        "yo",  # Yellow circles
    ]

    if len(args.files) > len(colors):
        print("Max number of files exceeded (Limit: {})".format(len(colors)))
        return

    plt.style.use(args.theme)
    plt.figure(figsize=(30, 12))
    time_label = 'Time (seconds)'

    # Determine the maximum time value to decide if we need to use hours or seconds
    max_time_in_seconds = 0
    all_data = []
    for file in args.files:
        _data = read_sysbench_output(file)
        _data = [(time * args.report_interval, tps) for time, tps in _data]
        all_data.append(_data)
        max_time_in_seconds = max(max_time_in_seconds, max(_data, key=lambda x: x[0])[0])

    # Convert times if necessary
    use_hours = max_time_in_seconds > 2 * 3600
    if use_hours:
        time_label = 'Time (hours)'

    for i, _data in enumerate(all_data, 1):
        if use_hours:
            _data = [(time / 3600, tps) for time, tps in _data]
        _dataf = pd.DataFrame(_data, columns=[time_label, 'TPS'])
        plt.plot(_dataf[time_label], _dataf['TPS'], colors[i-1], markersize=2, label=args.legends[i-1])

    plt.title(args.title)
    plt.xlabel(time_label)
    plt.ylabel(args.ylabel)
    plt.grid(True)
    # Try plotting without this to zoom in
    plt.ylim(0)
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.output)
    if args.show:
        plt.show()

if __name__ == '__main__':
    main()
