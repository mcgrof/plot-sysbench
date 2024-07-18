#!/usr/bin/python3
import argparse
import re
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.animation import FuncAnimation

# Parse command line arguments
parser = argparse.ArgumentParser(description='Compare FIO Steady-State Data between two directories')
parser.add_argument('--dir1', type=str, required=True, help='Path to the first directory containing FIO JSON files')
parser.add_argument('--dir2', type=str, required=True, help='Path to the second directory containing FIO JSON files')
parser.add_argument('--title-prefix', type=str, default='', help='Prefix for the title of the graph')
parser.add_argument('--iops-max', type=float, default=None, help='Maximum value for IOPS y-axis')
parser.add_argument('--bw-max', type=str, default=None, help='Maximum value for Bandwidth y-axis (e.g., 1.8GB/s)')
parser.add_argument('--red-drift', type=int, default=-100, help='RGB red color drift for the second directory')
parser.add_argument('--green-drift', type=int, default=80, help='RGB green color drift for the second directory')
parser.add_argument('--blue-drift', type=int, default=-50, help='RGB blue color drift for the second directory')
parser.add_argument('--dir1-marker-size', type=float, default=1, help='Base marker size for directory 1')
parser.add_argument('--dir2-marker-size', type=float, default=1, help='Base marker size for directory 2')
parser.add_argument('--dir1-alpha', type=float, default=1, help='Alpha value for directory 1 markers')
parser.add_argument('--dir2-alpha', type=float, default=0.4, help='Alpha value for directory 2 markers')

args = parser.parse_args()

global initial_legend

# Function to load data from a directory
def load_data(directory):
    data = {}
    files = ['ss_iops.json', 'ss_bw.json']
    for file in files:
        file_path = os.path.join(directory, file)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data[file] = json.load(f)
    return data

# Load data from both directories
data_dir1 = load_data(args.dir1)
data_dir2 = load_data(args.dir2)

if not data_dir1 and not data_dir2:
    raise FileNotFoundError("No valid JSON files found in both directories. Please provide at least one valid file in each directory.")

# Function to adjust the length of lists
def adjust_length(data_list, target_length):
    current_length = len(data_list)
    if current_length < target_length:
        data_list.extend([None] * (target_length - current_length))
    else:
        data_list = data_list[:target_length]
    return data_list

# Extract the number of entries dynamically for each job in both directories
def get_num_entries(data):
    return max(len(data[file]['jobs'][0]['steadystate']['data']['iops']) for file in data)

num_entries_job0_dir1 = get_num_entries(data_dir1) if data_dir1 else 0
num_entries_job1_dir1 = get_num_entries(data_dir1) if data_dir1 else 0
num_entries_job0_dir2 = get_num_entries(data_dir2) if data_dir2 else 0
num_entries_job1_dir2 = get_num_entries(data_dir2) if data_dir2 else 0

# Initialize lists to store the data
time_data_job0_dir1 = list(range(1, num_entries_job0_dir1 + 1))
time_data_job1_dir1 = list(range(1, num_entries_job1_dir1 + 1))
time_data_job0_dir2 = list(range(1, num_entries_job0_dir2 + 1))
time_data_job1_dir2 = list(range(1, num_entries_job1_dir2 + 1))

legend_created = False  # Flag to check if legend is already created
legend_handles = []  # Store handles for the legend
legend_labels = []  # Store labels for the legend

# Determine the appropriate time unit
max_time = max(time_data_job0_dir1 + time_data_job1_dir1 + time_data_job0_dir2 + time_data_job1_dir2)
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
time_data_job0_dir1 = [t / time_factor for t in time_data_job0_dir1]
time_data_job1_dir1 = [t / time_factor for t in time_data_job1_dir1]
time_data_job0_dir2= [t / time_factor for t in time_data_job0_dir2]
time_data_job1_dir2 = [t / time_factor for t in time_data_job1_dir2]

# Initialize DataFrames
df_iops_mean_dir1 = pd.DataFrame({f'Time ({time_unit})': time_data_job0_dir1})
df_bw_mean_dir1 = pd.DataFrame({f'Time ({time_unit})': time_data_job0_dir1})
df_iops_slope_dir1 = pd.DataFrame({f'Time ({time_unit})': time_data_job1_dir1})
df_bw_slope_dir1 = pd.DataFrame({f'Time ({time_unit})': time_data_job1_dir1})

