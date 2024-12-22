#!/usr/bin/env python
# coding: utf-8

# In[5]:


import tkinter as tk
from tkinter import scrolledtext, ttk
import serial
import serial.tools.list_ports
import threading
import time

# Function to scan available COM ports
def scan_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Function to refresh COM ports in dropdown
def refresh_ports():
    ports = scan_ports()
    port_combobox['values'] = ports
    if ports:
        port_combobox.set(ports[0])  # Set the first port as default

# Function to connect to the selected COM port
def connect_to_esp32():
    try:
        global ser
        selected_port = port_combobox.get()
        ser = serial.Serial(port=selected_port, baudrate=115200, timeout=1)
        log_message(f"Connected to ESP32 on {selected_port}")
        ser.write(b"PING\n")
        response = ser.readline().decode().strip()
        if response == "PONG":
            log_message("ESP32 is online!")
        # Start the serial reading thread
        threading.Thread(target=read_serial, daemon=True).start()
    except Exception as e:
        log_message(f"Error connecting to ESP32: {e}")


# Function to ping ESP32
def ping_esp32():
    try:
        ser.write(b"PING\n")
        response = ser.readline().decode().strip()
        if response == "PONG":
            log_message("ESP32 is online!")
        else:
            log_message("No response from ESP32.")
    except Exception as e:
        log_message(f"Error pinging ESP32: {e}")

# Function to read serial data
def read_serial():
    while True:
        try:
            if ser.in_waiting > 0:
                data = ser.readline().decode().strip()
                log_message(f"Received: {data}")
                # Process data for NFC
                if data.startswith("NFC:"):
                    global nfc_data
                    nfc_data = data.split("NFC:")[1]
                    log_message(f"NFC Data: {nfc_data}")
        except Exception as e:
            log_message(f"Error reading serial: {e}")
        time.sleep(0.1)

# Function to log messages in the GUI
def log_message(message):
    serial_monitor.configure(state="normal")
    serial_monitor.insert(tk.END, message + "\n")
    serial_monitor.configure(state="disabled")
    serial_monitor.see(tk.END)

# GUI Setup
root = tk.Tk()
root.title("ESP32 NFC Reader")

# Serial Port Configuration
port_label = tk.Label(root, text="Select Serial Port:")
port_label.pack(pady=5)

port_combobox = ttk.Combobox(root, state="readonly")
port_combobox.pack(pady=5)
refresh_ports()

refresh_button = tk.Button(root, text="Refresh Ports", command=refresh_ports)
refresh_button.pack(pady=5)

connect_button = tk.Button(root, text="Connect", command=connect_to_esp32)
connect_button.pack(pady=5)

# Ping ESP32 Button
ping_button = tk.Button(root, text="Ping ESP32", command=ping_esp32)
ping_button.pack(pady=5)

# Serial Monitor
serial_monitor_label = tk.Label(root, text="Serial Monitor:")
serial_monitor_label.pack(pady=5)
serial_monitor = scrolledtext.ScrolledText(root, width=50, height=20, state="disabled")
serial_monitor.pack(pady=5)

# Start the GUI event loop
root.mainloop()


# In[1]:


import tkinter as tk
from tkinter import scrolledtext, ttk
import serial
import serial.tools.list_ports
import threading
import time

# Flag for periodic ping thread
ping_active = False

# Function to scan available COM ports
def scan_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Function to refresh COM ports in dropdown
def refresh_ports():
    ports = scan_ports()
    port_combobox['values'] = ports
    if ports:
        port_combobox.set(ports[0])  # Set the first port as default

# Function to connect to the selected COM port
def connect_to_esp32():
    global ser, ping_active
    try:
        selected_port = port_combobox.get()
        ser = serial.Serial(port=selected_port, baudrate=115200, timeout=1)
        log_message(f"Connected to ESP32 on {selected_port}")
        ping_active = True
        # Start the serial reading thread
        threading.Thread(target=read_serial, daemon=True).start()
        # Start the periodic ping thread
        threading.Thread(target=periodic_ping, daemon=True).start()
    except Exception as e:
        log_message(f"Error connecting to ESP32: {e}")

