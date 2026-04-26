import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
import pyttsx3
import threading

class AudioBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Book Generator")
        self.root.geometry("450x280")
        
        self.pdf_path = ""
        
        # UI Elements
        self.lbl_title = tk.Label(root, text="PDF to Audio Book Generator", font=("Helvetica", 16, "bold"))
        self.lbl_title.pack(pady=15)
        
        self.btn_select = tk.Button(root, text="Select PDF File", command=self.select_pdf, width=25, font=("Helvetica", 10))
        self.btn_select.pack(pady=10)
        
        self.lbl_file = tk.Label(root, text="No file selected", fg="gray", font=("Helvetica", 9))
        self.lbl_file.pack(pady=5)
        
        self.btn_convert = tk.Button(root, text="Generate Audio", command=self.convert_to_audio, width=25, font=("Helvetica", 10), state=tk.DISABLED)
        self.btn_convert.pack(pady=10)
        
        self.lbl_status = tk.Label(root, text="", font=("Helvetica", 9))
        self.lbl_status.pack(pady=5)
        
    def select_pdf(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf")]
        )
        if file_path:
            self.pdf_path = file_path
            # Show the end of the path if it's too long
            display_path = "..." + file_path[-40:] if len(file_path) > 40 else file_path
            self.lbl_file.config(text=display_path)
            self.btn_convert.config(state=tk.NORMAL)
            self.lbl_status.config(text="")
            
    def convert_to_audio(self):
        if not self.pdf_path:
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 Files", "*.mp3")],
            title="Save Audio As"
        )
        
        if not save_path:
            return
            
        self.btn_convert.config(state=tk.DISABLED)
        self.btn_select.config(state=tk.DISABLED)
        self.lbl_status.config(text="Extracting text and generating audio... Please wait.", fg="blue")
        
        # Run conversion in a separate thread so UI doesn't freeze
        threading.Thread(target=self.process_pdf, args=(self.pdf_path, save_path), daemon=True).start()
        
    def process_pdf(self, pdf_path, save_path):
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + " "
                        
            if not text.strip():
                self.root.after(0, self.show_error, "Could not extract any text from the PDF. It might be scanned or image-based.")
                return
                
            engine = pyttsx3.init()
            # Optional: adjusting speech rate
            rate = engine.getProperty('rate')
            engine.setProperty('rate', max(100, rate - 25)) # Slightly slower for better comprehension
            
            engine.save_to_file(text, save_path)
            engine.runAndWait()
            
            self.root.after(0, self.show_success, f"Audio saved successfully to:\n{save_path}")
            
        except Exception as e:
            self.root.after(0, self.show_error, f"An error occurred: {str(e)}")
            
    def show_success(self, message):
        self.lbl_status.config(text="Audio generated successfully!", fg="green")
        messagebox.showinfo("Success", message)
        self.btn_convert.config(state=tk.NORMAL)
        self.btn_select.config(state=tk.NORMAL)
        
    def show_error(self, message):
        self.lbl_status.config(text="An error occurred.", fg="red")
        messagebox.showerror("Error", message)
        self.btn_convert.config(state=tk.NORMAL)
        self.btn_select.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioBookApp(root)
    root.mainloop()
