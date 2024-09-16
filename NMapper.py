import os
import subprocess
import customtkinter as ctk

# Set appearance mode to dark
ctk.set_appearance_mode("dark")

# Initialize the customTkinter app
app = ctk.CTk()
app.geometry("600x525")
app.title("Nmapper")

# Function to send the selected Nmap command and update the status box
def send_nmap_command():
    command = command_selection.get().split()[0]  # Get selected Nmap command
    target = target_entry.get()  # Get the target address
    if target:
        full_command = f"nmap {command} {target}"
        status_box.insert(ctk.END, f"Sending Command: {full_command}\n")
        status_box.insert(ctk.END, "-"*50 + "\n")
        status_box.see(ctk.END)  # Auto-scroll
        
        # Execute the Nmap command and capture the output
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Read and display the output in real-time
        for line in process.stdout:
            status_box.insert(ctk.END, line.decode('utf-8'))
            status_box.see(ctk.END)  # Auto-scroll as output comes in
        
        status_box.insert(ctk.END, "\n" + "-"*50 + "\nCommand Finished\n")
        status_box.see(ctk.END)

#  List of Nmap commands
nmap_commands = [
    "-sP (Ping Scan)",                 # Ping scan
    "-sS (TCP SYN Scan)",              # TCP SYN scan
    "-sU (UDP Scan)",                  # UDP scan
    "-O (OS Detection)",               # OS detection
    "-A (Aggressive Scan)",            # Aggressive scan
    "-sV (Version Detection)",         # Service version detection
    "-p- (Scan All Ports)",            # Scan all 65535 ports
    "--script=vuln (Vulnerability Scan)",  # Scan using vulnerability scripts
    "-Pn (Skip Host Discovery)",       # Skip host discovery (assume host is up)
    "-T4 (Faster Scan)",               # Faster scan (balanced)
    "-T5 (Fastest Scan)",              # Fastest scan speed
    "--top-ports 100 (Top 100 Ports)", # Scan top 100 most common ports
    "--traceroute (Traceroute)",       # Trace the path to the target
    "-sT (TCP Connect Scan)",           # TCP connect scan (less stealthy)
    "-sT -sU (TCP And UDP Scan)",
    "-p- -sS -sU -A --script=vuln --traceroute(Full Stealth Scan)"
]   
custom_font = ("Consolas", 22)
custom_font2 = ("Consolas" , 16)
custom_font3 = ("Consolas", 14)
# Create UI elements
command_label = ctk.CTkLabel(app, text="Select Nmap Command:", 
                             font=custom_font)
command_label.pack(pady=1)

# Dropdown for Nmap commands with custom colors
command_selection = ctk.CTkComboBox(app, values=nmap_commands, width=400, font=custom_font3)
command_selection.pack(pady=5)

target_label = ctk.CTkLabel(app, text="Enter Target Address:", 
                            font=custom_font)
target_label.pack(pady=1)

# Input box for the target address
target_entry = ctk.CTkEntry(app, width=300, font=custom_font3)
target_entry.pack(pady=5)

# Send button with custom dark green colors
send_button = ctk.CTkButton(app, text="Send Nmap Command", 
                            fg_color="#20CC00",  
                            hover_color="#53FF33",
                            text_color="#000000",
                            font=custom_font2,
                            command=send_nmap_command)  
                            
send_button.pack(pady=10)

# Status box to show command output
status_box = ctk.CTkTextbox(app, width=550, height=300)
status_box.pack(pady=10)

# Run the app
app.mainloop()