# Function to disconnect from the ESP32
def disconnect_from_esp32():
    global ser, ping_active
    try:
        ping_active = False
        if ser and ser.is_open:
            ser.close()
        log_message("Disconnected from ESP32.")
    except Exception as e:
        log_message(f"Error disconnecting from ESP32: {e}")

# Function to ping ESP32
def ping_esp32():
    try:
        if ser and ser.is_open:
            ser.write(b"PING\n")
            response = ser.readline().decode().strip()
            if response == "PONG":
                log_message("ESP32 is online!")
            else:
                log_message("No response from ESP32.")
    except Exception as e:
        log_message(f"Error pinging ESP32: {e}")

# Function to periodically ping ESP32
def periodic_ping():
    global ping_active
    while ping_active:
        ping_esp32()
        time.sleep(5)  # Adjust the interval as needed (e.g., 5 seconds)

# Function to read serial data
def read_serial():
    while True:
        try:
            if ser.in_waiting > 0:
                data = ser.readline().decode().strip()
                log_message(f"Received: {data}")
                # Process data for NFC
                if data.startswith("NFC:"):
                    global nfc_data
                    nfc_data = data.split("NFC:")[1]
                    log_message(f"NFC Data: {nfc_data}")
        except Exception as e:
            log_message(f"Error reading serial: {e}")
        time.sleep(0.1)

# Function to log messages in the GUI
def log_message(message):
    serial_monitor.configure(state="normal")
    serial_monitor.insert(tk.END, message + "\n")
    serial_monitor.configure(state="disabled")
    serial_monitor.see(tk.END)

# GUI Setup
root = tk.Tk()
root.title("ESP32 NFC Reader")

# Serial Port Configuration
port_label = tk.Label(root, text="Select Serial Port:")
port_label.pack(pady=5)

port_combobox = ttk.Combobox(root, state="readonly")
port_combobox.pack(pady=5)
refresh_ports()

refresh_button = tk.Button(root, text="Refresh Ports", command=refresh_ports)
refresh_button.pack(pady=5)

connect_button = tk.Button(root, text="Connect", command=connect_to_esp32)
connect_button.pack(pady=5)

disconnect_button = tk.Button(root, text="Disconnect", command=disconnect_from_esp32)
disconnect_button.pack(pady=5)

# Ping ESP32 Button
ping_button = tk.Button(root, text="Ping ESP32", command=ping_esp32)
ping_button.pack(pady=5)

# Serial Monitor
serial_monitor_label = tk.Label(root, text="Serial Monitor:")
serial_monitor_label.pack(pady=5)
serial_monitor = scrolledtext.ScrolledText(root, width=50, height=20, state="disabled")
serial_monitor.pack(pady=5)

# Start the GUI event loop
root.mainloop()


# In[ ]:


import tkinter as tk
from tkinter import scrolledtext, ttk
import serial
import serial.tools.list_ports
import threading
import time
import csv
import webbrowser
import os

# File path for the CSV
csv_filepath = r"C:\Users\gavin\Desktop\Hackthon\nfc_urls.csv"

