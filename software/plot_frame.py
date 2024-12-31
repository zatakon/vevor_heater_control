#!/usr/bin/env python3

import csv
import math
import matplotlib.pyplot as plt
from statistics import mean, stdev
from dataclasses import dataclass
from typing import List

################################################################################
# Data Structures
################################################################################

@dataclass
class Frame:
    payload: bytes

@dataclass
class Stats:
    count: int
    min: int
    max: int
    mean: float
    stdev: float

################################################################################
# Utility Functions
################################################################################

def hexstr_to_bytes(hexstr_with_spaces: str) -> bytes:
    """
    Convert a hex string with spaces into raw bytes.
    Example:
        "AA 77 02 33 01 01 0A 00 03 FB 00 9E ..."
        becomes
        b'\xAA\x77\x02\x33\x01\x01\x0A\x00\x03\xFB\x00\x9E...'
    """
    parts = hexstr_with_spaces.strip().split()
    return bytes.fromhex("".join(parts))

def big_endian_16(high: int, low: int) -> int:
    """
    Combine two bytes (high, low) into a 16-bit integer.
    """
    return (high << 8) | low

def compute_stats(values: List[int]) -> Stats:
    """
    Compute statistics for a list of numeric values.
    """
    if not values:
        return Stats(0, 0, 0, 0.0, 0.0)
    mn = min(values)
    mx = max(values)
    avg = mean(values)
    sd = stdev(values) if len(values) > 1 else 0.0
    return Stats(count=len(values), min=mn, max=mx, mean=avg, stdev=sd)

################################################################################
# Main Script
################################################################################

