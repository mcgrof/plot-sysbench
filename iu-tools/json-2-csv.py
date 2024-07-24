#!/usr/bin/python3
import json
import csv
import sys
import os

def load_json_data(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def format_size(size):
    size = int(size)
    return 1 << size

def json_to_csv(data1, data2, input_file1, input_file2, output_file_prefix):
    source1 = os.path.splitext(os.path.basename(input_file1))[0]
    source2 = os.path.splitext(os.path.basename(input_file2))[0]

    process_data("Block size", "IO Block Size", data1, data2, source1, source2, f"{output_file_prefix}_io_block_size.csv")
    process_data("Algn size", "Alignment", data1, data2, source1, source2, f"{output_file_prefix}_alignment.csv")

def process_data(key_type, data_type, data1, data2, source1, source2, output_file):
    # Generate all keys from 9 (512 bytes) to 30 (1GB)
    all_keys = range(9, 31)

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow(['Size (bytes)', f'{data_type} Count - {source1}', f'{data_type} Count - {source2}'])

        # Write data rows
        for key in all_keys:
            size = format_size(key)
            value1 = data1.get(key_type, {}).get(str(key), 0)
            value2 = data2.get(key_type, {}).get(str(key), 0)
            writer.writerow([size, value1, value2])

    print(f"CSV file '{output_file}' has been created.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_json_file1> <input_json_file2> <output_csv_prefix>")
        sys.exit(1)

    input_file1 = sys.argv[1]
    input_file2 = sys.argv[2]
    output_prefix = sys.argv[3]

    data1 = load_json_data(input_file1)
    data2 = load_json_data(input_file2)
    json_to_csv(data1, data2, input_file1, input_file2, output_prefix)
