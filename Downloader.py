import json
import requests
import os
from tqdm import tqdm  # For download progress visualization
from urllib.parse import urlparse

# Function to download a file with progress
def download_file(url, filename, save_directory):
    try:
        response = requests.get(url, stream=True)
        
        # Check if the response status is OK (200)
        if response.status_code == 200:
            file_path = os.path.join(save_directory, filename)
            total_size = int(response.headers.get('content-length', 0))  # Total size in bytes
            block_size = 1024  # Size of each chunk to download
            
            # Progress bar to visualize download
            with open(file_path, 'wb') as f, tqdm(
                desc=f"Downloading {filename}",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        bar.update(len(chunk))
            print(f"Completed: {filename}")
        else:
            print(f"Failed to download {filename}: Status {response.status_code}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

# Function to load JSON data
def load_json(json_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        # If the JSON file doesn't exist, create an empty structure
        data = {"files": []}
    return data

# Function to save JSON data
def save_json(json_file, data):
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

# Function to extract the filename from a URL
def get_filename_from_url(url):
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename:
        filename = "downloaded_file"  # Default name if URL doesn't contain a filename
    return filename

# Function to add new URL to the JSON
def add_url_to_json(json_file):
    data = load_json(json_file)
    
    # Get input from the user
    url = input("Enter the file URL to download: ")
    
    # If the user doesn't enter a URL, return None and skip the process
    if not url.strip():
        print("No URL entered. Skipping...")
        return None
    
    # Automatically generate filename from the URL
    filename = get_filename_from_url(url)
    
    # Add new entry to the JSON data
    new_entry = {"filename": filename, "url": url}
    data["files"].append(new_entry)
    
    # Save updated data back to the JSON file
    save_json(json_file, data)
    
    print(f"Added {filename} to the download list.")

    return new_entry

# Main function to batch download files
def batch_download(json_file, save_directory):
    # Ensure save directory exists
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    
    # Load the JSON file
    data = load_json(json_file)

    # Download the files
    for item in data["files"]:
        filename = item["filename"]
        url = item["url"]
        print(f"Starting download: {filename} from {url}")
        download_file(url, filename, save_directory)

if __name__ == "__main__":
    # Define the path to your JSON file and where to save the downloads
    json_file = 'files.json'  # Replace with your actual JSON file
    save_directory = 'downloads'  # Folder where files will be saved
    
    # Add a new URL to the JSON file
    new_entry = add_url_to_json(json_file)
    
    # Download all files listed in the JSON (including newly added ones, if any)
    batch_download(json_file, save_directory)