df_iops_mean_dir2 = pd.DataFrame({f'Time ({time_unit})': time_data_job0_dir2})
df_bw_mean_dir2 = pd.DataFrame({f'Time ({time_unit})': time_data_job0_dir2})
df_iops_slope_dir2 = pd.DataFrame({f'Time ({time_unit})': time_data_job1_dir2})
df_bw_slope_dir2 = pd.DataFrame({f'Time ({time_unit})': time_data_job1_dir2})

# Populate DataFrames if corresponding files are found in each directory
def populate_dataframes(data, df_iops_mean, df_bw_mean, df_iops_slope, df_bw_slope, num_entries_job0, num_entries_job1):
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

populate_dataframes(data_dir1, df_iops_mean_dir1, df_bw_mean_dir1, df_iops_slope_dir1, df_bw_slope_dir1, num_entries_job0_dir1, num_entries_job1_dir1)
populate_dataframes(data_dir2, df_iops_mean_dir2, df_bw_mean_dir2, df_iops_slope_dir2, df_bw_slope_dir2, num_entries_job0_dir2, num_entries_job1_dir2)

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

# Function to drift colors
def drift_color(color, red_drift, green_drift, blue_drift):
    r = min(max(int(color[1:3], 16) + red_drift, 0), 255)
    g = min(max(int(color[3:5], 16) + green_drift, 0), 255)
    b = min(max(int(color[5:7], 16) + blue_drift, 0), 255)
    return f'#{r:02X}{g:02X}{b:02X}'

# Our color palette
base_colors = {
    'red': '#FF0000',  # Red
    'green': '#00FF00',  # Green
    'blue': '#0000FF',  # Blue
    'yellow': '#FFFF00',  # Yellow
    'grey': '#808080',  # Grey
    'contrast_red': '#E4002B',  # Contrasting Red
    'contrast_yellow': '#FFC72C',  # Contrasting Yellow
    'contrast_blue': '#0057B8',  # Contrasting Blue
}

drifted_colors = {name: drift_color(color, args.red_drift, args.green_drift, args.blue_drift) for name, color in base_colors.items()}

# Plot the data
fig, ax1 = plt.subplots(figsize=(24, 16))  # Increased the figure size
fig.patch.set_facecolor('black')  # Set the background color to black
ax1.set_facecolor('black')  # Set the plot background color to black
global ax2
ax2 = ax1.twinx()  # Instantiate a second y-axis to plot bandwidth

# Get the basenames of the directories for legend
dir1_name = os.path.basename(os.path.normpath(args.dir1))
dir2_name = os.path.basename(os.path.normpath(args.dir2))

# parse shorthand bandwidth values
def parse_shorthand_bandwidth(value):
    units = {"B/s": 1, "KB/s": 1e3, "MB/s": 1e6, "GB/s": 1e9}
    match = re.match(r"([0-9.]+)([a-zA-Z/]+)", value)
    if match:
        num, unit = match.groups()
        return float(num) * units[unit]
    return float(value)  # Default to B/s if no unit is specified

