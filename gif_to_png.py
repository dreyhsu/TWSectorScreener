import os
from pathlib import Path
from PIL import Image

def find_gif_files(folder_path):
    """
    Find all GIF files in the specified folder and its subfolders
    
    Args:
        folder_path (str): Path to the folder to search
        
    Returns:
        list: List of paths to GIF files
    """
    gif_files = []
    
    # Convert to Path object for easier handling
    folder = Path(folder_path)
    
    # Find all .gif files (case insensitive)
    for gif_path in folder.rglob('*.gif'):
        gif_files.append(str(gif_path))
    for gif_path in folder.rglob('*.GIF'):
        gif_files.append(str(gif_path))
        
    return sorted(set(gif_files))  # Remove duplicates and sort

def convert_gif_to_png(gif_path, delete_original=False):
    """
    Convert a GIF file to PNG
    
    Args:
        gif_path (str): Path to the GIF file
        delete_original (bool): Whether to delete the original GIF file
        
    Returns:
        str: Path to the created PNG file, or None if conversion failed
    """
    try:
        # Open the GIF file
        with Image.open(gif_path) as img:
            # Create output path by replacing .gif extension with .png
            output_path = str(Path(gif_path).with_suffix('.png'))
            
            # Convert and save as PNG
            img.convert('RGBA').save(output_path, 'PNG')
            
            # Delete original if requested
            if delete_original:
                os.remove(gif_path)
                
            return output_path
            
    except Exception as e:
        print(f"Error converting {gif_path}: {e}")
        return None

def batch_convert_gifs(folder_path, delete_originals=False):
    """
    Convert all GIF files in a folder to PNG
    
    Args:
        folder_path (str): Path to the folder containing GIF files
        delete_originals (bool): Whether to delete original GIF files after conversion
        
    Returns:
        tuple: (successful conversions count, failed conversions count)
    """
    # Find all GIF files
    gif_files = find_gif_files(folder_path)
    
    if not gif_files:
        print(f"No GIF files found in {folder_path}")
        return 0, 0
    
    print(f"Found {len(gif_files)} GIF files")
    
    # Convert each file
    successful = 0
    failed = 0
    
    for gif_path in gif_files:
        print(f"Converting: {gif_path}")
        png_path = convert_gif_to_png(gif_path, delete_originals)
        
        if png_path:
            successful += 1
            print(f"Successfully converted to: {png_path}")
        else:
            failed += 1
            print(f"Failed to convert: {gif_path}")
            
    return successful, failed

def gif2png():
    # Get folder path from user
    folder_path = 'C:/Users/User/Documents/Python Scripts/TWSectorScreener/fig'
    
    # Get delete option from user
    delete_originals = 'y'
    
    print("\nStarting conversion...")
    successful, failed = batch_convert_gifs(folder_path, delete_originals)
    
    # Print summary
    print("\nConversion Summary:")
    print(f"Successfully converted: {successful}")
    print(f"Failed conversions: {failed}")
    print(f"Total files processed: {successful + failed}")

if __name__ == '__main__':
    gif2png()