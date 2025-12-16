# VENI VIDI VICI
# BY ROBERTO LIZZA

import csv
import os
import urllib.request
import requests
import urllib
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, SINGLE, MULTIPLE
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import security_check


# ------------------------------------------------------
# SECURITY CHECK
# ------------------------------------------------------

if not security_check.validate_license():
    raise SystemExit


# ------------------------------------------------------
# UI HELPERS
# ------------------------------------------------------

def pick_csv_file():
    """Open file dialog and return selected CSV path."""
    return filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )


def pick_save_folder():
    """Ask the user where to save downloaded images."""
    return filedialog.askdirectory(
        title="Choose folder to save downloaded images"
    )


def pick_column(columns):
    """
    UI window for selecting ONE column.
    Double‑click selects.
    """
    picker = tk.Toplevel()
    picker.title("Select Column")
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


def pick_multiple_columns(columns):
    """
    Multi-column picker.
    Double‑click to add a URL column.
    'DONE' to finish.
    """
    picker = tk.Toplevel()
    picker.title("Select URL Columns")
    picker.geometry("450x350")

    tk.Label(
        picker,
        text="Double‑click columns that contain image URLs"
    ).pack(pady=10)

    frame = tk.Frame(picker)
    frame.pack(fill="both", expand=True)

    # Left: all columns
    lb_all = Listbox(frame, selectmode=SINGLE)
    lb_all.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    for col in columns:
        lb_all.insert(tk.END, col)

    # Right: selected columns
    lb_selected = Listbox(frame)
    lb_selected.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    selected = []

    def on_double_click(event):
        idx = lb_all.curselection()
        if idx:
            col = columns[idx[0]]
            if col not in selected:
                selected.append(col)
                lb_selected.insert(tk.END, col)

    lb_all.bind("<Double-Button-1>", on_double_click)

    def done():
        picker.destroy()

    tk.Button(picker, text="DONE", command=done).pack(pady=10)

    picker.wait_window()
    return selected


# ------------------------------------------------------
# MAIN DOWNLOAD LOGIC
# ------------------------------------------------------

def download_images(csv_path, naming_column, url_columns, save_folder):
    """Process CSV and download images to selected folder."""
    os.makedirs(save_folder, exist_ok=True)

    with open(csv_path, newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            base_name = row.get(naming_column, "Image").strip()
            if not base_name:
                base_name = "Image"

            count = 1

            for col in url_columns:
                url = row.get(col, "").strip()
                if not url:
                    continue

                # Extract extension safely
                extension = "jpg"
                if "." in url:
                    ext = url.split(".")[-1].split("?")[0]
                    if 1 <= len(ext) <= 5:
                        extension = ext.lower()

                filename = f"{base_name}.{extension}"
                full_path = os.path.join(save_folder, filename)

                # Avoid overwriting duplicates
                while os.path.exists(full_path):
                    filename = f"{base_name}_{count}.{extension}"
                    full_path = os.path.join(save_folder, filename)
                    count += 1

                # Attempt download
                try:
                    urllib.request.urlretrieve(url, full_path)
                except Exception as e:
                    print(f"Failed to download {url}: {e}")

    messagebox.showinfo("Done", "Images downloaded successfully!")


# ------------------------------------------------------
# MAIN APPLICATION
# ------------------------------------------------------

def main():
    root = tk.Tk()
    root.withdraw()

    # Step 1 — Choose CSV
    csv_path = pick_csv_file()
    if not csv_path:
        return

    # Step 2 — Choose save folder (moved earlier)
    save_folder = pick_save_folder()
    if not save_folder:
        messagebox.showerror("Cancelled", "You must choose a save folder.")
        return

    # Step 3 — Read column headers
    with open(csv_path, newline='', encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=";")
        columns = next(reader)

    # Step 4 — Select naming column
    naming_column = pick_column(columns)
    if not naming_column:
        messagebox.showerror("Cancelled", "You must select a naming column.")
        return

    # Step 5 — Select MULTIPLE URL columns
    url_columns = pick_multiple_columns(columns)
    if not url_columns:
        messagebox.showerror("Cancelled", "You must select at least one URL column.")
        return

    # Step 6 — Download images
    download_images(csv_path, naming_column, url_columns, save_folder)


if __name__ == "__main__":
    main()