def save_url_to_csv(url):
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
        # Append the URL to the CSV file
        with open(csv_filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([url])
        log_message(f"URL saved to {csv_filepath}: {url}")
    except Exception as e:
        log_message(f"Error saving URL to CSV: {e}")

# Global variables
ser = None
ping_active = False
csv_filename = "nfc_urls.csv"

# Function to scan available COM ports
def scan_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Function to refresh COM ports in dropdown
def refresh_ports():
    ports = scan_ports()
    port_combobox['values'] = ports
    if ports:
        port_combobox.set(ports[0])  # Set the first port as default

# Function to connect to the selected COM port
def connect_to_esp32():
    global ser, ping_active
    try:
        selected_port = port_combobox.get()
        ser = serial.Serial(port=selected_port, baudrate=115200, timeout=1)
        log_message(f"Connected to ESP32 on {selected_port}")
        ping_active = True
        # Start the serial reading thread
        threading.Thread(target=read_serial, daemon=True).start()
        # Start the periodic ping thread
        threading.Thread(target=periodic_ping, daemon=True).start()
    except Exception as e:
        log_message(f"Error connecting to ESP32: {e}")

# Function to disconnect from the ESP32
def disconnect_from_esp32():
    global ser, ping_active
    try:
        ping_active = False
        if ser and ser.is_open:
            ser.close()
        log_message("Disconnected from ESP32.")
    except Exception as e:
        log_message(f"Error disconnecting from ESP32: {e}")

# Function to ping ESP32
def ping_esp32():
    try:
        if ser and ser.is_open:
            ser.write(b"PING\n")
            response = ser.readline().decode().strip()
            if response == "PONG":
                log_message("ESP32 is online!")
            else:
                log_message("No response from ESP32.")
    except Exception as e:
        log_message(f"Error pinging ESP32: {e}")

# Function to periodically ping ESP32
def periodic_ping():
    global ping_active
    while ping_active:
        ping_esp32()
        time.sleep(5)  # Adjust the interval as needed (e.g., 5 seconds)

# Function to read serial data
def read_serial():
    while True:
        try:
            if ser.in_waiting > 0:
                data = ser.readline().decode().strip()
                log_message(f"Received: {data}")
                # Pass the data directly to handle_nfc_data
                handle_nfc_data(data)
        except Exception as e:
            log_message(f"Error reading serial: {e}")
        time.sleep(0.1)

# Function to handle NFC data
def handle_nfc_data(nfc_data):
    if nfc_data.startswith("http://") or nfc_data.startswith("https://"):  # Check if it's a valid URL
        try:
            # Save the URL to the CSV file
            save_url_to_csv(nfc_data)
            # Update the clickable label with the URL
            update_url_label(nfc_data)
            log_message(f"URL received and opened: {nfc_data}")
        except Exception as e:
            log_message(f"Error handling NFC data: {e}")
    else:
        log_message("NFC data is not a valid URL.")

# Function to update the label with a clickable URL
def update_url_label(url):
    url_label.config(text=url)  # Set the label text to the URL
    url_label.bind("<Button-1>", lambda event: open_url(url))  # Bind the click event to open the URL

# Function to open the URL when the label is clicked
def open_url(url):
    try:
        webbrowser.open(url)
    except Exception as e:
        log_message(f"Error opening URL: {e}")

# Function to log messages in the GUI
def log_message(message):
    serial_monitor.configure(state="normal")
    serial_monitor.insert(tk.END, message + "\n")
    serial_monitor.configure(state="disabled")
    serial_monitor.see(tk.END)

# GUI Setup
root = tk.Tk()
root.title("ESP32 NFC Reader")

# Serial Port Configuration
port_label = tk.Label(root, text="Select Serial Port:")
port_label.pack(pady=5)

port_combobox = ttk.Combobox(root, state="readonly")
port_combobox.pack(pady=5)
refresh_ports()

refresh_button = tk.Button(root, text="Refresh Ports", command=refresh_ports)
refresh_button.pack(pady=5)

connect_button = tk.Button(root, text="Connect", command=connect_to_esp32)
connect_button.pack(pady=5)

disconnect_button = tk.Button(root, text="Disconnect", command=disconnect_from_esp32)
disconnect_button.pack(pady=5)

# Ping ESP32 Button
ping_button = tk.Button(root, text="Ping ESP32", command=ping_esp32)
ping_button.pack(pady=5)

# Serial Monitor
serial_monitor_label = tk.Label(root, text="Serial Monitor:")
serial_monitor_label.pack(pady=5)
serial_monitor = scrolledtext.ScrolledText(root, width=50, height=20, state="disabled")
serial_monitor.pack(pady=5)

# Label to display the clickable URL
url_label = tk.Label(root, text="No URL received", fg="blue", cursor="hand2")
url_label.pack(pady=10)

# Start the GUI event loop
root.mainloop()


# In[ ]:




