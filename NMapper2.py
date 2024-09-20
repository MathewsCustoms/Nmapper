
import os
import subprocess
import customtkinter as ctk
import re
import threading
import socket
from tkinter import filedialog

# Set appearance mode to dark
ctk.set_appearance_mode("dark")

# Initialize the customTkinter app
app = ctk.CTk()
app.geometry("600x625")
app.title("Nmapper")

# List to keep track of command history
command_history = []

# Variable to keep track of the current process
current_process = None
process_lock = threading.Lock()

# Function to remove text inside parentheses
def remove_comments(command):
    return re.sub(r'\s*\(.*?\)', '', command)

# Function to validate if the target address is an IP address or FQDN
def is_valid_target(target):
    try:
        socket.inet_aton(target)  # Check if it's an IP address
        return True
    except socket.error:
        try:
            socket.gethostbyname(target)  # Check if it's an FQDN
            return True
        except socket.error:
            return False

# Function to dynamically update the final command entry
def update_command_entry(*args):
    command = command_selection.get()  # Get selected Nmap command
    target = target_entry.get()  # Get the target address
    clean_command = remove_comments(command)  # Clean the selected command
    full_command = f"nmap {clean_command} {target}" if target else f"nmap {clean_command}"
    final_command_entry.delete(0, ctk.END)
    final_command_entry.insert(0, full_command)

# Function to populate the final command entry with a history command
def load_from_history(event):
    selected_command = command_history_dropdown.get()
    final_command_entry.delete(0, ctk.END)
    final_command_entry.insert(0, selected_command)

# Function to send the Nmap command from the final command entry
def send_nmap_command():
    global current_process
    full_command = final_command_entry.get()  # Use the final command entry box as the command
    
    if not full_command.startswith("nmap"):
        status_box.insert(ctk.END, "Error: Invalid command. Command must start with 'nmap'.\n")
        status_box.see(ctk.END)
        return
    
    target = target_entry.get()  # Get the target address
    if not is_valid_target(target):
        status_box.insert(ctk.END, "Error: Invalid target address. Must be an IP address or FQDN.\n")
        status_box.see(ctk.END)
        return
    
    # Add the new command to the history and update the dropdown
    if full_command not in command_history:
        command_history.append(full_command)
        command_history_dropdown.configure(values=command_history)
    
    # Update status box to show the command being sent
    status_box.insert(ctk.END, f"Sending Command: {full_command}\n")
    status_box.insert(ctk.END, "-" * 50 + "\n")
    status_box.see(ctk.END)  # Auto-scroll
    
    # If a process is already running, terminate it
    if current_process and current_process.poll() is None:
        current_process.terminate()
        status_box.insert(ctk.END, "Previous command terminated.\n")
    
    # Start a new thread to run the Nmap command
    threading.Thread(target=run_nmap_command, args=(full_command,), daemon=True).start()

def run_nmap_command(command):
    global current_process
    with process_lock:
        current_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Read and display the output in real-time
    for line in current_process.stdout:
        status_box.insert(ctk.END, line.decode('utf-8'))
        status_box.see(ctk.END)  # Auto-scroll as output comes in
    
    status_box.insert(ctk.END, "\n" + "-" * 50 + "\nCommand Finished\n")
    status_box.see(ctk.END)

# Function to stop the current Nmap command
def stop_nmap_command():
    global current_process
    with process_lock:
        if current_process and current_process.poll() is None:
            current_process.terminate()
            status_box.insert(ctk.END, "Nmap command stopped.\n")
            status_box.see(ctk.END)

# Function to save the scan output to a file
def save_scan_output():
    output = status_box.get("1.0", ctk.END)  # Get the content from the status box
    if not output.strip():
        status_box.insert(ctk.END, "No output to save.\n")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:  # Check if a file path was selected
        with open(file_path, 'w') as file:
            file.write(output)
        status_box.insert(ctk.END, f"Scan output saved to {file_path}\n")


# List of Nmap commands
nmap_commands = [
    "-sP (Ping Scan)",                 
    "-sS (TCP SYN Scan)",              
    "-sU (UDP Scan)",                  
    "-O (OS Detection)",               
    "-A (Aggressive Scan)",            
    "-sV (Version Detection)",         
    "-p- (Scan All Ports)",            
    "--script=vuln (Vulnerability Scan)",  
    "-Pn (Skip Host Discovery)",       
    "-T4 (Faster Scan)",               
    "-T5 (Fastest Scan)",              
    "--top-ports 100 (Top 100 Ports)", 
    "--traceroute (Traceroute)",       
    "-sT (TCP Connect Scan)",          
    "-sT -sU (TCP And UDP Scan)",
    "-p- -sS -sU -A --script=vuln --traceroute (Full Stealth Scan)"
]

custom_font = ("Consolas", 16)
custom_font2 = ("Consolas", 16)
custom_font3 = ("Consolas", 14)

# Create UI elements
command_label = ctk.CTkLabel(app, text="Select Nmap Command:", font=custom_font)
command_label.grid(row=0, column=0, padx=10, pady=10, sticky="n")

command_selection = ctk.CTkComboBox(app, values=nmap_commands, width=370, font=custom_font3)
command_selection.grid(row=0, column=1, padx=10, pady=10, sticky="n")
command_selection.bind("<<ComboboxSelected>>", update_command_entry)  # Bind event to update command

target_label = ctk.CTkLabel(app, text="Enter Target Address:", font=custom_font)
target_label.grid(row=1, column=0, padx=10, pady=10, sticky="n")

target_entry = ctk.CTkEntry(app, width=370, font=custom_font3)
target_entry.grid(row=1, column=1, padx=10, pady=10, sticky="n")
target_entry.bind("<KeyRelease>", update_command_entry)  # Update dynamically as user types

final_command_label = ctk.CTkLabel(app, text="Full Nmap Command:", font=custom_font)
final_command_label.grid(row=2, column=0, padx=10, pady=10, sticky="n")

final_command_entry = ctk.CTkEntry(app, width=370, font=custom_font3)
final_command_entry.grid(row=2, column=1, padx=10, pady=10, sticky="n")

send_button = ctk.CTkButton(app, text="Start Scan", fg_color="#20CC00", hover_color="#53FF33", text_color="#000000", font=custom_font2, command=send_nmap_command)
send_button.grid(row=3, column=0, columnspan=1, pady=10, sticky="e")

stop_button = ctk.CTkButton(app, text="Stop Scan", fg_color="#CC2020", hover_color="#FF3333", text_color="#FFFFFF", font=custom_font2, command=stop_nmap_command)
stop_button.grid(row=3, column=1, columnspan=1, padx=60, pady=10, sticky="e")

# Dropdown for command history
command_history_dropdown = ctk.CTkComboBox(app, values=[], width=550, font=custom_font3)
command_history_dropdown.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="n")
command_history_dropdown.set("Nmap History")
command_history_dropdown.bind("<<ComboboxSelected>>", load_from_history)  # Bind event to load history command

# Status box to show command output
status_box = ctk.CTkTextbox(app, width=550, height=300)
status_box.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="n")
#status_box.configure(state='disabled')  # Set the status box to read-only


save_button = ctk.CTkButton(app, text="Save Scan", fg_color="#20CC00", hover_color="#53FF33", text_color="#000000", font=custom_font2, command=save_scan_output)
save_button.grid(row=6, column=0, columnspan=2, pady=10, sticky="n")


# Run the app
app.mainloop()
