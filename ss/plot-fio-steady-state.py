#!/usr/bin/python3

import json
import pandas as pd
import matplotlib.pyplot as plt

# Load the fio JSON output
with open('ss_iops.json', 'r') as file:
    iops_data = json.load(file)

# Extract the number of entries dynamically
num_entries = len(iops_data['jobs'][0]['steadystate']['data']['iops'])

# Initialize lists to store the data
time_data = list(range(1, num_entries + 1))

# Extract IOPS and bandwidth data for both jobs
iops_mean_data = iops_data['jobs'][0]['steadystate']['data']['iops']
bw_mean_data = iops_data['jobs'][0]['steadystate']['data']['bw']
iops_slope_data = iops_data['jobs'][1]['steadystate']['data']['iops']
bw_slope_data = iops_data['jobs'][1]['steadystate']['data']['bw']

# Create DataFrames
df_iops_mean = pd.DataFrame({'Time (seconds)': time_data, 'Mean IOPS': iops_mean_data})
df_bw_mean = pd.DataFrame({'Time (seconds)': time_data, 'Mean Bandwidth (KB/s)': bw_mean_data})
df_iops_slope = pd.DataFrame({'Time (seconds)': time_data, 'Slope IOPS': iops_slope_data})
df_bw_slope = pd.DataFrame({'Time (seconds)': time_data, 'Slope Bandwidth (KB/s)': bw_slope_data})

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
ax2.set_ylabel('Bandwidth (KB/s)', color='b')
ax2.tick_params(axis='y', labelcolor='b')

# Add legends
fig.tight_layout()
fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9), bbox_transform=ax1.transAxes)

plt.title('Steady-State IOPS and Bandwidth Over Time')
plt.savefig('steady_state_iops.png')
#plt.show()

