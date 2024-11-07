import os
import csv
import psutil
import tkinter as tk
from datetime import datetime
from pathlib import Path

# Define the file path
log_folder = Path("c:/data_network")
log_folder.mkdir(parents=True, exist_ok=True)  # Create folder if it doesn't exist
log_file = log_folder / "network_usage_log.csv"

# Initialize CSV file with headers if it doesn't exist
if not log_file.exists():
    with open(log_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Data Rate (Mbps)", "Total MB Consumed", 
                         "Average Usage (Mbps)", "Peak Usage (Mbps)", "Time of Day", 
                         "Day of Week", "Anomaly Label"])

# Variables to track usage data
previous_bytes_sent = psutil.net_io_counters().bytes_sent
previous_bytes_recv = psutil.net_io_counters().bytes_recv
total_bytes_consumed = 0  # in bytes
peak_usage_mbps = 0
average_usage_mbps = 0
data_points = []

# Function to log network usage to CSV
def log_network_usage():
    global previous_bytes_sent, previous_bytes_recv, total_bytes_consumed, peak_usage_mbps, average_usage_mbps, data_points

    # Get current network stats
    current_stats = psutil.net_io_counters()
    current_bytes_sent = current_stats.bytes_sent
    current_bytes_recv = current_stats.bytes_recv
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate bytes consumed since last check
    bytes_sent_diff = current_bytes_sent - previous_bytes_sent
    bytes_recv_diff = current_bytes_recv - previous_bytes_recv
    total_bytes_diff = bytes_sent_diff + bytes_recv_diff
    
    # Update cumulative usage in MB
    total_bytes_consumed += total_bytes_diff
    total_mb_consumed = total_bytes_consumed / (1024 ** 2)  # Convert to MB

    # Calculate data rate in Mbps (bits per second, scaled to Mbps)
    data_rate_mbps = (total_bytes_diff * 8) / (5 * 1024 ** 2)  # over a 5-second interval

    # Update peak and average usage
    data_points.append(data_rate_mbps)
    if data_rate_mbps > peak_usage_mbps:
        peak_usage_mbps = data_rate_mbps
    average_usage_mbps = sum(data_points) / len(data_points) if data_points else 0

    # Determine time of day and day of week for logging
    time_of_day = datetime.now().strftime("%H:%M")
    day_of_week = datetime.now().strftime("%A")

    # Determine anomaly based on a threshold (e.g., over 10 Mbps for this example)
    anomaly_label = "Yes" if data_rate_mbps > 10 else "No"

    # Append data to CSV with all required columns
    with open(log_file, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, f"{data_rate_mbps:.2f}", f"{total_mb_consumed:.2f}", 
                         f"{average_usage_mbps:.2f}", f"{peak_usage_mbps:.2f}", 
                         time_of_day, day_of_week, anomaly_label])
    
    # Update previous stats
    previous_bytes_sent = current_bytes_sent
    previous_bytes_recv = current_bytes_recv
    
    # Schedule next log
    root.after(5000, log_network_usage)  # Update every 5 seconds

# Tkinter GUI setup
root = tk.Tk()
root.title("Network Usage Monitor")

# Hide the Tkinter window
root.withdraw()  # Use withdraw() to hide the window entirely

# Start logging
log_network_usage()

# Keep the Tkinter loop running in the background
root.mainloop()
