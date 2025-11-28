"""
Nikon Z Camera Menu Visual Editor
A GUI tool for visually editing Nikon Z camera menu settings files
Supports both Z5 Mark 1 and Mark 2 formats with auto-detection
"""

import sys
import struct
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from pathlib import Path

class NikonZMenuEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Nikon Z Camera Menu Editor")
        self.root.geometry("1200x800")
        
        # Data storage
        self.current_file = None
        self.file_data = None
        self.config_sections = {}
        self.modified = False
        
        # Menu definitions - Updated based on Nikon Z5 Mark 2 Reference Guide
        self.imenu_names = {
            0: "Active D-Lighting", 1: "AF area mode", 2: "AF tracking sensitivity", 
            3: "Auto bracketing", 4: "Bluetooth connection", 5: "Monitor/viewfinder brightness", 
            6: "Color space", 7: "Choose image area", 8: "Custom controls", 
            9: "Shutter type", 10: "Electronic front-curtain shutter", 11: "Exposure compensation", 
            12: "Exposure delay mode", 13: "Flash compensation", 14: "Flash mode", 
            15: "Focus Mode", 16: "Focus peaking", 17: "HDR", 18: "Highlight-weighted metering",
            19: "High ISO NR", 20: "Image review", 21: "Image Quality", 22: "Image Size", 
            23: "ISO display", 24: "ISO sensitivity settings", 25: "Long exposure NR", 
            26: "Apply settings to live view", 27: "Metering", 28: "Matrix metering", 
            29: "Multiple Exposure", 30: "Peaking Highlights", 31: "Set Picture Control", 
            32: "Release Mode", 33: "Silent Photography", 34: "Split-screen display zoom", 
            35: "Vibration Reduction", 36: "White Balance", 37: "White balance fine-tuning",
            38: "Wifi connection", 39: "View memory card info", 40: "Interval timer shooting", 
            41: "Time-lapse movie", 42: "Focus shift shooting", 43: "Wind noise reduction",
            44: "Zebras", 45: "Movie quality", 46: "Movie frame size/frame rate",
            47: "Movie microphone", 48: "Movie wind noise reduction", 49: "HDMI output resolution",
            50: "Copyright information", 51: "Group flash options", 52: "FV lock",
            53: "BKT button assignment", 54: "Fn1 button assignment", 55: "Fn2 button assignment",
            56: "AF-assist illuminator", 57: "Beep options", 58: "Touch controls",
            59: "Eye-Detection AF", 60: "Animal-Detection AF", 61: "Subject tracking",
            62: "Wide-area AF (L)", 63: "Wide-area AF (S)", 64: "Auto-area AF",
            65: "Pinpoint AF", 66: "Single-point AF", 67: "Dynamic-area AF",
            68: "3D-tracking", 69: "Group-area AF", 70: "Auto ISO sensitivity control",
            71: "Spot metering", 72: "Center-weighted metering", 73: "Flash sync speed",
            74: "Flash control mode", 75: "Wireless flash control", 76: "Built-in flash mode",
            77: "Commander mode", 78: "Remote flash control", 79: "TTL flash mode",
            80: "Manual flash mode"
        }
        
        self.mode_names = {
            29: "Program (P)", 30: "Shutter Priority (S)", 31: "Aperture Priority (A)", 
            32: "Manual (M)", 33: "Auto", 34: "U1 (User Setting 1)", 
            35: "U2 (User Setting 2)", 36: "U3 (User Setting 3)"
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Menu File...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file, state="disabled")
        file_menu.add_command(label="Save As...", command=self.save_as_file, state="disabled")
        file_menu.add_separator()
        file_menu.add_command(label="Export Settings...", command=self.export_settings, state="disabled")
        file_menu.add_command(label="Import Settings...", command=self.import_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Analyze File Structure", command=self.analyze_structure, state="disabled")
        tools_menu.add_command(label="Backup Original", command=self.backup_file, state="disabled")
        tools_menu.add_command(label="Verify CRC", command=self.verify_crc, state="disabled")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # File info frame
        info_frame = ttk.LabelFrame(main_frame, text="File Information", padding="5")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        # File info labels
        ttk.Label(info_frame, text="File:").grid(row=0, column=0, sticky=tk.W)
        self.file_label = ttk.Label(info_frame, text="No file loaded", foreground="gray")
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(info_frame, text="Camera:").grid(row=1, column=0, sticky=tk.W)
        self.camera_label = ttk.Label(info_frame, text="", foreground="gray")
        self.camera_label.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(info_frame, text="Firmware:").grid(row=2, column=0, sticky=tk.W)
        self.firmware_label = ttk.Label(info_frame, text="", foreground="gray")
        self.firmware_label.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        # Configuration selection frame
        config_frame = ttk.LabelFrame(main_frame, text="Camera Modes", padding="5")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        config_frame.columnconfigure(0, weight=1)
        
        # Mode listbox
        self.mode_listbox = tk.Listbox(config_frame, height=10)
        self.mode_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.mode_listbox.bind('<<ListboxSelect>>', self.on_mode_select)
        
        scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=self.mode_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.mode_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="5")
        settings_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.rowconfigure(1, weight=1)
        
        # Mode info
        mode_info_frame = ttk.Frame(settings_frame)
        mode_info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        mode_info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(mode_info_frame, text="Mode:").grid(row=0, column=0, sticky=tk.W)
        self.current_mode_label = ttk.Label(mode_info_frame, text="", font=("TkDefaultFont", 10, "bold"))
        self.current_mode_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Notebook for different setting categories
        self.notebook = ttk.Notebook(settings_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # i-menu tab
        self.setup_imenu_tab()
        
        # User Settings tab (for U1, U2, U3)
        self.setup_user_settings_tab()
        
        # Other settings tab
        self.setup_other_settings_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Load a menu file to begin")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Store menu references for enabling/disabling
        self.file_menu = file_menu
        self.tools_menu = tools_menu
        
    def setup_imenu_tab(self):
        """Setup the i-menu configuration tab"""
        imenu_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(imenu_frame, text="i-menu Configuration")
        
        # Instructions
        ttk.Label(imenu_frame, text="Configure the 12 slots in your camera's i-menu:", 
                 font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Enhanced explanation based on Z5 Mark 2 Reference Guide
        explanation_text = ("The i-menu provides quick access to frequently used settings. Press the 'i' button on your camera "
                          "to access this 3×4 grid of customizable functions. Each shooting mode (P, S, A, M, U1, U2, U3) "
                          "can have its own i-menu configuration. Available options include focus settings, exposure controls, "
                          "image quality settings, custom functions, and more.")
        ttk.Label(imenu_frame, text=explanation_text, wraplength=700, foreground="gray", 
                 font=("TkDefaultFont", 9)).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        # i-menu slots
        self.imenu_vars = []
        self.imenu_combos = []
        
        # Create sorted list of i-menu options
        imenu_options = ["(Empty)"] + [f"{name} ({id})" for id, name in sorted(self.imenu_names.items())]
        
        # Create frames for the two rows of settings
        row1_frame = ttk.LabelFrame(imenu_frame, text="Top Row (Slots 1-6)", padding="5")
        row1_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5), pady=5)
        
        row2_frame = ttk.LabelFrame(imenu_frame, text="Bottom Row (Slots 7-12)", padding="5")
        row2_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0), pady=5)
        
        for i in range(12):
            is_bottom_row = i >= 6
            parent_frame = row2_frame if is_bottom_row else row1_frame
            
            # Calculate row within the frame (0-5)
            row = i % 6
            
            # Camera grid position
            cam_row = 2 if is_bottom_row else 1
            cam_col = (i % 6) + 1
            
            # Slot label with position indicator
            position_text = f"Pos {i+1} (R{cam_row}, C{cam_col}):"
            ttk.Label(parent_frame, text=position_text).grid(row=row, column=0, sticky=tk.W, padx=(0, 5), pady=2)
            
            # Combo box for selection
            var = tk.StringVar()
            combo = ttk.Combobox(parent_frame, textvariable=var, values=imenu_options, width=25, state="readonly")
            combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
            combo.bind('<<ComboboxSelected>>', lambda e, slot=i: self.on_imenu_change(slot))
            
            self.imenu_vars.append(var)
            self.imenu_combos.append(combo)
            
        # Configure weights
        imenu_frame.columnconfigure(0, weight=1)
        imenu_frame.columnconfigure(1, weight=1)
        
        # Add visual layout representation
        layout_frame = ttk.LabelFrame(imenu_frame, text="i-menu Layout on Camera Screen", padding="5")
        layout_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # Create visual grid showing how the i-menu appears on camera (2 rows x 6 columns)
        self.layout_labels = []
        for i in range(12):
            row = (i // 6)
            col = (i % 6)
            
            label = ttk.Label(layout_frame, text=f"Pos {i+1}\n(Empty)", 
                            relief="solid", borderwidth=1, width=15, anchor="center",
                            font=("TkDefaultFont", 8))
            label.grid(row=row, column=col, padx=2, pady=2, sticky=(tk.W, tk.E))
            self.layout_labels.append(label)
        
        # Configure layout frame columns
        for i in range(6):
            layout_frame.columnconfigure(i, weight=1)
    
    def setup_user_settings_tab(self):
        """Setup the User Settings (U1, U2, U3) management tab"""
        user_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(user_frame, text="User Settings (U1/U2/U3)")
        
        # Instructions
        ttk.Label(user_frame, text="Manage User Settings (U1, U2, U3):", 
                 font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Enhanced explanation based on Z5 Mark 2 Reference Guide
        explanation_text = ("User Settings (U1, U2, U3) store complete camera configurations including:\n"
                          "• Exposure settings (ISO, aperture, shutter speed)\n"
                          "• Focus settings (AF mode, AF area mode, tracking)\n" 
                          "• i-menu customization (all 12 slots)\n"
                          "• Picture Control settings\n"
                          "• Custom function assignments\n"
                          "• Movie settings and more\n\n"
                          "Use this to quickly switch between different shooting scenarios.")
        ttk.Label(user_frame, text=explanation_text, wraplength=600, foreground="gray", 
                 font=("TkDefaultFont", 9)).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        # Current User Setting info
        current_frame = ttk.LabelFrame(user_frame, text="Currently Selected User Setting", padding="5")
        current_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        current_frame.columnconfigure(1, weight=1)
        
        ttk.Label(current_frame, text="Mode:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.current_user_mode_label = ttk.Label(current_frame, text="Select a User Setting from the left panel", 
                                               font=("TkDefaultFont", 9), foreground="gray")
        self.current_user_mode_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # User Setting operations
        operations_frame = ttk.LabelFrame(user_frame, text="User Setting Operations", padding="5")
        operations_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Copy from other modes
        ttk.Label(operations_frame, text="Copy settings from:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.copy_source_var = tk.StringVar()
        self.copy_source_combo = ttk.Combobox(operations_frame, textvariable=self.copy_source_var, 
                                            values=[], width=25, state="readonly")
        self.copy_source_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        self.copy_button = ttk.Button(operations_frame, text="Copy Settings", command=self.copy_user_settings)
        self.copy_button.grid(row=0, column=2, padx=(5, 0), pady=5)
        
        # Reset User Setting
        ttk.Label(operations_frame, text="Reset User Setting:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.reset_button = ttk.Button(operations_frame, text="Reset to Default", command=self.reset_user_settings)
        self.reset_button.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        operations_frame.columnconfigure(1, weight=1)
        
        # User Setting details
        details_frame = ttk.LabelFrame(user_frame, text="User Setting Details", padding="5")
        details_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Text widget for showing user setting details
        self.user_details_text = tk.Text(details_frame, height=10, wrap=tk.WORD, font=("Courier", 9))
        user_scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.user_details_text.yview)
        self.user_details_text.configure(yscrollcommand=user_scrollbar.set)
        
        self.user_details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        user_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        
        # Configure main frame
        user_frame.columnconfigure(0, weight=1)
        user_frame.rowconfigure(4, weight=1)
        
        # Initially disable buttons
        self.copy_button.config(state="disabled")
        self.reset_button.config(state="disabled")
    
    def setup_other_settings_tab(self):
        """Setup the other settings tab"""
        other_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(other_frame, text="Other Settings")
        
        # File prefix
        prefix_frame = ttk.LabelFrame(other_frame, text="File Naming", padding="5")
        prefix_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        prefix_frame.columnconfigure(1, weight=1)
        
        ttk.Label(prefix_frame, text="File Prefix:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.prefix_var = tk.StringVar()
        self.prefix_entry = ttk.Entry(prefix_frame, textvariable=self.prefix_var, width=10)
        self.prefix_entry.grid(row=0, column=1, sticky=tk.W)
        self.prefix_entry.bind('<KeyRelease>', self.on_prefix_change)
        
        ttk.Label(prefix_frame, text="(e.g., 'DSC' for DSC_0001.JPG)").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Additional settings placeholder
        additional_frame = ttk.LabelFrame(other_frame, text="Additional Settings", padding="5")
        additional_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        ttk.Label(additional_frame, text="More settings will be added as the file format is better understood.", 
                 foreground="gray", wraplength=400).grid(row=0, column=0, sticky=tk.W)
        
        other_frame.columnconfigure(0, weight=1)
        other_frame.rowconfigure(1, weight=1)
    
    def open_file(self):
        """Open a camera menu file"""
        filename = filedialog.askopenfilename(
            title="Open Nikon Z Menu File",
            filetypes=[
                ("Camera Menu Files", "*.bin *.BIN"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            self.load_file(filename)
    
    def load_file(self, filename):
        """Load and analyze a camera menu file"""
        try:
            with open(filename, "rb") as f:
                self.file_data = bytearray(f.read())
            
            self.current_file = filename
            self.modified = False
            
            # Update file info
            self.file_label.config(text=os.path.basename(filename), foreground="black")
            
            # Extract camera info
            if len(self.file_data) > 10:
                model_bytes = self.file_data[0:11]
                null_pos = model_bytes.find(0)
                if null_pos >= 0:
                    model_bytes = model_bytes[:null_pos]
                try:
                    camera_model = model_bytes.decode('ascii')
                    self.camera_label.config(text=camera_model, foreground="black")
                except UnicodeDecodeError:
                    self.camera_label.config(text="Unknown", foreground="black")
            
            if len(self.file_data) > 28:
                fw_bytes = self.file_data[24:29]
                null_pos = fw_bytes.find(0)
                if null_pos >= 0:
                    fw_bytes = fw_bytes[:null_pos]
                try:
                    firmware = fw_bytes.decode('ascii')
                    self.firmware_label.config(text=firmware, foreground="black")
                except UnicodeDecodeError:
                    self.firmware_label.config(text="Unknown", foreground="black")
            
            # Find configuration sections
            self.find_config_sections()
            
            # Update UI
            self.populate_mode_list()
            self.enable_menus()
            
            self.status_var.set(f"Loaded: {os.path.basename(filename)} - {len(self.config_sections)} modes found")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def find_config_sections(self):
        """Find and analyze configuration sections in the file"""
        self.config_sections = {}
        
        # Check camera model
        camera_model = self.camera_label.cget("text")
        
        # Define offsets based on camera model
        if "Z5_2" in camera_model:
            # Z5 Mark 2 offsets (from analysis)
            standard_sections = [
                (92549, "Manual"),
                (295672, "Program"),
                (294104, "Aperture Priority"),
                (294152, "U1"),
                (294132, "U2"),
                (294108, "U3")
            ]
        else:
            # Z5 Mark 1 standard offsets
            standard_sections = [
                (169824, "Primary M/A/S/P/Auto"),
                (176452, "Secondary M/A/S/P/Auto"), 
                (183080, "U1"),
                (189708, "U2"),
                (196336, "U3")
            ]
        
        for offset, name in standard_sections:
            if self.is_valid_config_section(offset):
                mode_id = self.file_data[offset + 1240]
                mode_name = self.mode_names.get(mode_id, f"Unknown Mode {mode_id}")
                self.config_sections[f"{name} ({mode_name})"] = {
                    'offset': offset,
                    'mode_id': mode_id,
                    'mode_name': mode_name,
                    'source': 'standard'
                }
        
        # If no standard sections found, use auto-detection
        if not self.config_sections:
            self.auto_detect_sections()
    
    def auto_detect_sections(self):
        """Auto-detect configuration sections (for Z5 Mark 2)"""
        mode_patterns = {
            29: "Program (P)", 30: "Shutter Priority (S)", 31: "Aperture Priority (A)", 
            32: "Manual (M)", 33: "Auto", 34: "U1 (User Setting 1)", 
            35: "U2 (User Setting 2)", 36: "U3 (User Setting 3)"
        }
        
        found_sections = {}
        
        for mode_id, mode_name in mode_patterns.items():
            candidates = []
            pos = 0
            
            while True:
                pos = self.file_data.find(bytes([mode_id]), pos)
                if pos == -1:
                    break
                
                potential_section_start = pos - 1240
                if potential_section_start >= 0 and self.is_valid_config_section(potential_section_start):
                    # Score this section
                    score = self.score_config_section(potential_section_start)
                    candidates.append({
                        'offset': potential_section_start,
                        'score': score,
                        'mode_id': mode_id,
                        'mode_name': mode_name
                    })
                
                pos += 1
            
            # Keep the best candidate for each mode
            if candidates:
                best = max(candidates, key=lambda x: x['score'])
                section_name = f"{mode_name} (Auto-detected)"
                found_sections[section_name] = {
                    'offset': best['offset'],
                    'mode_id': best['mode_id'],
                    'mode_name': best['mode_name'],
                    'source': 'auto'
                }
        
        self.config_sections = found_sections
    
    def is_valid_config_section(self, offset):
        """Check if an offset contains a valid configuration section"""
        if offset + 6628 > len(self.file_data):
            return False
        
        # Check data density
        section_data = self.file_data[offset:offset+6628]
        zero_count = section_data.count(0)
        data_density = (len(section_data) - zero_count) / len(section_data)
        
        return data_density >= 0.01  # At least 1% non-zero data
    
    def score_config_section(self, offset):
        """Score a configuration section for quality"""
        if not self.is_valid_config_section(offset):
            return 0
        
        # Calculate data density
        section_data = self.file_data[offset:offset+6628]
        zero_count = section_data.count(0)
        data_density = (len(section_data) - zero_count) / len(section_data)
        
        # Count valid i-menu entries
        imenu_offset = offset + 924
        valid_entries = 0
        for i in range(12):
            pos = imenu_offset + i * 4
            if pos < len(self.file_data):
                item_id = self.file_data[pos]
                if item_id in self.imenu_names:
                    valid_entries += 1
        
        return (data_density * 50) + (valid_entries * 5)
    
    def populate_mode_list(self):
        """Populate the mode selection listbox"""
        self.mode_listbox.delete(0, tk.END)
        for section_name in sorted(self.config_sections.keys()):
            self.mode_listbox.insert(tk.END, section_name)
        
        # Select first item if available
        if self.config_sections:
            self.mode_listbox.selection_set(0)
            self.on_mode_select(None)
    
    def on_mode_select(self, event):
        """Handle mode selection"""
        selection = self.mode_listbox.curselection()
        if selection:
            section_name = self.mode_listbox.get(selection[0])
            self.load_section_settings(section_name)
    
    def load_section_settings(self, section_name):
        """Load settings for a configuration section"""
        if section_name not in self.config_sections:
            return
        
        section = self.config_sections[section_name]
        offset = section['offset']
        
        # Update mode label
        self.current_mode_label.config(text=section['mode_name'])
        
        # Update User Settings tab if this is a user setting
        self.update_user_settings_display(section_name, section)
        
        # Load i-menu settings
        imenu_offset = offset + 924
        for i in range(12):
            pos = imenu_offset + i * 4
            if pos < len(self.file_data):
                item_id = self.file_data[pos]
                if item_id == 0:
                    self.imenu_vars[i].set("(Empty)")
                elif item_id in self.imenu_names:
                    self.imenu_vars[i].set(f"{self.imenu_names[item_id]} ({item_id})")
                else:
                    self.imenu_vars[i].set(f"Unknown/Invalid ({item_id})")
        
        # Update visual layout
        self.update_imenu_layout()
        
        # Load file prefix
        prefix_offset = offset + 1540
        if prefix_offset + 10 < len(self.file_data):
            prefix_bytes = self.file_data[prefix_offset:prefix_offset+10]
            null_pos = prefix_bytes.find(0)
            if null_pos >= 0:
                prefix_bytes = prefix_bytes[:null_pos]
            try:
                prefix = prefix_bytes.decode('ascii')
                self.prefix_var.set(prefix)
            except UnicodeDecodeError:
                self.prefix_var.set("")
    
    def update_user_settings_display(self, section_name, section):
        """Update the User Settings tab display"""
        mode_name = section['mode_name']
        
        # Check if this is a User Setting
        if any(mode_name.startswith(u) for u in ["U1", "U2", "U3"]):
            self.current_user_mode_label.config(text=mode_name, foreground="black")
            
            # Enable buttons
            self.copy_button.config(state="normal")
            self.reset_button.config(state="normal")
            
            # Update copy source combo with other modes
            other_modes = [name for name in self.config_sections.keys() if name != section_name]
            self.copy_source_combo.config(values=other_modes)
            
            # Update details display
            self.update_user_details_display(section)
            
        else:
            self.current_user_mode_label.config(text="Select a User Setting from the left panel", foreground="gray")
            self.copy_button.config(state="disabled")
            self.reset_button.config(state="disabled")
            self.user_details_text.delete(1.0, tk.END)
    
    def update_user_details_display(self, section):
        """Update the user setting details display"""
        self.user_details_text.delete(1.0, tk.END)
        
        offset = section['offset']
        details = []
        
        details.append(f"=== {section['mode_name']} Details ===\n")
        details.append(f"File Offset: {offset} (0x{offset:x})\n")
        details.append(f"Mode ID: {section['mode_id']}\n")
        details.append(f"Detection Method: {section['source']}\n\n")
        
        # i-menu configuration
        details.append("i-menu Configuration:\n")
        imenu_offset = offset + 924
        for i in range(12):
            pos = imenu_offset + i * 4
            if pos < len(self.file_data):
                item_id = self.file_data[pos]
                if item_id == 0:
                    details.append(f"  Slot {i+1:2d}: (Empty)\n")
                elif item_id in self.imenu_names:
                    details.append(f"  Slot {i+1:2d}: {self.imenu_names[item_id]}\n")
                else:
                    details.append(f"  Slot {i+1:2d}: Unknown/Invalid ({item_id})\n")
        
        # File prefix
        prefix_offset = offset + 1540
        if prefix_offset + 10 < len(self.file_data):
            prefix_bytes = self.file_data[prefix_offset:prefix_offset+10]
            null_pos = prefix_bytes.find(0)
            if null_pos >= 0:
                prefix_bytes = prefix_bytes[:null_pos]
            try:
                prefix = prefix_bytes.decode('ascii')
                details.append(f"\nFile Prefix: '{prefix}'\n")
            except UnicodeDecodeError:
                details.append(f"\nFile Prefix: (invalid)\n")
        
        # Data density analysis
        section_data = self.file_data[offset:offset+6628]
        zero_count = section_data.count(0)
        data_density = (len(section_data) - zero_count) / len(section_data)
        details.append(f"\nData Density: {data_density:.2%}\n")
        details.append(f"Non-zero bytes: {len(section_data) - zero_count}\n")
        
        self.user_details_text.insert(tk.END, "".join(details))
        self.user_details_text.config(state=tk.DISABLED)
    
    def copy_user_settings(self):
        """Copy settings from one mode to current User Setting"""
        current_selection = self.mode_listbox.curselection()
        if not current_selection:
            messagebox.showwarning("Warning", "Please select a User Setting (U1, U2, or U3) first.")
            return
        
        current_section_name = self.mode_listbox.get(current_selection[0])
        current_section = self.config_sections[current_section_name]
        
        # Check if current selection is a User Setting
        if not any(current_section['mode_name'].startswith(u) for u in ["U1", "U2", "U3"]):
            messagebox.showwarning("Warning", "Please select a User Setting (U1, U2, or U3) as the target.")
            return
        
        source_name = self.copy_source_var.get()
        if not source_name or source_name not in self.config_sections:
            messagebox.showwarning("Warning", "Please select a source mode to copy from.")
            return
        
        # Confirm the operation
        result = messagebox.askyesno("Confirm Copy", 
                                   f"Copy all settings from '{source_name}' to '{current_section_name}'?\n\n"
                                   f"This will overwrite the current {current_section['mode_name']} configuration.")
        
        if result:
            try:
                source_section = self.config_sections[source_name]
                self.perform_settings_copy(source_section['offset'], current_section['offset'])
                
                # Refresh the display
                self.load_section_settings(current_section_name)
                self.modified = True
                self.update_title()
                
                messagebox.showinfo("Success", f"Settings copied from '{source_name}' to '{current_section_name}'")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy settings: {str(e)}")
    
    def reset_user_settings(self):
        """Reset User Setting to default values"""
        current_selection = self.mode_listbox.curselection()
        if not current_selection:
            messagebox.showwarning("Warning", "Please select a User Setting (U1, U2, or U3) first.")
            return
        
        current_section_name = self.mode_listbox.get(current_selection[0])
        current_section = self.config_sections[current_section_name]
        
        # Check if current selection is a User Setting
        if not any(current_section['mode_name'].startswith(u) for u in ["U1", "U2", "U3"]):
            messagebox.showwarning("Warning", "Please select a User Setting (U1, U2, or U3) to reset.")
            return
        
        # Confirm the operation
        result = messagebox.askyesno("Confirm Reset", 
                                   f"Reset '{current_section_name}' to default values?\n\n"
                                   f"This will clear all custom settings in {current_section['mode_name']}.")
        
        if result:
            try:
                self.perform_settings_reset(current_section['offset'])
                
                # Refresh the display
                self.load_section_settings(current_section_name)
                self.modified = True
                self.update_title()
                
                messagebox.showinfo("Success", f"'{current_section_name}' has been reset to default values")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {str(e)}")
    
    def perform_settings_copy(self, source_offset, target_offset):
        """Copy configuration data from source to target offset"""
        # Copy the entire configuration section (6628 bytes)
        source_data = self.file_data[source_offset:source_offset+6628]
        
        # Preserve the mode ID in the target (it should remain as U1/U2/U3)
        target_mode_id = self.file_data[target_offset + 1240]
        
        # Copy data
        for i, byte in enumerate(source_data):
            if target_offset + i < len(self.file_data):
                self.file_data[target_offset + i] = byte
        
        # Restore the target mode ID
        if target_offset + 1240 < len(self.file_data):
            self.file_data[target_offset + 1240] = target_mode_id
    
    def perform_settings_reset(self, target_offset):
        """Reset a User Setting to default values"""
        # Store the mode ID
        target_mode_id = self.file_data[target_offset + 1240]
        
        # Clear the entire section
        for i in range(6628):
            if target_offset + i < len(self.file_data):
                self.file_data[target_offset + i] = 0
        
        # Restore the mode ID
        if target_offset + 1240 < len(self.file_data):
            self.file_data[target_offset + 1240] = target_mode_id
        
        # Set default file prefix "DSC"
        prefix_offset = target_offset + 1540
        default_prefix = b"DSC"
        for i, byte in enumerate(default_prefix):
            if prefix_offset + i < len(self.file_data):
                self.file_data[prefix_offset + i] = byte
    
    def on_imenu_change(self, slot):
        """Handle i-menu slot change"""
        # Mark as modified
        self.modified = True
        self.update_title()
        
        # Apply change to file data
        self.apply_imenu_changes()
        
        # Update visual layout
        self.update_imenu_layout()
    
    def update_imenu_layout(self):
        """Update the visual i-menu layout representation"""
        if not hasattr(self, 'layout_labels'):
            return
        
        for i in range(12):
            value = self.imenu_vars[i].get()
            if value == "(Empty)":
                display_text = f"Pos {i+1}\n(Empty)"
                bg_color = "#f0f0f0"
            else:
                # Extract function name (remove ID part)
                function_name = value.split(' (')[0]
                # Truncate if too long
                if len(function_name) > 15:
                    function_name = function_name[:12] + "..."
                display_text = f"Pos {i+1}\n{function_name}"
                bg_color = "#e6f3ff"
            
            self.layout_labels[i].config(text=display_text, background=bg_color)
    
    def on_prefix_change(self, event):
        """Handle file prefix change"""
        self.modified = True
        self.update_title()
        self.apply_prefix_change()
    
    def apply_imenu_changes(self):
        """Apply i-menu changes to file data"""
        selection = self.mode_listbox.curselection()
        if not selection:
            return
        
        section_name = self.mode_listbox.get(selection[0])
        section = self.config_sections[section_name]
        offset = section['offset']
        imenu_offset = offset + 924
        
        for i in range(12):
            pos = imenu_offset + i * 4
            if pos < len(self.file_data):
                value = self.imenu_vars[i].get()
                if value == "(Empty)":
                    item_id = 0
                else:
                    # Extract ID from "Name (ID)" format
                    try:
                        item_id = int(value.split('(')[-1].split(')')[0])
                    except:
                        item_id = 0
                
                self.file_data[pos] = item_id
    
    def apply_prefix_change(self):
        """Apply file prefix change to file data"""
        selection = self.mode_listbox.curselection()
        if not selection:
            return
        
        section_name = self.mode_listbox.get(selection[0])
        section = self.config_sections[section_name]
        offset = section['offset']
        prefix_offset = offset + 1540
        
        prefix = self.prefix_var.get()[:10]  # Limit to 10 characters
        prefix_bytes = prefix.encode('ascii', errors='ignore')
        
        # Clear the prefix area
        for i in range(10):
            if prefix_offset + i < len(self.file_data):
                self.file_data[prefix_offset + i] = 0
        
        # Write new prefix
        for i, byte in enumerate(prefix_bytes):
            if prefix_offset + i < len(self.file_data):
                self.file_data[prefix_offset + i] = byte
    
    def update_title(self):
        """Update window title to show modification status"""
        title = "Nikon Z Camera Menu Editor"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
            if self.modified:
                title += " *"
        self.root.title(title)
    
    def enable_menus(self):
        """Enable menu items after file is loaded"""
        self.file_menu.entryconfig("Save", state="normal")
        self.file_menu.entryconfig("Save As...", state="normal") 
        self.file_menu.entryconfig("Export Settings...", state="normal")
        self.tools_menu.entryconfig("Analyze File Structure", state="normal")
        self.tools_menu.entryconfig("Backup Original", state="normal")
        self.tools_menu.entryconfig("Verify CRC", state="normal")
    
    def save_file(self):
        """Save changes to current file"""
        if self.current_file and self.modified:
            self.save_to_file(self.current_file)
    
    def save_as_file(self):
        """Save as new file"""
        if not self.file_data:
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Menu File As",
            defaultextension=".bin",
            filetypes=[
                ("Camera Menu Files", "*.bin"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            self.save_to_file(filename)
            self.current_file = filename
            self.file_label.config(text=os.path.basename(filename))
    
    def save_to_file(self, filename):
        """Save file data to specified filename"""
        try:
            # Update CRC before saving
            self.update_crc()
            
            with open(filename, "wb") as f:
                f.write(self.file_data)
            
            self.modified = False
            self.update_title()
            self.status_var.set(f"Saved: {os.path.basename(filename)}")
            messagebox.showinfo("Success", f"File saved successfully to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def update_crc(self):
        """Update CRC checksum at end of file"""
        if len(self.file_data) >= 2:
            # Calculate CRC-16 over all data except last 2 bytes
            crc_data = self.file_data[:-2]
            crc = self.calculate_crc16(crc_data)
            
            # Update CRC in file (big-endian)
            self.file_data[-2] = (crc >> 8) & 0xFF
            self.file_data[-1] = crc & 0xFF
    
    def calculate_crc16(self, data):
        """Calculate CRC-16 checksum (XMODEM variant)"""
        crc = 0
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return crc
    
    def export_settings(self):
        """Export settings to JSON file"""
        if not self.config_sections:
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[
                ("JSON Files", "*.json"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            try:
                settings = {}
                for section_name, section in self.config_sections.items():
                    settings[section_name] = self.extract_section_settings(section)
                
                with open(filename, "w") as f:
                    json.dump(settings, f, indent=2)
                
                messagebox.showinfo("Success", f"Settings exported to:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export settings: {str(e)}")
    
    def extract_section_settings(self, section):
        """Extract all settings from a configuration section"""
        offset = section['offset']
        settings = {
            'mode_name': section['mode_name'],
            'mode_id': section['mode_id'],
            'imenu': {},
            'file_prefix': ''
        }
        
        # Extract i-menu settings
        imenu_offset = offset + 924
        for i in range(12):
            pos = imenu_offset + i * 4
            if pos < len(self.file_data):
                item_id = self.file_data[pos]
                settings['imenu'][f'slot_{i+1}'] = {
                    'id': item_id,
                    'name': self.imenu_names.get(item_id, f"Unknown ({item_id})")
                }
        
        # Extract file prefix
        prefix_offset = offset + 1540
        if prefix_offset + 10 < len(self.file_data):
            prefix_bytes = self.file_data[prefix_offset:prefix_offset+10]
            null_pos = prefix_bytes.find(0)
            if null_pos >= 0:
                prefix_bytes = prefix_bytes[:null_pos]
            try:
                settings['file_prefix'] = prefix_bytes.decode('ascii')
            except UnicodeDecodeError:
                settings['file_prefix'] = ''
        
        return settings
    
    def import_settings(self):
        """Import settings from JSON file"""
        filename = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[
                ("JSON Files", "*.json"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, "r") as f:
                    settings = json.load(f)
                
                # TODO: Implement settings import
                messagebox.showinfo("Info", "Settings import functionality will be implemented in a future version.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import settings: {str(e)}")
    
    def analyze_structure(self):
        """Show file structure analysis"""
        if not self.file_data:
            return
        
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("File Structure Analysis")
        analysis_window.geometry("800x600")
        
        text_widget = tk.Text(analysis_window, wrap=tk.WORD, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(analysis_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Generate analysis
        analysis = self.generate_structure_analysis()
        text_widget.insert(tk.END, analysis)
        text_widget.config(state=tk.DISABLED)
    
    def generate_structure_analysis(self):
        """Generate detailed file structure analysis"""
        analysis = []
        analysis.append("=== Nikon Z Camera Menu File Structure Analysis ===\n")
        analysis.append(f"File: {os.path.basename(self.current_file) if self.current_file else 'Unknown'}\n")
        analysis.append(f"Size: {len(self.file_data)} bytes\n\n")
        
        # Camera info
        analysis.append("=== Camera Information ===\n")
        analysis.append(f"Model: {self.camera_label.cget('text')}\n")
        analysis.append(f"Firmware: {self.firmware_label.cget('text')}\n\n")
        
        # Configuration sections
        analysis.append("=== Configuration Sections ===\n")
        for section_name, section in self.config_sections.items():
            analysis.append(f"{section_name}:\n")
            analysis.append(f"  Offset: {section['offset']} (0x{section['offset']:x})\n")
            analysis.append(f"  Mode ID: {section['mode_id']}\n")
            analysis.append(f"  Detection: {section['source']}\n")
            analysis.append(f"  Quality Score: {self.score_config_section(section['offset']):.1f}\n\n")
        
        # Data density analysis
        analysis.append("=== Data Density Analysis ===\n")
        total_zeros = self.file_data.count(0)
        density = (len(self.file_data) - total_zeros) / len(self.file_data)
        analysis.append(f"Overall data density: {density:.2%}\n")
        analysis.append(f"Zero bytes: {total_zeros}\n")
        analysis.append(f"Non-zero bytes: {len(self.file_data) - total_zeros}\n\n")
        
        return "".join(analysis)
    
    def backup_file(self):
        """Create backup of original file"""
        if not self.current_file:
            return
        
        backup_file = self.current_file + ".backup"
        try:
            with open(self.current_file, "rb") as src, open(backup_file, "wb") as dst:
                dst.write(src.read())
            
            messagebox.showinfo("Success", f"Backup created:\n{backup_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {str(e)}")
    
    def verify_crc(self):
        """Verify CRC checksum"""
        if not self.file_data or len(self.file_data) < 2:
            return
        
        # Extract current CRC
        current_crc = struct.unpack('>H', self.file_data[-2:])[0]
        
        # Calculate expected CRC
        crc_data = self.file_data[:-2]
        expected_crc = self.calculate_crc16(crc_data)
        
        if current_crc == expected_crc:
            messagebox.showinfo("CRC Verification", f"CRC checksum is valid!\n\nCurrent: 0x{current_crc:04X}\nExpected: 0x{expected_crc:04X}")
        else:
            messagebox.showwarning("CRC Verification", f"CRC checksum mismatch!\n\nCurrent: 0x{current_crc:04X}\nExpected: 0x{expected_crc:04X}\n\nThe file may be corrupted or modified.")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Nikon Z Camera Menu Editor
Version 1.0

A visual tool for editing Nikon Z camera menu settings files.
Supports both Z5 Mark 1 and Mark 2 formats with auto-detection.

Features:
• Visual i-menu configuration
• File prefix editing  
• Automatic format detection
• CRC verification
• Settings export/import
• File structure analysis

Created for the nzconfigtools project."""
        
        messagebox.showinfo("About", about_text)

def main():
    root = tk.Tk()
    app = NikonZMenuEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
