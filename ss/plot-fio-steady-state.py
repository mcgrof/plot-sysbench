#!/usr/bin/python3
import argparse
import re
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Parse optional max values from command line arguments
parser = argparse.ArgumentParser(description='Plot FIO Steady-State Data')
parser.add_argument('--title-prefix', type=str, default='', help='Prefix for the title of the graph')
parser.add_argument('--iops-max', type=float, default=None, help='Maximum value for IOPS y-axis')
parser.add_argument('--bw-max', type=str, default=None, help='Maximum value for Bandwidth y-axis (e.g., 1.8GB/s, 8MB/s, 400KB/s, 500B/s')

args = parser.parse_args()

# Load the fio JSON output
files = ['ss_iops.json', 'ss_bw.json']
data = {}

for file in files:
    if os.path.exists(file):
        with open(file, 'r') as f:
            data[file] = json.load(f)

if not data:
    raise FileNotFoundError("No valid JSON files found. Please provide at least one of 'ss_iops.json' or 'ss_bw.json' or both.")

# Function to adjust the length of lists
def adjust_length(data_list, target_length):
    current_length = len(data_list)
    if current_length < target_length:
        data_list.extend([None] * (target_length - current_length))
    else:
        data_list = data_list[:target_length]
    return data_list

# Extract the number of entries dynamically for each job
num_entries_job0 = max(len(data[file]['jobs'][0]['steadystate']['data']['iops']) for file in data)
num_entries_job1 = max(len(data[file]['jobs'][1]['steadystate']['data']['iops']) for file in data)

# Initialize lists to store the data
time_data_job0 = list(range(1, num_entries_job0 + 1))
time_data_job1 = list(range(1, num_entries_job1 + 1))

# Determine the appropriate time unit
max_time = max(max(time_data_job0), max(time_data_job1))
if max_time >= 3600:
    time_unit = 'hours'
    time_factor = 3600
elif max_time >= 60:
    time_unit = 'minutes'
    time_factor = 60
else:
    time_unit = 'seconds'
    time_factor = 1

# Adjust the time data according to the chosen time unit
time_data_job0 = [t / time_factor for t in time_data_job0]
time_data_job1 = [t / time_factor for t in time_data_job1]

# Initialize DataFrames
df_iops_mean = pd.DataFrame({f'Time ({time_unit})': time_data_job0})
df_bw_mean = pd.DataFrame({f'Time ({time_unit})': time_data_job0})
df_iops_slope = pd.DataFrame({f'Time ({time_unit})': time_data_job1})
df_bw_slope = pd.DataFrame({f'Time ({time_unit})': time_data_job1})

# Populate DataFrames if corresponding files are found
if 'ss_iops.json' in data:
    iops_data = data['ss_iops.json']
    df_iops_mean['Mean IOPS'] = adjust_length(iops_data['jobs'][0]['steadystate']['data']['iops'], num_entries_job0)
    df_bw_mean['Mean Bandwidth (KB/s)'] = adjust_length(iops_data['jobs'][0]['steadystate']['data']['bw'], num_entries_job0)
    df_iops_slope['Slope IOPS'] = adjust_length(iops_data['jobs'][1]['steadystate']['data']['iops'], num_entries_job1)
    df_bw_slope['Slope Bandwidth (KB/s)'] = adjust_length(iops_data['jobs'][1]['steadystate']['data']['bw'], num_entries_job1)

if 'ss_bw.json' in data:
    bw_data = data['ss_bw.json']
    df_iops_mean['Mean IOPS (BW)'] = adjust_length(bw_data['jobs'][0]['steadystate']['data']['iops'], num_entries_job0)
    df_bw_mean['Mean Bandwidth (KB/s) (BW)'] = adjust_length(bw_data['jobs'][0]['steadystate']['data']['bw'], num_entries_job0)
    df_iops_slope['Slope IOPS (BW)'] = adjust_length(bw_data['jobs'][1]['steadystate']['data']['iops'], num_entries_job1)
    df_bw_slope['Slope Bandwidth (KB/s) (BW)'] = adjust_length(bw_data['jobs'][1]['steadystate']['data']['bw'], num_entries_job1)

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

# Our color palette
colors = {
    'red': '#FF0000',  # Red
    'green': '#00FF00',  # Green
    'blue': '#0000FF',  # Blue
    'pink': '#FFC0CB',  # Pink
    'yellow': '#FFFF00',  # Yellow
    'light_red': '#DFE3E8',  # Light Gray
    'light_yellow': '#1428A0',  # Blue
    'purple': '#1428A0',  # Purpelish
    'cyan': '#00FFFF',  # Cyan
    'light_blue': '#76C7C0', # Light Blue
    'light_green': '#90EE90', # Light Green
    'grey': '#808080', # Grey
    'light_grey': '#D3D3D3', # Light Grey
    'contrast_red': '#E4002B',  # Contrasting Red
    'contrast_yellow': '#FFC72C',  # Contrasting Yellow
    'contrast_blue': '#0057B8',  # Contrasting Blue
}

