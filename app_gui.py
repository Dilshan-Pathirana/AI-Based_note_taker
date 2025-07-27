import os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import subprocess
import platform

from image_utils import extract_text_preserve_all  # Your OCR extraction function
from refiner import refine_notes_with_ai           # Your updated sync chunked AI refiner
from pdf_generator import generate_pdf_from_markdown


class NoteTakerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI-Based Note Taker")
        self.geometry("620x350")

        self.images_path = tk.StringVar()
        self.output_path = tk.StringVar()

        tk.Label(self, text="Images Folder:").pack(anchor="w", padx=10, pady=(10, 0))
        frame_img = tk.Frame(self)
        frame_img.pack(fill="x", padx=10)
        tk.Entry(frame_img, textvariable=self.images_path).pack(side="left", fill="x", expand=True)
        tk.Button(frame_img, text="Browse", command=self.browse_images).pack(side="left", padx=5)

        tk.Label(self, text="Output Folder:").pack(anchor="w", padx=10, pady=(10, 0))
        frame_out = tk.Frame(self)
        frame_out.pack(fill="x", padx=10)
        tk.Entry(frame_out, textvariable=self.output_path).pack(side="left", fill="x", expand=True)
        tk.Button(frame_out, text="Browse", command=self.browse_output).pack(side="left", padx=5)

        self.status_label = tk.Label(self, text="Idle", fg="blue", justify="left")
        self.status_label.pack(pady=10)

        frame_buttons = tk.Frame(self)
        frame_buttons.pack(pady=10)

        self.scan_btn = tk.Button(frame_buttons, text="Scan Images", command=self.scan_images)
        self.scan_btn.pack(side="left", padx=5)

        self.generate_ai_btn = tk.Button(frame_buttons, text="Generate PDF (AI)", command=self.generate_pdf_ai, state="disabled")
        self.generate_ai_btn.pack(side="left", padx=5)

        self.generate_no_ai_btn = tk.Button(frame_buttons, text="Generate PDF (No AI)", command=self.generate_pdf_no_ai, state="disabled")
        self.generate_no_ai_btn.pack(side="left", padx=5)

        self.open_output_btn = tk.Button(frame_buttons, text="Open Output Folder", command=self.open_output_folder, state="disabled")
        self.open_output_btn.pack(side="left", padx=5)

        self.raw_text = None
        self.refined_text = None

    def browse_images(self):
        folder = filedialog.askdirectory()
        if folder:
            self.images_path.set(folder)

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)

    def scan_images(self):
        if not self.images_path.get():
            messagebox.showerror("Error", "Please select images folder")
            return
        self.status_label.config(text="Scanning images, please wait...", fg="orange")
        self.scan_btn.config(state="disabled")
        self.generate_ai_btn.config(state="disabled")
        self.generate_no_ai_btn.config(state="disabled")
        self.open_output_btn.config(state="disabled")

        def worker():
            try:
                lines = extract_text_preserve_all(self.images_path.get())
                self.raw_text = "\n".join(lines)
                self.status_label.config(text=f"Scan complete. {len(lines)} lines extracted.", fg="green")
                self.generate_ai_btn.config(state="normal")
                self.generate_no_ai_btn.config(state="normal")
            except Exception as e:
                self.status_label.config(text=f"Error during scan: {e}", fg="red")
            finally:
                self.scan_btn.config(state="normal")

        threading.Thread(target=worker, daemon=True).start()

    def generate_pdf_ai(self):
        if not self.raw_text:
            messagebox.showerror("Error", "No scanned text available. Please scan images first.")
            return
        if not self.output_path.get():
            messagebox.showerror("Error", "Please select output folder")
            return

        self.status_label.config(text="Refining notes using AI, please wait...", fg="orange")
        self.generate_ai_btn.config(state="disabled")
        self.generate_no_ai_btn.config(state="disabled")
        self.scan_btn.config(state="disabled")
        self.open_output_btn.config(state="disabled")

        def worker():
            try:
                self.refined_text = refine_notes_with_ai(self.raw_text)

                output_path = self.output_path.get()
                ocr_pdf_path = os.path.join(output_path, "ocr_notes.pdf")
                ai_pdf_path = os.path.join(output_path, "ai_notes.pdf")

                generate_pdf_from_markdown(self.raw_text, ocr_pdf_path)
                generate_pdf_from_markdown(self.refined_text, ai_pdf_path)

                self.status_label.config(text=f"PDFs saved:\n{ocr_pdf_path}\n{ai_pdf_path}", fg="green")
                self.open_output_btn.config(state="normal")
            except Exception as e:
                self.status_label.config(text=f"Error during AI PDF generation: {e}", fg="red")
            finally:
                self.generate_ai_btn.config(state="normal")
                self.generate_no_ai_btn.config(state="normal")
                self.scan_btn.config(state="normal")

        threading.Thread(target=worker, daemon=True).start()

    def generate_pdf_no_ai(self):
        if not self.raw_text:
            messagebox.showerror("Error", "No scanned text available. Please scan images first.")
            return
        if not self.output_path.get():
            messagebox.showerror("Error", "Please select output folder")
            return

        self.status_label.config(text="Generating PDF without AI, please wait...", fg="orange")
        self.generate_ai_btn.config(state="disabled")
        self.generate_no_ai_btn.config(state="disabled")
        self.scan_btn.config(state="disabled")
        self.open_output_btn.config(state="disabled")

        def worker():
            try:
                output_path = self.output_path.get()
                ocr_pdf_path = os.path.join(output_path, "ocr_notes.pdf")

                generate_pdf_from_markdown(self.raw_text, ocr_pdf_path)

                self.status_label.config(text=f"PDF saved without AI:\n{ocr_pdf_path}", fg="green")
                self.open_output_btn.config(state="normal")
            except Exception as e:
                self.status_label.config(text=f"Error during PDF generation: {e}", fg="red")
            finally:
                self.generate_ai_btn.config(state="normal")
                self.generate_no_ai_btn.config(state="normal")
                self.scan_btn.config(state="normal")

        threading.Thread(target=worker, daemon=True).start()

    def open_output_folder(self):
        path = self.output_path.get()
        if not path or not os.path.isdir(path):
            messagebox.showerror("Error", "Output folder path is invalid or not set.")
            return

        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", path])
            else:  # Linux and others
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {e}")


if __name__ == "__main__":
    app = NoteTakerApp()
    app.mainloop()
