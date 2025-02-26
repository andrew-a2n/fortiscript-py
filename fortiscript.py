import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import csv
import re

def open_csv_file():
    file_path = filedialog.askopenfilename(title="Open CSV File", filetypes=[("CSV files", "*.csv")])
    if file_path:
        display_csv_data(file_path)
        
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, command=lambda: \
               treeview_sort_column(tv, col, not reverse))
               
def truncate_string(s, length):
    if len(s) > length:
        return s[:length-3] + '...'  # Subtract 3 for the ellipsis
    return s
               
def copy_copy(box_data):
    #print(box_data)
    root.clipboard_clear()
    root.clipboard_append(box_data)
    
def file_save(my_script, win_parent):
    f = filedialog.asksaveasfile(mode='w', defaultextension=".txt", initialfile="output.txt", parent=win_parent)
    if f is None:
        return
    try:    
        f.write(my_script)
        f.close()
        status_label.config(text=f"File written: {str(f.name)}")
        win_parent.destroy()
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}")
               
def show_popup_window(text_data):
    window = tk.Toplevel(root)
    window.title('FortiScript')
    
    T = tk.Text(window)
    b1=tk.Button(window, text='Copy to Clipboard', command=lambda:copy_copy(T.get("1.0", tk.END)), bg='lightgreen')
    b2=tk.Button(window, text='Save to File', command=lambda:file_save(T.get("1.0", tk.END), window), bg='lightblue')
    
    b1.pack()
    b2.pack()
    T.pack(expand=True, fill=tk.BOTH)
    T.insert(tk.END, text_data)
    T.config(state=tk.DISABLED)
               
def convert_to_fortinet():
    if (clicked.get() == options[0]):
        print ("Processing Network Objects...")
        convert_address_objects()
    elif (clicked.get() == options[1]):
        print ("Processing Service Objects")
        convert_service_objects()
    elif (clicked.get() == options[2]):
        print ("Processing Network Groups")
        messagebox.showinfo("Not Implemented Yet","Coming Soon...Network Groups")
    elif (clicked.get() == options[3]):
        print ("Processing Service Groups")
        messagebox.showinfo("Not Implemented Yet","Coming Soon...Service Groups")
    elif (clicked.get() == options[4]):
        print ("Processing Policy Rules")
        messagebox.showinfo("Not Implemented Yet","Coming Soon...Policy Rules")
   
   
def convert_address_objects():
    #Regex to match the IP column to a single IP or a range of IP's. If the value does not match either of these then its not a proper IPv4 address, write a message to the console and skip it.
    iprange_regex = re.compile(r"(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3} - (\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}")
    ip_regex = re.compile(r"(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}")
    mask_regex = re.compile(r"^(255)\.(0|128|192|224|240|248|252|254|255)\.(0|128|192|224|240|248|252|254|255)\.(0|128|192|224|240|248|252|254|255)")
    try:
        #Header and footer for firewall address type objects
        header = "config firewall address\n"
        footer = "end\n"
        converted = ""
        
        #Iterate the array of table rows
        for parent in tree.get_children():
        
            #Store the values from the row columns
            ipv4_addr = str(tree.item(parent)["values"][1])
            mask = tree.item(parent)["values"][2]
            
            #Fortinet max string length for comment field is 255 characters so we need to truncate if the source data is longer
            comment = truncate_string(str(tree.item(parent)["values"][3]), 255)
            
            #Test for an ip range in the ipv4_address column
            if re.search(iprange_regex, ipv4_addr):
            
                #Split the IP range into an array of 2 variables, startip and endip, using the hyphen with space as delimeter
                split_ip = ipv4_addr.split(" - ")
                
                #Generate fortinet syntax for IP range object
                converted += ("    edit \"" + tree.item(parent)["values"][0] + "\"\n        set type iprange\n        set start-ip " + split_ip[0] + "\n        set end-ip " + split_ip[1] + "\n        set comment \"" + comment + "\"\n    next\n")
                
            #Test for a single IP string in the ipv4_address column
            elif re.search(ip_regex, ipv4_addr):
            
                #If the mask column has an explicit mask value then insert it into the output, otherwise we are hard coding a /32 mask into the output
                if mask:
                    if re.search(mask_regex, mask):
                        converted += ("    edit \"" + tree.item(parent)["values"][0] + "\"\n        set subnet " + tree.item(parent)["values"][1] + " " + mask + "\n        set comment \"" + comment + "\"\n    next\n")
                    else:
                        print(f"Unable to convert mask: {ipv4_addr} {mask}")
                else:
                    converted += ("    edit \"" + tree.item(parent)["values"][0] + "\"\n        set subnet " + tree.item(parent)["values"][1] + " " + "255.255.255.255" + "\n        set comment \"" + comment + "\"\n    next\n")
            
            #Cant handle any other object types here. If the regex doesn't match to an IP or range, then dump the values to the console for troubleshooting.
            else:
                print(f"Unable to convert IP: {ipv4_addr} {mask}")
        
        #Spawns a child window with a textbox containing the output of this function, the resulting completed fortinet script
        show_popup_window(header + converted + footer)
    except Exception as e:
       messagebox.showinfo("OH NO ITS AN ERROR!", e)


def convert_service_objects():
    #Regex to match the port column to a single port or a range of ports. If the value does not match either of these then its not a proper tcp/udp port, write a message to the console and skip it.
    portrange_regex = re.compile(r"^(([1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5]))-(([1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5]))$")
    port_regex = re.compile(r"^(([1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5]))$")
    type_regex = re.compile(r"^(tcp|udp)$")
    try:
        #Header and footer for firewall address type objects
        header = "config firewall service custom\n"
        footer = "end\n"
        converted = ""
        
        #Iterate the array of table rows
        for parent in tree.get_children():
        
            #Store the values from the row columns
            port_name = str(tree.item(parent)["values"][0])
            port_type = str(tree.item(parent)["values"][1]).lower()
            port = str(tree.item(parent)["values"][2])
            
            
            #Fortinet max string length for comment field is 255 characters so we need to truncate if the source data is longer
            comment = truncate_string(str(tree.item(parent)["values"][3]), 255)
            
            #Test for a valid port or range and type
            if ((re.search(portrange_regex, port) or re.search(port_regex, port)) and re.search(type_regex, port_type)):
            
                #Generate fortinet syntax for IP range object
                converted += ("    edit \"" + port_name + "\"\n        set " + port_type + "-portrange " + port + "\n        set comment \"" + comment + "\"\n    next\n")
                
            #Bad port definition, dump it to the console for troubleshooting.
            else:
                print(f"Unable to convert Port: {port_name} {port_type} {port}")
        
        #Spawns a child window with a textbox containing the output of this function, the resulting completed fortinet script
        show_popup_window(header + converted + footer)
    except Exception as e:
       messagebox.showinfo("OH NO ITS AN ERROR!", e)


def display_csv_data(file_path):
    try:
        with open(file_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  # Read the header row
            tree.delete(*tree.get_children())  # Clear the current data

            tree["columns"] = header
            for col in header:
                tree.heading(col, text=col, command=lambda _col=col: \
                     treeview_sort_column(tree, col, False))
                tree.column(col, width=100)

            for row in csv_reader:
                tree.insert("", "end", values=row)

            status_label.config(text=f"CSV file loaded: {file_path}")
            convert_button.config(state=tk.NORMAL)

    except Exception as e:
        status_label.config(text=f"Error: {str(e)}")

def clear_treeview():
    tree.delete(*tree.get_children())  # Clear the current data
    convert_button.config(state=tk.DISABLED)
    status_label.config(text="No data loaded")
    
def show_help_dialog():
    messagebox.showinfo("Friendly Help Dialog","You must upload a csv spreadsheet with columns exactly like: Name,IPv4 address,Mask,Comments\n\nInclude the header row")
    

# Dropdown menu options 
options = [ 
    "Network, host, IP Range", 
    "Services", 
    "Network Groups", 
    "Service Groups", 
    "Policy Rules"
]

root = tk.Tk()
root.title("Fortinet Script Generator")

clicked = tk.StringVar()
clicked.set("Network, host, IP Range")

frame = tk.Frame(root)
frame.pack()

bottomframe = tk.Frame(root)
bottomframe.pack( side = tk.BOTTOM, expand=True, fill="both" )

drop = tk.OptionMenu( frame , clicked , *options ) 
drop.pack(padx=20, pady= 10, side=tk.LEFT) 

open_button = tk.Button(frame, text="Open CSV File", command=open_csv_file)
open_button.pack(padx=20, pady=10, side=tk.LEFT)

clear_button = tk.Button(frame, text="Clear Data", command=clear_treeview)
clear_button.pack(padx=20, pady=10, side=tk.LEFT)

convert_button = tk.Button(frame, text="Convert!", command=convert_to_fortinet, state=tk.DISABLED)
convert_button.pack(padx=20, pady=10, side=tk.LEFT)

help_button = tk.Button(frame, text="Help!", command=show_help_dialog)
help_button.pack(padx=20, pady=20, side=tk.LEFT)

tree = ttk.Treeview(bottomframe, show="headings")
tree.pack(padx=20, pady=20, fill="both", expand=True)

status_label = tk.Label(bottomframe, text="", padx=20, pady=10)
status_label.pack()

root.mainloop()