# Plot the data
fig, ax1 = plt.subplots(figsize=(28, 16))  # Increased the figure size
fig.patch.set_facecolor('black')  # Set the background color to black
ax1.set_facecolor('black')  # Set the plot background color to black

# Plot IOPS on the left y-axis
if 'Mean IOPS' in df_iops_mean:
    ax1.plot(df_iops_mean[f'Time ({time_unit})'], df_iops_mean['Mean IOPS'], 'o', markersize=2, color=colors['red'], label='Mean IOPS (ss_iops)', alpha=0.6)
if 'Slope IOPS' in df_iops_slope:
    ax1.plot(df_iops_slope[f'Time ({time_unit})'], df_iops_slope['Slope IOPS'], 'o', markersize=1, color=colors['contrast_yellow'], label='Slope IOPS (ss_iops)', alpha=0.4)
if 'Mean IOPS (BW)' in df_iops_mean:
    ax1.plot(df_iops_mean[f'Time ({time_unit})'], df_iops_mean['Mean IOPS (BW)'], 'o', markersize=2, color=colors['green'], label='Mean IOPS (ss_bw)', alpha=0.6)
if 'Slope IOPS (BW)' in df_iops_slope:
    ax1.plot(df_iops_slope[f'Time ({time_unit})'], df_iops_slope['Slope IOPS (BW)'], 'o', markersize=1, color=colors['yellow'], label='Slope IOPS (ss_bw)', alpha=0.4)
ax1.set_xlabel(f'Time ({time_unit})', color='white')
ax1.set_ylabel('IOPS', color='white')
ax1.tick_params(axis='y', labelcolor='white')
ax1.tick_params(axis='x', labelcolor='white')
ax1.grid(True, color='gray')
ax1.set_ylim(bottom=0)  # Ensure the left y-axis starts from 0
if args.iops_max:
    ax1.set_ylim(top=args.iops_max)  # Set the maximum value for the left y-axis if provided

# parse shorthand bandwidth values
def parse_shorthand_bandwidth(value):
    units = {"B/s": 1, "KB/s": 1e3, "MB/s": 1e6, "GB/s": 1e9}
    match = re.match(r"([0-9.]+)([a-zA-Z/]+)", value)
    if match:
        num, unit = match.groups()
        return float(num) * units[unit]
    return float(value)  # Default to B/s if no unit is specified

# Instantiate a second y-axis to plot bandwidth
ax2 = ax1.twinx()
ax2.set_facecolor('black')  # Set the secondary y-axis background color to black
if 'Mean Bandwidth (KB/s)' in df_bw_mean:
    ax2.plot(df_bw_mean[f'Time ({time_unit})'], df_bw_mean['Mean Bandwidth (KB/s)'], 'x', markersize=1, color='blue', label='Mean Bandwidth (KB/s) (ss_iops)', alpha=0.6)
if 'Slope Bandwidth (KB/s)' in df_bw_slope:
    ax2.plot(df_bw_slope[f'Time ({time_unit})'], df_bw_slope['Slope Bandwidth (KB/s)'], 'x', markersize=0.5, color=colors['cyan'], label='Slope Bandwidth (KB/s) (ss_iops)', alpha=0.4)
if 'Mean Bandwidth (KB/s) (BW)' in df_bw_mean:
    ax2.plot(df_bw_mean[f'Time ({time_unit})'], df_bw_mean['Mean Bandwidth (KB/s) (BW)'], 'x', markersize=1, color=colors['grey'], label='Mean Bandwidth (KB/s) (ss_bw)', alpha=0.6)
if 'Slope Bandwidth (KB/s) (BW)' in df_bw_slope:
    ax2.plot(df_bw_slope[f'Time ({time_unit})'], df_bw_slope['Slope Bandwidth (KB/s) (BW)'], 'x', markersize=0.5, color='white', label='Slope Bandwidth (KB/s) (ss_bw)', alpha=0.4)
ax2.set_ylabel('Bandwidth', color='white')
ax2.tick_params(axis='y', labelcolor='white')
ax2.yaxis.set_major_formatter(FuncFormatter(human_readable_bandwidth))
ax2.set_ylim(bottom=0)  # Ensure the right y-axis starts from 0
if args.bw_max:
    bw_max = parse_shorthand_bandwidth(args.bw_max)
    ax2.set_ylim(top=bw_max)  # Set the maximum value for the right y-axis if provided


# Add legends
fig.tight_layout(rect=[0, 0, 1, 1])  # Adjust the right margin to make more space for the legend
fig.legend(loc='upper right', bbox_to_anchor=(0.85, 0.9), facecolor='black', edgecolor='black')
legend = fig.legend(loc='upper right', bbox_to_anchor=(0.85, 0.9), facecolor='black', edgecolor='black', markerscale=8)

for text in legend.get_texts():
     text.set_color('white')
legend.get_frame().set_facecolor('black')
fig.tight_layout(pad=2.0)  # Add padding to ensure the title is not cut off

plt.title(f'{args.title_prefix} Steady-State IOPS and Bandwidth Over Time', color='white')
plt.savefig('steady_state_iops_bw.png', facecolor=fig.get_facecolor())
plt.show()
