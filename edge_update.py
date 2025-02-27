import os
import re
import requests
import zipfile
from io import BytesIO
import subprocess

# Paths
driver_path = r'driver\edgedriver_win32\msedgedriver.exe'
driver_dir = os.path.dirname(driver_path)

# Function to get the installed Edge browser version
# def get_installed_edge_version():
#     try:
#         # Command to get Edge version
#         result = subprocess.run(
#             [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', '--version'],
#             capture_output=True,
#             text=True,
#             check=True
#         )
#         version = result.stdout.strip().split()[-1]
#         return version
#     except Exception as e:
#         print(f"Error retrieving Edge version: {e}")
#         return None

# Function to get the latest stable WebDriver version
def get_latest_stable_driver_version():
    try:
        # Use Microsoft's official Edge Driver download page
        edge_driver_versions = 'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/'
        
        # Alternative direct URL method
        response = requests.get(
            'https://msedgedriver.azureedge.net/LATEST_STABLE', 
            timeout=10,
            verify=True
        )
        response.raise_for_status()
        return response.text.strip()
    
    except requests.RequestException as e:
        print(f"Error fetching latest stable driver version: {e}")
        
        # Fallback to manual version matching
        try:
            # Extract major version from installed Edge
            installed_version = 'x'
            if installed_version:
                major_version = installed_version.split('.')[0]
                return f"{major_version}.0.2903.87"  # Use a known stable version pattern
        
        except Exception as fallback_error:
            print(f"Fallback method failed: {fallback_error}")
        
        return None

# Function to download and extract the WebDriver
def download_and_extract_driver(version, extract_to):
    try:
        # Primary download URL
        download_url = f'https://msedgedriver.azureedge.net/{version}/edgedriver_win32.zip'
        
        # Alternative download URLs
        alternate_urls = [
            f'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/{version}/edgedriver_win32.zip',
            f'https://github.com/microsoft/edge-webdriver/releases/download/v{version}/edgedriver_win32.zip'
        ]
        
        # Try primary URL first
        response = requests.get(download_url)
        response.raise_for_status()
        
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            z.extractall(extract_to)
        print(f"WebDriver version {version} downloaded and extracted to {extract_to}")
    
    except requests.RequestException as e:
        print(f"Primary download failed: {e}")
        
        # Try alternate URLs
        for alt_url in alternate_urls:
            try:
                response = requests.get(alt_url)
                response.raise_for_status()
                
                with zipfile.ZipFile(BytesIO(response.content)) as z:
                    z.extractall(extract_to)
                print(f"WebDriver downloaded from alternate URL: {alt_url}")
                return
            except Exception as alt_error:
                print(f"Alternate URL {alt_url} failed: {alt_error}")
        
        print("All download attempts failed.")

# Main logic
if __name__ == "__main__":
    # Ensure driver directory exists
    os.makedirs(driver_dir, exist_ok=True)

    # Get installed Edge version
    # installed_edge_version = get_installed_edge_version()
    # if not installed_edge_version:
    #     print("Unable to determine installed Edge version.")
    #     exit(1)

    # Get latest stable WebDriver version
    latest_driver_version = '133.0.3065.69'
    if not latest_driver_version:
        print("Unable to determine latest stable WebDriver version.")
        exit(1)

    # Check if WebDriver needs to be updated
    if os.path.exists(driver_path):
        # Get current WebDriver version
        result = subprocess.run([driver_path, '--version'], capture_output=True, text=True)
        current_driver_version = re.search(r'\d+\.\d+\.\d+\.\d+', result.stdout)
        if current_driver_version:
            current_driver_version = current_driver_version.group(0)
            if current_driver_version == latest_driver_version:
                print(f"WebDriver is up to date (version {current_driver_version}).")
                exit(0)
            else:
                print(f"Updating WebDriver from version {current_driver_version} to {latest_driver_version}.")
        else:
            print("Unable to determine current WebDriver version. Proceeding with download.")
    else:
        print("WebDriver not found. Downloading the latest version.")

    # Download and extract the latest WebDriver
    download_and_extract_driver(latest_driver_version, driver_dir)