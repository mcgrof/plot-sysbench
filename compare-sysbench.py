#!/usr/bin/python3

import pandas as pd
import matplotlib.pyplot as plt
import re
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

# Read and parse both sysbench output files
tps_data_1 = read_sysbench_output('sysbench_output_doublewrite.txt')
tps_data_2 = read_sysbench_output('sysbench_output_nodoublewrite.txt')

# Determine the maximum time value to decide if we need to use hours or seconds
max_time_in_seconds = max(max(tps_data_1, key=lambda x: x[0])[0], max(tps_data_2, key=lambda x: x[0])[0])
use_hours = max_time_in_seconds > 2 * 3600

# Convert times if necessary
if use_hours:
    tps_data_1 = [(time / 3600, tps) for time, tps in tps_data_1]
    tps_data_2 = [(time / 3600, tps) for time, tps in tps_data_2]
    time_label = 'Time (hours)'
else:
    time_label = 'Time (seconds)'

# Create pandas DataFrames
df1 = pd.DataFrame(tps_data_1, columns=[time_label, 'TPS'])
df2 = pd.DataFrame(tps_data_2, columns=[time_label, 'TPS'])

# Plot the TPS values
plt.figure(figsize=(30, 12))

plt.plot(df2[time_label], df2['TPS'], 'ro', markersize=2, label='innodb_doublewrite=ON')
plt.plot(df1[time_label], df1['TPS'], 'go', markersize=2, label='innodb_doublewrite=OFF')

plt.title('Transactions Per Second (TPS) Over Time')
plt.xlabel(time_label)
plt.ylabel('TPS')
plt.grid(True)
# Try plotting without this to zoom in
plt.ylim(0)
plt.legend()
plt.tight_layout()
plt.savefig('a_vs_b.png')
#plt.show()
