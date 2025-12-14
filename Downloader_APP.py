# VENI VIDI VICI
# BY ROBERTO LIZZA

import csv
import os
import urllib.request
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, SINGLE

import security_check

if not security_check.validate_license():
    raise SystemExit

# ---------------------------
# UI HELPERS
# ---------------------------

def pick_csv_file():
    """Open file dialog and return selected CSV path."""
    path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )
    return path

def pick_column(columns):
    """Show a UI window listing column names. Double‑click selects."""
    picker = tk.Toplevel()
    picker.title("Select Column for Image Naming")
    picker.geometry("350x300")

    tk.Label(picker, text="Double‑click a column:").pack(pady=10)

    lb = Listbox(picker, selectmode=SINGLE)
    lb.pack(fill="both", expand=True, padx=10, pady=10)

    for col in columns:
        lb.insert(tk.END, col)

    selection = {"value": None}

    def on_double_click(event):
        idx = lb.curselection()
        if idx:
            selection["value"] = columns[idx[0]]
            picker.destroy()

    lb.bind("<Double-Button-1>", on_double_click)

    picker.wait_window()
    return selection["value"]

# ---------------------------
# MAIN DOWNLOAD LOGIC
# ---------------------------

def download_images(csv_path, naming_column, url_columns):
    """Process CSV and download images."""
    save_folder = os.path.join(os.path.dirname(csv_path), "downloaded_images")
    os.makedirs(save_folder, exist_ok=True)

    with open(csv_path, newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            base_name = row.get(naming_column, "Image")

            count = 1
            for col in url_columns:
                url = row.get(col, "").strip()
                if not url:
                    continue

                extension = url.split(".")[-1][:5]
                filename = f"{base_name}.{extension}"

                # If duplicate images exist: Marca_2, Marca_3...
                if os.path.exists(os.path.join(save_folder, filename)):
                    filename = f"{base_name}_{count}.{extension}"
                count += 1

                filepath = os.path.join(save_folder, filename)

                try:
                    urllib.request.urlretrieve(url, filepath)
                except Exception as e:
                    print(f"Failed to download {url}: {e}")

    messagebox.showinfo("Done", "Images downloaded successfully!")

# ---------------------------
# MAIN UI APPLICATION
# ---------------------------

def main():
    # Security check first
    if not security_check.validate_license():
        messagebox.showerror("Security Error", "Security validation failed.")
        return

    root = tk.Tk()
    root.withdraw()  # Hide main Tkinter window

    # Step 1 — Choose CSV
    csv_path = pick_csv_file()
    if not csv_path:
        return

    # Read columns
    with open(csv_path, newline='', encoding="utf-8") as file:
        reader = csv.reader(file)
        columns = next(reader)

    # Step 2 — Pick naming column
    naming_column = pick_column(columns)
    if not naming_column:
        messagebox.showerror("Cancelled", "No column selected.")
        return

    # Step 3 — Pick columns containing image URLs
    url_column = pick_column(columns)
    if not url_column:
        messagebox.showerror("Cancelled", "No URL column selected.")
        return

    download_images(csv_path, naming_column, [url_column])


if __name__ == "__main__":
    main()

