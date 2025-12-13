import csv
import os
import urllib.request
from security_check import security_check

# Ensure security passes first
if not security_check():
    print("Security check failed. Exiting.")
    exit()

print("Security check passed. Starting downloader...\n")

# ------------------------- CONFIGURABLE VALUES -------------------------

CSV_FILE = "input.csv"            # The CSV file the user will provide
OUTPUT_FOLDER = "Downloaded"      # Folder where images are stored

# Names of possible image columns
IMAGE_COLUMNS = ["Imagen", "Imagen_2", "Image", "Image_2"]

# ----------------------------------------------------------------------


def ensure_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def sanitize_filename(name):
    """Basic cleaner to avoid invalid file characters."""
    invalid = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid:
        name = name.replace(char, "_")
    return name.strip()


def download_image(url, path):
    try:
        urllib.request.urlretrieve(url, path)
        return True
    except Exception as e:
        print(f"   [ERROR] Failed: {url}")
        print(f"           {e}")
        return False


def main():
    ensure_folder(OUTPUT_FOLDER)

    # 1. Load CSV and ask user which column defines the filenames
    with open(CSV_FILE, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames

        print("Available columns:")
        for i, col in enumerate(header, start=1):
            print(f"{i}. {col}")

        choice = input("\nEnter the number of the column to name the images: ")
        choice = int(choice) - 1
        name_column = header[choice]

        print(f"\nNaming images based on column: {name_column}\n")

        # 2. Loop rows
        for row_index, row in enumerate(reader, start=2):
            base_name = sanitize_filename(row[name_column])

            image_links = []
            for col in IMAGE_COLUMNS:
                if col in row and row[col].strip():
                    image_links.append(row[col].strip())

            if not image_links:
                print(f"[Row {row_index}] No image URLs found.")
                continue

            # 3. Download each image
            for idx, url in enumerate(image_links, start=1):
                ext = url.split(".")[-1].lower()
                if ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
                    ext = "jpg"

                name = base_name if idx == 1 else f"{base_name}_{idx}"
                filename = f"{name}.{ext}"
                filepath = os.path.join(OUTPUT_FOLDER, filename)

                print(f"[Row {row_index}] Downloading {url} → {filename}")
                download_image(url, filepath)

    print("\nDone!")


if __name__ == "__main__":
    main()