# Function to create plots
def create_plot():
    global ax2
    global initial_legend;
    ax1.cla()
    ax2.cla()

    ax1.set_facecolor('black')
    ax2.set_facecolor('black')

    if 'Mean IOPS' in df_iops_mean_dir2:
        ax1.plot(df_iops_mean_dir2[f'Time ({time_unit})'], df_iops_mean_dir2['Mean IOPS'], 'o', markersize=args.dir2_marker_size, color=drifted_colors['red'], label=f'Mean IOPS ({dir2_name})', alpha=args.dir2_alpha)
    if 'Slope IOPS' in df_iops_slope_dir2:
        ax1.plot(df_iops_slope_dir2[f'Time ({time_unit})'], df_iops_slope_dir2['Slope IOPS'], 'o', markersize=args.dir2_marker_size * 0.5, color=drifted_colors['contrast_yellow'], label=f'Slope IOPS ({dir2_name})', alpha=args.dir2_alpha * 0.5)
    if 'Mean IOPS (BW)' in df_iops_mean_dir2:
        ax1.plot(df_iops_mean_dir2[f'Time ({time_unit})'], df_iops_mean_dir2['Mean IOPS (BW)'], 'o', markersize=args.dir2_marker_size, color=drifted_colors['green'], label=f'Mean IOPS (BW) ({dir2_name})', alpha=args.dir2_alpha)
    if 'Slope IOPS (BW)' in df_iops_slope_dir2:
        ax1.plot(df_iops_slope_dir2[f'Time ({time_unit})'], df_iops_slope_dir2['Slope IOPS (BW)'], 'o', markersize=args.dir2_marker_size * 0.5, color=drifted_colors['yellow'], label=f'Slope IOPS (BW) ({dir2_name})', alpha=args.dir2_alpha * 0.5)

    ax1.set_xlabel(f'Time ({time_unit})', color='white')
    ax1.set_ylabel('IOPS', color='white')
    ax1.tick_params(axis='y', labelcolor='white')
    ax1.tick_params(axis='x', labelcolor='white')
    ax1.grid(True, color='gray')
    ax1.set_ylim(bottom=0)  # Ensure the left y-axis starts from 0
    if args.iops_max:
        ax1.set_ylim(top=args.iops_max)  # Set the maximum value for the left y-axis if provided

    if 'Mean Bandwidth (KB/s)' in df_bw_mean_dir2:
        ax2.plot(df_bw_mean_dir2[f'Time ({time_unit})'], df_bw_mean_dir2['Mean Bandwidth (KB/s)'], 'x', markersize=args.dir2_marker_size * 0.5, color=drifted_colors['blue'], label=f'Mean Bandwidth (KB/s) ({dir2_name})', alpha=args.dir2_alpha)
    if 'Slope Bandwidth (KB/s)' in df_bw_slope_dir2:
        ax2.plot(df_bw_slope_dir2[f'Time ({time_unit})'], df_bw_slope_dir2['Slope Bandwidth (KB/s)'], 'x', markersize=args.dir2_marker_size * 0.25, color=drifted_colors['contrast_blue'], label=f'Slope Bandwidth (KB/s) ({dir2_name})', alpha=args.dir2_alpha * 0.5)
    if 'Mean Bandwidth (KB/s) (BW)' in df_bw_mean_dir2:
        ax2.plot(df_bw_mean_dir2[f'Time ({time_unit})'], df_bw_mean_dir2['Mean Bandwidth (KB/s) (BW)'], 'x', markersize=args.dir2_marker_size * 0.5, color=drifted_colors['grey'], label=f'Mean Bandwidth (KB/s) (BW) ({dir2_name})', alpha=args.dir2_alpha)
    if 'Slope Bandwidth (KB/s) (BW)' in df_bw_slope_dir2:
        ax2.plot(df_bw_slope_dir2[f'Time ({time_unit})'], df_bw_slope_dir2['Slope Bandwidth (KB/s) (BW)'], 'x', markersize=args.dir2_marker_size * 0.25, color=drifted_colors['grey'], label=f'Slope Bandwidth (KB/s) (BW) ({dir2_name})', alpha=args.dir2_alpha * 0.5)

    ax2.set_ylabel('Bandwidth', color='white')
    ax2.tick_params(axis='y', labelcolor='white')
    ax2.yaxis.set_major_formatter(FuncFormatter(human_readable_bandwidth))
    ax2.set_ylim(bottom=0)  # Ensure the right y-axis starts from 0
    if args.bw_max:
        bw_max = parse_shorthand_bandwidth(args.bw_max)
        ax2.set_ylim(top=bw_max)  # Set the maximum value for the right y-axis if provided

    # Add initial legend
    initial_legend = fig.legend(loc='upper right', bbox_to_anchor=(0.85, 0.90),
                                facecolor='black', edgecolor='black', markerscale=2)
    for text in initial_legend.get_texts():
        text.set_color('black')
    initial_legend.get_frame().set_facecolor('white')
    initial_legend.get_frame().set_edgecolor('white')
    fig.tight_layout(pad=2.0)  # Add padding to ensure the title is not cut off

    plt.title(f'{args.title_prefix} Steady-State IOPSand Bandwidth Over Time', color='white')

