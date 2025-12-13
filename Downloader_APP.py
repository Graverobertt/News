# VENI VIDI VICI
# BY ROBERTO LIZZA

import csv
import urllib.request
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from security_check import security_check

# ----------------------
# GUI HELPERS
# ----------------------

def choose_csv_gui():
    """Opens a dialog to choose a CSV file. Returns path or None."""
    root = tk.Tk()
    root.withdraw()  # hide empty root window

    file_path = filedialog.askopenfilename(
        title="Select your CSV file",
        filetypes=[("CSV Files", "*.csv")]
    )

    root.destroy()
    return file_path if file_path else None


def choose_column_gui(headers):
    """
    Displays a list of headers. User double-clicks one.
    Returns selected header or None.
    """
    selected = {"value": None}

    def on_double_click(event):
        w = event.widget
        index = w.curselection()
        if index:
            selected["value"] = w.get(index)
            top.destroy()

    top = tk.Tk()
    top.title("Select Naming Column")

    label = tk.Label(top, text="Double-click the column to name your images:")
    label.pack(pady=5)

    listbox = tk.Listbox(top, width=40, height=10)
    listbox.pack(padx=10, pady=10)

    for h in headers:
        listbox.insert(tk.END, h)

    listbox.bind("<Double-Button-1>", on_double_click)

    top.mainloop()

    return selected["value"]


# ----------------------
# DOWNLOADER LOGIC
# ----------------------

def download_images(csv_path, naming_column):
    output_folder = "Downloaded_Images"
    os.makedirs(output_folder, exist_ok=True)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        image_columns = [h for h in headers if h.lower().startswith("imagen")]

        if not image_columns:
            messagebox.showerror("Error", "No columns named Imagen or Imagen_2 found.")
            return

        count = 0
        failures = []

        for row in reader:
            base_name = row[naming_column].strip().replace(" ", "_")

            for i, img_col in enumerate(image_columns, start=1):
                url = row.get(img_col, "").strip()

                if not url or not url.startswith("http"):
                    failures.append(f"{base_name} → No valid URL in column {img_col}")
                    continue

                # filename example: Marca.jpg or Marca_2.jpg
                suffix = "" if i == 1 else f"_{i}"
                ext = os.path.splitext(url)[1]
                if ext.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
                    ext = ".jpg"

                filename = f"{base_name}{suffix}{ext}"
                filepath = os.path.join(output_folder, filename)

                try:
                    urllib.request.urlretrieve(url, filepath)
                    count += 1
                except Exception as e:
                    failures.append(f"{base_name} ({img_col}) → Download failed: {e}")

        # Show result summary
        msg = f"Downloaded: {count}\nFailed: {len(failures)}"
        if failures:
            msg += "\n\nFailures:\n" + "\n".join(failures)

        messagebox.showinfo("Download Complete", msg)


# ----------------------
# MAIN APP LOGIC
# ----------------------

def main():
    # Run security first
    if not security_check():
        messagebox.showerror("Security Check", "Security validation failed. Exiting.")
        return

    # Step 1 — Select CSV
    csv_file = choose_csv_gui()
    if not csv_file:
        messagebox.showwarning("Cancelled", "No CSV selected.")
        return

    # Step 2 — Read headers
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

    if not headers:
        messagebox.showerror("Error", "CSV file has no headers.")
        return

    # Step 3 — GUI header picker
    naming_column = choose_column_gui(headers)
    if not naming_column:
        messagebox.showwarning("Cancelled", "No column selected.")
        return

    # Step 4 — Download images
    download_images(csv_file, naming_column)


if __name__ == "__main__":
    main()