def main():
    # Change this to your CSV name or path
    csv_filename = "frames_other.csv"

    # List to store all frames in order
    frames: List[Frame] = []

    ########################################################################
    # 1) Load CSV, filter frames
    ########################################################################
    with open(csv_filename, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            hex_data = row[1].strip()
            if not hex_data:
                continue

            try:
                frame = hexstr_to_bytes(hex_data)
            except ValueError:
                # Skip lines with invalid hex data
                continue

            # Must start with AA 77 => heater->controller
            if len(frame) >= 8 and frame[0] == 0xAA and frame[1] == 0x77:
                # Extract the "payload" after the first 8 bytes
                # If you want the full frame as payload, uncomment the next line
                # payload = frame
                # Otherwise, extract payload after first 8 bytes
                payload = frame
                frames.append(Frame(payload=payload))

    if not frames:
        print("No AA 77 frames found! Check your CSV or filters.")
        return

    # Filter out frames where payload is all zeros
    original_length = len(frames)
    frames = [frame for frame in frames if any(byte != 0 for byte in frame.payload)]
    filtered_length = len(frames)
    print(f"Filtered out {original_length - filtered_length} frames with all-zero payloads.")

    if not frames:
        print("No non-zero payload frames found after filtering!")
        return

    ########################################################################
    # 2) Basic stats for single bytes and 16-bit pairs
    ########################################################################
    # Determine the maximum payload length
    max_len = max(len(frame.payload) for frame in frames)

    # Initialize lists for single bytes and 16-bit pairs
    single_bytes: List[List[int]] = [[] for _ in range(max_len)]
    pairs_16: List[List[int]] = [[] for _ in range(max_len - 1)]

    # Populate the lists
    for frame in frames:
        plen = len(frame.payload)
        for i in range(plen):
            single_bytes[i].append(frame.payload[i])
        for i in range(plen - 1):
            val16 = big_endian_16(frame.payload[i], frame.payload[i+1])
            pairs_16[i].append(val16)

    # Compute statistics
    single_bytes_stats: List[Stats] = [compute_stats(sb) for sb in single_bytes]
    pairs_16_stats: List[Stats] = [compute_stats(p) for p in pairs_16]

    # Print out some stats
    print("\n======== Single-Byte Offsets Stats ========")
    for i, st in enumerate(single_bytes_stats):
        if st.count > 0:
            print(f"Offset {i}: count={st.count}, "
                  f"range=({st.min},{st.max}), "
                  f"mean={st.mean:.1f}, stdev={st.stdev:.1f}")

    print("\n======== 16-bit (Big-Endian) Offsets Stats ========")
    for i, st in enumerate(pairs_16_stats):
        if st.count > 0:
            print(f"Offset {i}-{i+1}: count={st.count}, "
                  f"range=({st.min},{st.max}), "
                  f"mean={st.mean:.1f}, stdev={st.stdev:.1f}")

    ########################################################################
    # 3) Best-Guess for Key Fields
    ########################################################################
    print("\n======== Heuristic Guess for Known Fields ========")
    # Guess offset0-1 is Voltage if range is ~900..1600 (9..16 V * 100)
    if max_len >= 2:
        stv = single_bytes_stats[0]  # Using single-byte stats as an example
        if stv.min > 500 and stv.max < 3000:
            print(f"Likely Voltage at byte 0, range {stv.min}..{stv.max} => {stv.min/100.0:.2f}..{stv.max/100.0:.2f} V")

    # Guess offset2-3 is Temperature if range is ~0..1000 (0..100 C * 10)
    if max_len >= 4:
        stt = pairs_16_stats[1]  # Pair [2-3]
        if stt.count > 0 and stt.min >= 0 and stt.max < 1000:
            print(f"Likely Temperature at pair [2-3], range {stt.min}..{stt.max} => {stv.min/10.0:.1f}..{stv.max/10.0:.1f} °C")

    ########################################################################
    # 4) Plotting Statistics and Data
    ########################################################################
    print("\nPlotting data and statistics... Close plots to end.\n")

    frame_ids = list(range(len(frames)))

    # Define the offsets to exclude from plotting
    # 0:  identifier 0xAA
    # 1:  device ID (controller 0x66, heater 0x77)
    # 2:  command? every time 0x02
    # 3:  length field (0x0B for controller->heater, 0x33 for heater->controller)
    # 4:  heater enable?
    # 5:  state (0x00: off, 0x01: glowing, 0x02: heating, 0x03: stable combustion, 0x04: cooling)
    # 6:  power level (0x00..0x0A)
    # 7:  0x00
    # 8:  0x03 if running, 0x00 if stopped
    # 9:  0xFB if running, 0x00 if stopped
    # 10: 0x00
    # 11: 153-158 (input voltage*10)
    # 12: 0x00
    # 13: 0-12 (glow plug? Input current?)
    # 14: 0-1
    # 15: 0-21: some temperature?
    # 16-17: 480,1630 (chamber temperature * 100)
    # 18: 0x00
    # 19: 0x00
    # 20: 0-1
    # 21: 0-255
    # 22: 0x00
    # 23: 0-51
    # 24: 0-66
    # 25: 0-86
    # 26: 0-56
    # 27: 0-12
    # 28: 0-17
    # 29: 0-255
    # 30-45: 0x00
    # 46: 35
    # 47: 4
    # 48: 17
    # 49: 35
    # 50: 0x00
    # 51: 20
    # 52: 0-1
    # 53: 0-250
    # 54: 0x00
    # 55: 3-250

    offsets_to_skip = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,18,19,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]

    # Define the 16-bit pairs to plot
    # For example, to plot only pair starting at offset 15 (i.e., pair 15-16)
    pairs_to_plot = [16]

    # ===========================
    # Plot Single-Byte Payloads
    # ===========================

    # Determine the offsets to include
    included_offsets = [i for i in range(max_len) if i not in offsets_to_skip]

    if not included_offsets:
        print("No byte offsets left to plot after applying exclusions.")
    else:
        # Calculate the number of subplots needed
        subplot_num = len(included_offsets)

        # Create subplots
        fig_sb, axes_sb = plt.subplots(nrows=subplot_num, ncols=1, figsize=(15, 3 * subplot_num), sharex=True)

        # If there's only one subplot, axes_sb is not a list, so make it a list for consistency
        if subplot_num == 1:
            axes_sb = [axes_sb]

        fig_sb.suptitle("Single-Byte Payload Offsets vs. Frame ID", fontsize=16)

        # Iterate over included offsets and their corresponding axes
        for ax, offset in zip(axes_sb, included_offsets):
            byte_values = single_bytes[offset]
            ax.plot(frame_ids, byte_values, ".-", label=f"Byte {offset}")
            ax.set_ylabel(f"Byte {offset}\nRange: {min(byte_values)}-{max(byte_values)}")
            ax.grid(True)
            ax.legend(loc='upper right')

        axes_sb[-1].set_xlabel("Frame ID")
        fig_sb.tight_layout(rect=[0, 0.03, 1, 0.95])

    # ===========================
    # Plot 16-bit Pair Payloads
    # ===========================

    if not pairs_to_plot:
        print("No 16-bit pairs specified to plot.")
    else:
        # Validate pairs_to_plot
        valid_pairs_to_plot = [pair for pair in pairs_to_plot if 0 <= pair < (max_len -1)]
        invalid_pairs = set(pairs_to_plot) - set(valid_pairs_to_plot)
        if invalid_pairs:
            print(f"Warning: The following pairs are out of range and will be skipped: {sorted(invalid_pairs)}")

        if not valid_pairs_to_plot:
            print("No valid 16-bit pairs to plot.")
        else:
            # Calculate the number of valid pairs to plot
            num_pairs = len(valid_pairs_to_plot)

            # Create subplots
            fig_p16, axes_p16 = plt.subplots(nrows=num_pairs, ncols=1, figsize=(15, 3 * num_pairs), sharex=True)

            # If there's only one subplot, axes_p16 is not a list, so make it a list for consistency
            if num_pairs == 1:
                axes_p16 = [axes_p16]

            fig_p16.suptitle("16-bit Big-Endian Payload Pairs vs. Frame ID", fontsize=16)

            # Iterate over valid pairs and their corresponding axes
            for ax, pair_start in zip(axes_p16, valid_pairs_to_plot):
                pair_values = pairs_16[pair_start]
                ax.plot(frame_ids, pair_values, ".-", label=f"Pair {pair_start}-{pair_start +1}")
                ax.set_ylabel(f"Pair {pair_start}-{pair_start +1}\nRange: {min(pair_values)}-{max(pair_values)}")
                ax.grid(True)
                ax.legend(loc='upper right')

            axes_p16[-1].set_xlabel("Frame ID")
            fig_p16.tight_layout(rect=[0, 0.03, 1, 0.95])

    # ===========================
    # Show all plots
    # ===========================
    plt.show()

if __name__ == "__main__":
    main()
