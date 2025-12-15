# VENI VIDI VICI
# BY ROBERTO LIZZA

import csv
import os
import requests
import urllib
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, SINGLE, MULTIPLE
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import security_check

# ---------------------------
# SECURITY CHECK
# ---------------------------

if not security_check.validate_license():
    messagebox.showerror("Security Error", "Your license is invalid.")
    raise SystemExit


# ---------------------------
# UI HELPERS
# ---------------------------

def pick_csv_file():
    """Open file dialog and return selected CSV path."""
    return filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )


def pick_column(columns, title="Select Column"):
    """Show a UI window listing column names. Returns ONE."""
    picker = tk.Toplevel()
    picker.title(title)
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
    """Allows selecting multiple URL columns."""
    picker = tk.Toplevel()
    picker.title("Select URL Columns")
    picker.geometry("350x350")

    tk.Label(picker, text="Select ALL columns that contain image URLs:").pack(pady=10)

    lb = Listbox(picker, selectmode=MULTIPLE)
    lb.pack(fill="both", expand=True, padx=10, pady=10)

    for col in columns:
        lb.insert(tk.END, col)

    result = {"cols": None}

    def on_confirm():
        idxs = lb.curselection()
        result["cols"] = [columns[i] for i in idxs]
        picker.destroy()

    tk.Button(picker, text="Confirm", command=on_confirm).pack(pady=10)

    picker.wait_window()
    return result["cols"]


# ---------------------------
# DOWNLOAD LOGIC
# ---------------------------

def is_probably_url(text):
    """Very basic URL validation."""
    return text.startswith("http://") or text.startswith("https://")


def download_images(csv_path, naming_column, url_columns):
    save_folder = os.path.join(os.path.dirname(csv_path), "downloaded_images")
    os.makedirs(save_folder, exist_ok=True)

    with open(csv_path, newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=';')

        for row in reader:
            base_name = row.get(naming_column, "Image").strip()
            counter = 1

            for col in url_columns:
                url = row.get(col, "").strip()

                if not url or not is_probably_url(url):
                    print(f"Skipping invalid url in '{col}': {url}")
                    continue

                extension = url.split(".")[-1][:5]
                filename = f"{base_name}.{extension}"

                # Handle duplicates: Brand_2.jpg, Brand_3.jpg...
                while os.path.exists(os.path.join(save_folder, filename)):
                    filename = f"{base_name}_{counter}.{extension}"
                    counter += 1

                filepath = os.path.join(save_folder, filename)

                try:
                    urllib.request.urlretrieve(url, filepath)
                    import requests

                    r = requests.get(url, timeout=20)
                    with open(filepath, "wb") as f:
                        f.write(r.content)
                except Exception as e:
                    print(f"Failed to download {url}: {e}")

    messagebox.showinfo("Done", "Images downloaded successfully!")


# ---------------------------
# MAIN APPLICATION
# ---------------------------

def main():
    root = tk.Tk()
    root.withdraw()

    # Step 1: Pick CSV file
    csv_path = pick_csv_file()
    if not csv_path:
        return

    # Read columns (semicolon-separated)
    with open(csv_path, newline='', encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=';')
        columns = next(reader)

    # Step 2: Select column for image naming
    naming_column = pick_column(columns, "Select Naming Column")
    if not naming_column:
        messagebox.showerror("Error", "No naming column selected.")
        return

    # Step 3: Select one or multiple image URL columns
    url_columns = pick_multiple_columns(columns)
    if not url_columns:
        messagebox.showerror("Error", "No URL columns selected.")
        return

    download_images(csv_path, naming_column, url_columns)


if __name__ == "__main__":
    main()