def update_plot(frame):
    global initial_legend
    if frame == 0:
        create_plot()  # Initial plot setup
    if frame == 25:
        fig.legends.clear()  # Remove the initial legend
    if frame > 25:
        if 'Mean IOPS' in df_iops_mean_dir1:
            ax1.plot(df_iops_mean_dir1[f'Time ({time_unit})'], df_iops_mean_dir1['Mean IOPS'], 'o', markersize=args.dir1_marker_size, color=base_colors['red'], label=f'Mean IOPS ({dir1_name})', alpha=args.dir1_alpha)
        if 'Slope IOPS' in df_iops_slope_dir1:
            ax1.plot(df_iops_slope_dir1[f'Time ({time_unit})'], df_iops_slope_dir1['Slope IOPS'], 'o', markersize=args.dir1_marker_size * 0.5, color=base_colors['contrast_yellow'], label=f'Slope IOPS ({dir1_name})', alpha=args.dir1_alpha * 0.5)
        if 'Mean IOPS (BW)' in df_iops_mean_dir1:
            ax1.plot(df_iops_mean_dir1[f'Time ({time_unit})'], df_iops_mean_dir1['Mean IOPS (BW)'], 'o', markersize=args.dir1_marker_size, color=base_colors['green'], label=f'Mean IOPS (BW) ({dir1_name})', alpha=0.6)
        if 'Slope IOPS (BW)' in df_iops_slope_dir1:
            ax1.plot(df_iops_slope_dir1[f'Time ({time_unit})'], df_iops_slope_dir1['Slope IOPS (BW)'], 'o', markersize=args.dir1_marker_size * 0.5, color=base_colors['yellow'], label=f'Slope IOPS (BW) ({dir1_name})', alpha=args.dir1_alpha * 0.5)

        if 'Mean Bandwidth (KB/s)' in df_bw_mean_dir1:
            ax2.plot(df_bw_mean_dir1[f'Time ({time_unit})'], df_bw_mean_dir1['Mean Bandwidth (KB/s)'], 'x', markersize=args.dir1_marker_size * 0.5, color=base_colors['blue'], label=f'Mean Bandwidth (KB/s) ({dir1_name})', alpha=args.dir1_alpha)
        if 'Slope Bandwidth (KB/s)' in df_bw_slope_dir1:
            ax2.plot(df_bw_slope_dir1[f'Time ({time_unit})'], df_bw_slope_dir1['Slope Bandwidth (KB/s)'], 'x', markersize=args.dir1_marker_size * 0.25, color=base_colors['contrast_blue'], label=f'Slope Bandwidth (KB/s) ({dir1_name})', alpha=args.dir1_alpha * 0.5)
        if 'Mean Bandwidth (KB/s) (BW)' in df_bw_mean_dir1:
            ax2.plot(df_bw_mean_dir1[f'Time ({time_unit})'], df_bw_mean_dir1['Mean Bandwidth (KB/s) (BW)'], 'x', markersize=args.dir1_marker_size * 0.5, color=base_colors['grey'], label=f'Mean Bandwidth (KB/s) (BW) ({dir1_name})', alpha=args.dir1_alpha)
        if 'Slope Bandwidth (KB/s) (BW)' in df_bw_slope_dir1:
            ax2.plot(df_bw_slope_dir1[f'Time ({time_unit})'], df_bw_slope_dir1['Slope Bandwidth (KB/s) (BW)'], 'x', markersize=args.dir1_marker_size * 0.25, color='white', label=f'Slope Bandwidth (KB/s) (BW) ({dir1_name})', alpha=args.dir1_alpha * 0.5)
        global legend_created, legend_handles, legend_labels
        if not legend_created:
            handles, labels = ax1.get_legend_handles_labels()
            handles2, labels2 = ax2.get_legend_handles_labels()
            legend_handles.extend(handles + handles2)
            legend_labels.extend(labels + labels2)
            legend = fig.legend(legend_handles, legend_labels, loc='upper right', bbox_to_anchor=(0.85, 0.90),
                                facecolor='black', edgecolor='black', markerscale=2)
            for text in legend.get_texts():
                text.set_color('black')
            legend.get_frame().set_facecolor('white')
            legend.get_frame().set_edgecolor('white')
            fig.tight_layout(pad=2.0)  # Add padding to ensure the title is not cut off
            legend_created = True  # Set the flag to avoid recreating the legend

# Create the initial plot
update_plot(0)

# Create the animation
anim = FuncAnimation(fig, update_plot, frames=range(50), interval=50, repeat=False)

# Save the animation as a gif
anim.save('steady_state_comparison.gif', writer='imagemagick')

plt.show()
