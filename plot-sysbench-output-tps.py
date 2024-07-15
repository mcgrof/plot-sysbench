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

# Read the sysbench output file
with open('sysbench_output.txt', 'r') as file:
    lines = file.readlines()

# Use ThreadPoolExecutor to parse lines concurrently
with ThreadPoolExecutor() as executor:
    results = list(executor.map(parse_line, lines))

# Filter out None results
tps_data = [result for result in results if result is not None]

# Determine if we need to use hours or seconds based on the maximum time value
max_time_in_seconds = max(tps_data, key=lambda x: x[0])[0]
use_hours = max_time_in_seconds > 2 * 3600

# Convert times if necessary
if use_hours:
    tps_data = [(time / 3600, tps) for time, tps in tps_data]
    time_label = 'Time (hours)'
else:
    time_label = 'Time (seconds)'

# Create a pandas DataFrame
df = pd.DataFrame(tps_data, columns=[time_label, 'TPS'])

# Plot the TPS values
plt.figure(figsize=(30, 12))
plt.plot(df[time_label], df['TPS'], 'o', markersize=2)
plt.title('Transactions Per Second (TPS) Over Time')
plt.xlabel(time_label)
plt.ylabel('TPS')
plt.grid(True)
# Plot without this to zoom in
plt.ylim(0)
plt.tight_layout()
plt.savefig('tps_over_time.png')
#plt.show()
