#!/usr/bin/env python3

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
class Cycle:
    request: Frame
    response: Frame

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
    # Change this to your TXT name or path
    txt_filename = "docs/communication/log_start_running_stop.txt"

    # List to store all cycles in order
    cycles: List[Cycle] = []

    ########################################################################
    # 1) Load TXT, filter and associate frames
    ########################################################################
    try:
        with open(txt_filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File {txt_filename} not found!")
        return

    # Ensure that the number of lines is even (pairs of request and response)
    if len(lines) % 2 != 0:
        print("Warning: The number of lines in the TXT file is not even. "
              "The last line will be ignored.")

    # Process lines in pairs
    for i in range(0, len(lines) - 1, 2):
        request_line = lines[i].strip()
        response_line = lines[i + 1].strip()

        try:
            request_bytes = hexstr_to_bytes(request_line)
            response_bytes = hexstr_to_bytes(response_line)
        except ValueError:
            # Skip pairs with invalid hex data
            print(f"Skipping invalid pair at lines {i+1} and {i+2}.")
            continue

        # Create Frame objects for request and response
        request_frame = Frame(payload=request_bytes)
        response_frame = Frame(payload=response_bytes)

        # Append as a Cycle
        cycles.append(Cycle(request=request_frame, response=response_frame))

    if not cycles:
        print("No valid frame pairs found! Check your TXT file.")
        return

    # Filter out cycles where response payload is all zeros
    original_length = len(cycles)
    cycles = [cycle for cycle in cycles if any(byte != 0 for byte in cycle.response.payload)]
    filtered_length = len(cycles)
    print(f"Filtered out {original_length - filtered_length} frame pairs with all-zero response payloads.")

    if not cycles:
        print("No non-zero response payload frame pairs found after filtering!")
        return

    ########################################################################
    # 2) Basic stats for single bytes and 16-bit pairs
    ########################################################################
    # Determine the maximum payload length
    max_len = max(len(cycle.response.payload) for cycle in cycles)

    # Initialize lists for single bytes and 16-bit pairs
    single_bytes: List[List[int]] = [[] for _ in range(max_len)]
    pairs_16: List[List[int]] = [[] for _ in range(max_len - 1)]

    # Populate the lists with response payloads
    for cycle in cycles:
        frame = cycle.response
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
            print(f"Likely Temperature at pair [2-3], range {stt.min}..{stt.max} => {stt.min/10.0:.1f}..{stt.max/10.0:.1f} °C")

    ########################################################################
    # 4) Plotting Statistics and Data
    ########################################################################
    print("\nPlotting data and statistics... Close plots to end.\n")

    frame_ids = list(range(len(cycles)))

    # Define the offsets to exclude from plotting
    # 0:     100%  0xAA        identifier 0xAA
    # 1:     100%  0x66, 0x77  device ID (controller 0x66, heater 0x77)
    # 2:     50%   0x02        command?
    # 3:     100%  0x0B, 0x33  length field (0x0B for controller->heater, 0x33 for heater->controller)
    # 4:     80%   0-1         all 1, last one 0 | heater enabled?
    # 5:     99%   0x00-0x04   state (0x00: off, 0x01: glow plug pre heat, 0x02: ignited, 0x03: stable combustion, 0x04: stoping, cooling) [state]
    # 6:     100%  0x01-0x0A   power level [level]
    # 7:     0%    0x00        unknown
    # 8:     0%    0x00, 0x03  0x03 if running, 0x00 if stopped (just last one is 0)
    # 9:     0%    0x00, 0xFB  0xFB if running, 0x00 if stopped (just last one is 0)
    # 10:    0%    0x00        unknown
    # 11:    99%   153-158     input voltage [V * 10]
    # 12:    0%    0x00        unknown
    # 13:    40%   0-12        glow plug current [A]
    # 14:    50%   0-1         cooling down [0/1]
    # 15:    30%   0-16        Fan voltage? Some temperature? [V]
    # 16-17: 99%   480,1630    heat exchanger temperature [°C * 100]
    # 18:    0%    0x00        unknown
    # 19:    0%    0x00        unknown
    # 20-21: 90%   0-325       state duration [s]
    # 22:    0%    0x00        unknown
    # 23:    90%   0-51        pump frequency [Hz*10]
    # 24:    25%   0-66        glow plug voltage/current/temperature
    # 25:    25%   0-86        glow plug voltage/current/temperature
    # 26:    25%   0-56        glow plug voltage/current/temperature
    # 27:    25%   0-12        glow plug voltage/current/temperature
    # 28-29  90%   0-3939      fan speed [rpm]
    # 30-45: 0%    0x00        unknown
    # 46:    0%    35          unknown constant
    # 47:    0%    4           unknown constant
    # 48:    0%    17          unknown constant
    # 49:    0%    35          unknown constant
    # 50:    0%    0x00        unknown
    # 51:    0%    30, 40      unknown
    # 52-53  10%   0-420       something glow plug related
    # 54:    0%    0x00        unknown
    # 55:    100%  1-254       checksum

    offsets_to_skip = [4, 7, 8,9,10, 12, 13, 22,30,51,54,55, 16,17,20,21,28,29,52,53,0,1,2,3,18,19,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]

    # Define the 16-bit pairs to plot
    # For example, to plot only pair starting at offset 15 (i.e., pair 15-16)
    pairs_to_plot = [16, 20, 28, 52]

    plots_into_one = [[13,24,25,26,27]]

    # ===========================
    # Plot Single-Byte Payloads, 16-bit Pairs, and Combined Groups into One Figure
    # ===========================

    # Determine the offsets to include for single-byte plots (excluding those in plots_into_one)
    included_offsets = [i for i in range(max_len) if i not in offsets_to_skip and not any(i in group for group in plots_into_one)]

    # Calculate the number of subplots:
    # - Single-byte plots
    # - plots_into_one groups
    # - 16-bit pair plots
    num_single_byte_plots = len(included_offsets)
    num_plots_into_one = len(plots_into_one)
    # Validate pairs_to_plot
    valid_pairs_to_plot = [pair for pair in pairs_to_plot if 0 <= pair < (max_len -1)]
    num_pairs_to_plot = len(valid_pairs_to_plot)
    total_subplots = num_single_byte_plots + num_plots_into_one + num_pairs_to_plot

    if total_subplots == 0:
        print("No data available to plot.")
        return

    # Create a single figure with all subplots
    fig, axes = plt.subplots(nrows=total_subplots, ncols=1, figsize=(15, 3 * total_subplots), sharex=True)
    
    # If there's only one subplot, axes is not a list, so make it a list for consistency
    if total_subplots == 1:
        axes = [axes]

    fig.suptitle("All Payload Offsets and 16-bit Pairs vs. Frame ID", fontsize=16)

    current_subplot = 0  # To keep track of the current subplot index

    # ===========================
    # Plot Single-Byte Payloads
    # ===========================
    if included_offsets:
        for offset in included_offsets:
            ax = axes[current_subplot]
            byte_values = single_bytes[offset]
            ax.plot(frame_ids, byte_values, ".-", label=f"Byte {offset}")
            ax.set_ylabel(f"Byte {offset}\nRange: {min(byte_values)}-{max(byte_values)}")
            ax.grid(True)
            ax.legend(loc='upper right')
            current_subplot += 1

    # ===========================
    # Plot Combined Groups from plots_into_one
    # ===========================
    if plots_into_one:
        for group in plots_into_one:
            ax = axes[current_subplot]
            for offset in group:
                byte_values = single_bytes[offset]
                ax.plot(frame_ids, byte_values, ".-", label=f"Byte {offset}")
            group_label = "-".join(map(str, group))
            ax.set_ylabel(f"Bytes {group_label}\nRange: {min(min(single_bytes[offset] for offset in group))}-{max(max(single_bytes[offset] for offset in group))}")
            ax.set_title(f"Combined Bytes {group_label}")
            ax.grid(True)
            ax.legend(loc='upper right')
            current_subplot += 1

    # ===========================
    # Plot 16-bit Pair Payloads
    # ===========================
    if valid_pairs_to_plot:
        for pair_start in valid_pairs_to_plot:
            ax = axes[current_subplot]
            pair_values = pairs_16[pair_start]
            ax.plot(frame_ids, pair_values, ".-", label=f"Pair {pair_start}-{pair_start +1}")
            ax.set_ylabel(f"Pair {pair_start}-{pair_start +1}\nRange: {min(pair_values)}-{max(pair_values)}")
            ax.grid(True)
            ax.legend(loc='upper right')
            current_subplot += 1

    # Set the xlabel for the last subplot
    axes[-1].set_xlabel("Frame ID")

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    # ===========================
    # Show all plots
    # ===========================
    plt.show()

if __name__ == "__main__":
    main()
