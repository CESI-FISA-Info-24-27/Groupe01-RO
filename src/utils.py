import os
import re
from PIL import Image
import shutil

def create_gif_from_png_folder(png_folder, output_gif, duration=200):
    """
    Create a GIF with all PNG files in a specified folder.
    
    Args:
        png_folder (str): Path to the folder containing files
        output_gif (str): Path for the output GIF file
        duration (int): Duration for each image (milliseconds)
    """

    if not os.path.exists(png_folder):
        raise FileNotFoundError(f"Folder {png_folder} doesn't exist.")
    
    png_files = []
    for file in os.listdir(png_folder):
        if file.endswith(".png") and file.startswith("result_graph_"):
            png_files.append(file)
    
    if not png_files:
        raise ValueError("No such file found named 'result_graph_X.png'.")
    
    # Sort files by number (result_graph_0, result_graph_1, etc.)
    png_files.sort(key=lambda x: int(re.search(r'result_graph_(\d+)\.png', x).group(1)))
    
    # Open images
    images = []
    for png_file in png_files:
        png_path = os.path.join(png_folder, png_file)
        images.append(Image.open(png_path))
    
    # Save GIF
    images[0].save(
        output_gif,
        save_all=True,
        append_images=images[1:],
        optimize=False,
        duration=duration,
        loop=0
    )
    
    print(f"GIF created at: {output_gif}")



def clear_folder(folder_path):
    """
    Delete all the content of a folder.
    
    Args:
        folder_path (str): Path of the folder to delete
    """
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} doesn't exist.")
        return
    
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)