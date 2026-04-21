# LIN Payload & Timing Analyzer (Custom Extension)

This extension is a **High-Level Analyzer (HLA)** for Saleae Logic 2, specifically optimized to measure the **Net Data Payload Duration** on a LIN Bus. It is designed to automate the timing analysis that usually requires manual cursor measurements.

## Core Features & Improvements

* **Precise Data Timing:** Measures the duration from the **start of Data Byte 1 (D1)** to the **end of the last Data Byte (D7/D8)**.
* **Gap Extraction:** Automatically excludes Header (Break, Sync, PID) and Checksum times to focus on the raw data transfer.
* **Dynamic Type Tagging:** Instead of a generic label, it categorizes rows by byte count (e.g., `DATA_LEN_8B`, `DATA_LEN_7B`) in the Type column.
* **Excel Optimized:** The numeric duration value (e.g., `4.756`) is injected into the **Data** column for direct mathematical analysis after CSV export.
* **Zero-Overlap Engine:** Built with a "single-frame-per-segment" logic to prevent Saleae Logic 2 from hanging at 1% during processing.

## How to Understand the Results

### 1. The Measurement Logic
The analyzer tracks the LIN frame state and calculates time as follows:
* **p_start:** Triggered at the falling edge of the Start Bit of the first data byte.
* **p_end:** Updated at the end of every data byte.
* **Result:** Calculated as `(p_end - p_start)` upon reaching the Checksum.

### 2. Column Mapping for Data Table & Excel

| Table Column | Value Generated | Purpose |
| :--- | :--- | :--- |
| **Type** | `DATA_LEN_8B`, `h_break`, `d_byte` | Use this to filter specific message lengths in Excel. |
| **Data** | `4.756` (Example) | Raw numeric duration in milliseconds. Use this for formulas. |
| **Label (lbl)** | `0x71 (8B, DataDur:4.756ms)` | Human-readable summary on the waveform. |
| **ms** | `0.130 ms` | Duration of IBS (Inter-Byte) or IFS (Inter-Frame) gaps. |

## Quick Start Guide

1.  **Installation:** Build this extension and load it into Saleae Logic 2.
2.  **Setup:** Add a standard **LIN Analyzer** first. Then, add this **LIN Payload & Timing Analyzer** and select the standard LIN analyzer as its input.
3.  **Export:** * Open the **Data Table** in Logic 2.
    * Click the three dots (...) and select **Export Table (CSV)**.
4.  **Analyze:** In Excel, filter the **Type** column for `DATA_LEN_8B` to see all 8-byte payload timings instantly.

## Developer Notes
This extension replaces the generic `lin_data` labels with specific protocol stages (`h_break`, `h_sync`, `h_pid`, `d_byte`) to make the data table much easier to read and debug.