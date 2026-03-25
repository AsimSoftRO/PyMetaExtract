import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PIL import Image
from PIL.ExifTags import TAGS
from PyPDF2 import PdfReader

RED = "\033[31m"
GREEN= "\033[92m"
BLACK = "\033[0m"

def extract_image_metadata(file_path, report=None):
    print(f"\n[+] Analyzing image: {file_path}")
    try:
        image = Image.open(file_path)
        info = image.getexif()
        if not info:
            print(f"{RED}[-] No EXIF metadata found.{BLACK}")
            if report is not None:
                report[file_path] = "No EXIF metadata found."
            return
        meta_data = {}
        for tag_id, value in info.items():
            tag = TAGS.get(tag_id, tag_id)
            print(f"{GREEN} {tag}\{BLACK}: {value}")
            meta_data[tag] = value
        if report is not None:
            report[file_path] = meta_data
    except Exception as e:
        print(f"\{RED}[-] Error opening image{BLACK}: {e}")
        if report is not None:
            report[file_path] = f"Error: {e}"

def extract_pdf_metadata(file_path, report=None):
    print(f"\n[+] Analyzing PDF: {file_path}")
    try:
        reader = PdfReader(file_path)
        meta = reader.metadata
        if meta:
            meta_data = {}
            for key, value in meta.items():
                print(f" {GREEN}{key} {BLACK}: {value}")
                meta_data[key] = value
            if report is not None:
                report[file_path] = meta_data
        else:
            print("[-] No metadata found in PDF.\033[0m")
            if report is not None:
                report[file_path] = "No metadata found in PDF."
    except Exception as e:
        print(f"[-] Error opening PDF: {e}")
        if report is not None:
            report[file_path] = f"Error: {e}"

def scan_webpage_for_files(url):
    print(f"\n[+] Scanning URL: {url}")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        files = []
        for tag in soup.find_all(['a', 'img']):
            file_url = tag.get('href') or tag.get('src')
            if file_url:
                file_url = urljoin(url, file_url)
                if file_url.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif')):
                    files.append(file_url)
        return files
    except Exception as e:
        print(f"[-] Error scanning URL: {e}")
        return []

def download_file(file_url):
    local_filename = os.path.basename(urlparse(file_url).path)
    try:
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_filename
    except Exception as e:
        print(f"{RED}[-] Error downloading{BLACK} {file_url}: {e}")
        return None

def analyze_webpage(url):
    files = scan_webpage_for_files(url)
    if not files:
        print("[-] No images or PDFs found on the webpage.")
        return
    
    report = {}
    for file_url in files:
        print(f"\n[+] Processing file: {file_url}")
        local_file = download_file(file_url)
        if local_file:
            if local_file.lower().endswith('.pdf'):
                extract_pdf_metadata(local_file, report)
            else:
                extract_image_metadata(local_file, report)
            os.remove(local_file)
    print("\n=== Webpage Analysis Report ===")


def main_menu():
    while True:
        print("\n=== PyMetaExtract ===")
        print("1. Analyze an Image")
        print("2. Analyze a PDF")
        print("3. Analyze a Webpage for Images and PDFs")
        print("4. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            file_path = input("Enter the path to the image: ").strip()
            if os.path.isfile(file_path):
                extract_image_metadata(file_path)
            else:
                print("[-] File does not exist!")
        elif choice == "2":
            file_path = input("Enter the path to the PDF: ").strip()
            if os.path.isfile(file_path):
                extract_pdf_metadata(file_path)
            else:
                print("[-] File does not exist!")
        elif choice == "3":
            url = input("Enter the URL of the webpage: ").strip()
            analyze_webpage(url)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("[-] Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()