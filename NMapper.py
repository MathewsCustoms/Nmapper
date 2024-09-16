import os
import subprocess
import customtkinter as ctk
import re
import threading
import socket

# Set appearance mode to dark
ctk.set_appearance_mode("dark")

# Initialize the customTkinter app
app = ctk.CTk()
app.geometry("600x575")  # Adjusted height to accommodate the new buttons
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
        # Check if it's an IP address
        socket.inet_aton(target)
        return True
    except socket.error:
        # Not an IP address, check if it's an FQDN
        try:
            socket.gethostbyname(target)
            return True
        except socket.error:
            return False

# Function to send the selected Nmap command and update the status box
def send_nmap_command():
    global current_process
    command = command_selection.get()  # Get selected Nmap command
    target = target_entry.get()  # Get the target address
    
    if not is_valid_target(target):
        status_box.insert(ctk.END, "Error: Invalid target address. Must be an IP address or FQDN.\n")
        status_box.see(ctk.END)
        return
    
    clean_command = remove_comments(command)  # Clean command by removing comments
    full_command = f"nmap {clean_command} {target}"
    
    # Add the new command to the history and update the dropdown
    if full_command not in command_history:
        command_history.append(full_command)
        command_history_dropdown.configure(values=command_history)
    
    # Update status box to show the command being sent
    status_box.insert(ctk.END, f"Sending Command: {full_command}\n")
    status_box.insert(ctk.END, "-"*50 + "\n")
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
    
    status_box.insert(ctk.END, "\n" + "-"*50 + "\nCommand Finished\n")
    status_box.see(ctk.END)

# Function to stop the current Nmap command
def stop_nmap_command():
    global current_process
    with process_lock:
        if current_process and current_process.poll() is None:
            current_process.terminate()
            status_box.insert(ctk.END, "Nmap command stopped.\n")
            status_box.see(ctk.END)

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

target_label = ctk.CTkLabel(app, text="Enter Target Address:", font=custom_font)
target_label.grid(row=1, column=0, padx=10, pady=10, sticky="n")

target_entry = ctk.CTkEntry(app, width=370, font=custom_font3)
target_entry.grid(row=1, column=1, padx=10, pady=10, sticky="n")

send_button = ctk.CTkButton(app, text="Send Nmap Command", fg_color="#20CC00", hover_color="#53FF33", text_color="#000000", font=custom_font2, command=send_nmap_command)
send_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="n")

stop_button = ctk.CTkButton(app, text="Stop Nmap Command", fg_color="#CC2020", hover_color="#FF3333", text_color="#FFFFFF", font=custom_font2, command=stop_nmap_command)
stop_button.grid(row=3, column=0, columnspan=2, pady=10, sticky="s")

# Dropdown for command history
command_history_dropdown = ctk.CTkComboBox(app, values=[], width=550, font=custom_font3)
command_history_dropdown.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="n")
command_history_dropdown.set("Nmap History")

# Status box to show command output
status_box = ctk.CTkTextbox(app, width=550, height=300)
status_box.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="n")

# Run the app
app.mainloop()

