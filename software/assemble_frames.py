"""
OBSOLETE: This script is no longer used in the project. 
It was used to merge frames based on a time difference of less than 10ms and split them into two categories based on the length field (byte[3]).

"""

import pandas as pd
import glob

def merge_frames_by_time(data):
    """
    Merges frames based on a time difference of less than 10ms, using the time of the previous byte for time difference calculation.
    Args:
        data (pd.DataFrame): DataFrame with 'Start Time (s)' and 'Data' columns.
    Returns:
        pd.DataFrame: DataFrame with merged frames.
    """
    # Sort data by Start Time for proper grouping
    data = data.sort_values(by="Start Time (s)").reset_index(drop=True)

    # Initialize variables
    merged_frames = []
    current_group = []
    current_start_time = data.loc[0, 'Start Time (s)']
    last_byte_time = current_start_time

    # Iterate through the sorted data to group frames
    for _, row in data.iterrows():
        if current_group and (row['Start Time (s)'] - last_byte_time) < 0.01:
            # Add the current row to the group
            current_group.append(row)
            last_byte_time = row['Start Time (s)']
        else:
            if current_group:
                # Finalize the current group
                merged_data = ''.join([item['Data'] for item in current_group])
                merged_frames.append({'Start Time (s)': current_start_time, 'Data': merged_data})
            # Reset the group
            current_group = [row]
            current_start_time = row['Start Time (s)']
            last_byte_time = row['Start Time (s)']

    # Add the last group
    if current_group:
        merged_data = ''.join([item['Data'] for item in current_group])
        merged_frames.append({'Start Time (s)': current_start_time, 'Data': merged_data})

    # Convert the merged frames into a DataFrame
    return pd.DataFrame(merged_frames)

# Example usage
# Process multiple input files
input_files = glob.glob('input_csv_files/*.csv')
all_frames_length_0x0B = []
all_frames_other = []

for file in input_files:
    print(f"Processing file: {file}")
    data = pd.read_csv(file, delimiter=';')
    data['Start Time (s)'] = data['Start Time (s)'].str.replace(',', '.').astype(float)

    # Call the function to merge frames
    merged_frames_df = merge_frames_by_time(data)

    # Split frames into two categories based on the length field (byte[3])
    frames_length_0x0B = []
    frames_other = []

    for _, row in merged_frames_df.iterrows():
        data_bytes = ' '.join([row['Data'][i:i+2] for i in range(0, len(row['Data']), 2)])
        if len(data_bytes.split()) > 4 and data_bytes.split()[3] == '0B':
            frames_length_0x0B.append({'Start Time (s)': row['Start Time (s)'], 'Data': data_bytes})
        else:
            frames_other.append({'Start Time (s)': row['Start Time (s)'], 'Data': data_bytes})

    # Append results to global lists
    all_frames_length_0x0B.extend(frames_length_0x0B)
    all_frames_other.extend(frames_other)

# Convert lists to DataFrames
frames_length_0x0B_df = pd.DataFrame(all_frames_length_0x0B)
frames_other_df = pd.DataFrame(all_frames_other)

# Save the results to separate files
frames_length_0x0B_df.to_csv('frames_length_0x0B.csv', index=False)
frames_other_df.to_csv('frames_other.csv', index=False)

print("Frames with length 0x0B saved to frames_length_0x0B.csv")
print("Other frames saved to frames_other.csv")
