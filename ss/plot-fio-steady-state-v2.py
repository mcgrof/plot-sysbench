#!/usr/bin/python3

import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Load the fio JSON output
with open('ss_iops.json', 'r') as file:
    iops_data = json.load(file)

# Extract the number of entries dynamically for each job
num_entries_job0 = len(iops_data['jobs'][0]['steadystate']['data']['iops'])
num_entries_job1 = len(iops_data['jobs'][1]['steadystate']['data']['iops'])

# Initialize lists to store the data
time_data_job0 = list(range(1, num_entries_job0 + 1))
time_data_job1 = list(range(1, num_entries_job1 + 1))

# Extract IOPS and bandwidth data for both jobs
iops_mean_data = iops_data['jobs'][0]['steadystate']['data']['iops']
bw_mean_data = iops_data['jobs'][0]['steadystate']['data']['bw']
iops_slope_data = iops_data['jobs'][1]['steadystate']['data']['iops']
bw_slope_data = iops_data['jobs'][1]['steadystate']['data']['bw']

# Create DataFrames
df_iops_mean = pd.DataFrame({'Time (seconds)': time_data_job0, 'Mean IOPS': iops_mean_data})
df_bw_mean = pd.DataFrame({'Time (seconds)': time_data_job0, 'Mean Bandwidth (KB/s)': bw_mean_data})
df_iops_slope = pd.DataFrame({'Time (seconds)': time_data_job1, 'Slope IOPS': iops_slope_data})
df_bw_slope = pd.DataFrame({'Time (seconds)': time_data_job1, 'Slope Bandwidth (KB/s)': bw_slope_data})

# Function to format bandwidth values
def human_readable_bandwidth(x, pos):
    if x >= 1e9:
        return f'{x*1e-9:.1f} GB/s'
    elif x >= 1e6:
        return f'{x*1e-6:.1f} MB/s'
    elif x >= 1e3:
        return f'{x*1e-3:.1f} KB/s'
    else:
        return f'{x:.1f} B/s'

# Plot the data
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot IOPS on the left y-axis
ax1.plot(df_iops_mean['Time (seconds)'], df_iops_mean['Mean IOPS'], 'g-', label='Mean IOPS')
ax1.plot(df_iops_slope['Time (seconds)'], df_iops_slope['Slope IOPS'], 'g--', label='Slope IOPS')
ax1.set_xlabel('Time (seconds)')
ax1.set_ylabel('IOPS', color='g')
ax1.tick_params(axis='y', labelcolor='g')
ax1.grid(True)

# Instantiate a second y-axis to plot bandwidth
ax2 = ax1.twinx()
ax2.plot(df_bw_mean['Time (seconds)'], df_bw_mean['Mean Bandwidth (KB/s)'], 'b-', label='Mean Bandwidth (KB/s)')
ax2.plot(df_bw_slope['Time (seconds)'], df_bw_slope['Slope Bandwidth (KB/s)'], 'b--', label='Slope Bandwidth (KB/s)')
ax2.set_ylabel('Bandwidth', color='b')
ax2.tick_params(axis='y', labelcolor='b')
ax2.yaxis.set_major_formatter(FuncFormatter(human_readable_bandwidth))

# Add legends
fig.tight_layout()
fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9), bbox_transform=ax1.transAxes)

plt.title('Steady-State IOPS and Bandwidth Over Time')
plt.savefig('steady_state_iops.png')
plt.show()
