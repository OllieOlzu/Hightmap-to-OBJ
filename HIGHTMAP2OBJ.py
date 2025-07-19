import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

class HeightmapConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Heightmap to OBJ Converter")
        
        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.scale_value = tk.DoubleVar(value=1.0)
        self.max_height = tk.DoubleVar(value=1.0)
        self.status_text = tk.StringVar(value="Ready")
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Input File Selection
        ttk.Label(self.root, text="Input Heightmap:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="Browse...", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)
        
        # Output File Selection
        ttk.Label(self.root, text="Output OBJ File:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.output_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="Browse...", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Parameters
        ttk.Label(self.root, text="Scale:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Scale(self.root, from_=0.1, to=10, variable=self.scale_value, orient="horizontal").grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.root, textvariable=self.scale_value).grid(row=2, column=2, padx=5, pady=5)
        
        ttk.Label(self.root, text="Max Height:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Scale(self.root, from_=0.1, to=10, variable=self.max_height, orient="horizontal").grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.root, textvariable=self.max_height).grid(row=3, column=2, padx=5, pady=5)
        
        # Convert Button
        ttk.Button(self.root, text="Convert to OBJ", command=self.convert).grid(row=4, column=1, pady=10)
        
        # Status/Output
        ttk.Label(self.root, text="Status:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(self.root, textvariable=self.status_text).grid(row=5, column=1, padx=5, pady=5, sticky="w")
        
        # Output Text
        self.output_text = tk.Text(self.root, height=10, width=60, state="disabled")
        self.output_text.grid(row=6, column=0, columnspan=3, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.root, command=self.output_text.yview)
        scrollbar.grid(row=6, column=3, sticky="ns")
        self.output_text.config(yscrollcommand=scrollbar.set)
        
    def browse_input(self):
        filetypes = (
            ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"),
            ("All files", "*.*")
        )
        filename = filedialog.askopenfilename(title="Select Heightmap Image", filetypes=filetypes)
        if filename:
            self.input_path.set(filename)
            # Suggest output filename
            base = os.path.splitext(filename)[0]
            self.output_path.set(f"{base}.obj")
            self.update_status(f"Selected: {os.path.basename(filename)}")
    
    def browse_output(self):
        filetypes = (("OBJ files", "*.obj"), ("All files", "*.*"))
        filename = filedialog.asksaveasfilename(
            title="Save OBJ File",
            defaultextension=".obj",
            filetypes=filetypes,
            initialfile=os.path.basename(self.output_path.get())
        )
        if filename:
            self.output_path.set(filename)
    
    def update_status(self, message):
        self.status_text.set(message)
        self.append_output(message + "\n")
        self.root.update_idletasks()
    
    def append_output(self, text):
        self.output_text.config(state="normal")
        self.output_text.insert("end", text)
        self.output_text.see("end")
        self.output_text.config(state="disabled")
    
    def convert(self):
        input_path = self.input_path.get()
        output_path = self.output_path.get()
        scale = self.scale_value.get()
        max_height = self.max_height.get()
        
        if not input_path:
            messagebox.showerror("Error", "Please select an input heightmap image")
            return
        
        if not output_path:
            messagebox.showerror("Error", "Please specify an output OBJ file")
            return
        
        try:
            self.update_status("Starting conversion...")
            
            # Load the image and convert to grayscale
            self.update_status(f"Loading image: {input_path}")
            img = Image.open(input_path).convert('L')
            width, height = img.size
            pixels = np.array(img).astype(np.float32)
            
            self.update_status(f"Image dimensions: {width}x{height} pixels")
            
            # Normalize pixel values to 0-1 range (black=0, white=1)
            pixels = pixels / 255.0
            
            # Scale the height values
            pixels = pixels * max_height
            
            with open(output_path, 'w') as obj_file:
                # Write OBJ header
                obj_file.write("# Heightmap to OBJ\n")
                obj_file.write(f"# Original image: {input_path}\n")
                obj_file.write(f"# Dimensions: {width}x{height}\n")
                obj_file.write(f"# Scale: {scale}\n")
                obj_file.write(f"# Max height: {max_height}\n\n")
                
                self.update_status("Writing vertices...")
                
                # Write vertices
                for y in range(height):
                    for x in range(width):
                        # Calculate vertex position
                        x_pos = (x - width/2) * scale
                        y_pos = pixels[y, x] * scale
                        z_pos = (y - height/2) * scale
                        obj_file.write(f"v {x_pos:.4f} {y_pos:.4f} {z_pos:.4f}\n")
                
                self.update_status("Writing faces...")
                
                # Write faces (quads)
                for y in range(height - 1):
                    for x in range(width - 1):
                        # Calculate vertex indices
                        v1 = y * width + x + 1
                        v2 = y * width + x + 2
                        v3 = (y + 1) * width + x + 2
                        v4 = (y + 1) * width + x + 1
                        
                        # Write face (quad)
                        obj_file.write(f"f {v1} {v2} {v3} {v4}\n")
                
                success_message = (f"Conversion complete!\n"
                                 f"Vertices: {width*height}\n"
                                 f"Faces: {(width-1)*(height-1)}\n"
                                 f"Saved to: {output_path}")
                
                self.update_status(success_message)
                messagebox.showinfo("Success", success_message)
                
        except Exception as e:
            error_message = f"Error during conversion: {str(e)}"
            self.update_status(error_message)
            messagebox.showerror("Error", error_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = HeightmapConverterApp(root)
    root.mainloop()
