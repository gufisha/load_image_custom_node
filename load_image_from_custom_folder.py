import os
# from PIL import Image # This line should be removed or commented if not used
from PIL import Image, ImageOps
import numpy as np
import torch
from nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
# from comfy.utils import load_image # This will be replaced

class LoadImageFromCustomFolder:
    DEFAULT_FOLDER_PATH = "./input/custom"  # Configurable default folder path

    @classmethod
    def INPUT_TYPES(cls):
        initial_image_files = ["<Error initializing. Check console.>"] 
        try:
            # INPUT_TYPES_GENERATOR will use cls.DEFAULT_FOLDER_PATH
            # and handles cases like folder not found or no images.
            generated_outputs = cls.INPUT_TYPES_GENERATOR() 
            
            image_file_tuple = generated_outputs.get("image_file")
            if image_file_tuple and \
               isinstance(image_file_tuple, tuple) and \
               len(image_file_tuple) > 0 and \
               isinstance(image_file_tuple[0], list):
                initial_image_files = image_file_tuple[0]
                # If the generator somehow returns an actual empty list, provide a fallback.
                # Normally, it should return like ["<no images found>"].
                if not initial_image_files:
                    initial_image_files = ["<No files from generator>"]
            else:
                initial_image_files = ["<Generator structure error>"]
        except Exception as e:
            print(f"[LoadImageFromCustomFolder] Error during initial INPUT_TYPES: {e}")
            # initial_image_files already has a default error message.

        return {
            "required": {
                # "folder_path": ("STRING", {"default": default_folder_path}), # Removed
                "image_file": (initial_image_files, ), # Defines image_file as a dropdown
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE_PREVIEW") # Added IMAGE_PREVIEW
    RETURN_NAMES = ("image", "preview")      # Added preview
    FUNCTION = "load_selected_image"
    CATEGORY = "image/load"

    def load_selected_image(self, image_file): # Removed folder_path
        # folder_path = folder_path.strip() # Removed

        if not os.path.isdir(self.DEFAULT_FOLDER_PATH): # Use constant
            raise Exception(f"Folder does not exist: {self.DEFAULT_FOLDER_PATH}")

        image_path = os.path.join(self.DEFAULT_FOLDER_PATH, image_file) # Use constant
        if not os.path.isfile(image_path):
            raise Exception(f"Image not found: {image_path}")

        pil_image_original = Image.open(image_path)
        
        # For tensor processing
        img_for_tensor = ImageOps.exif_transpose(pil_image_original.copy())
        img_rgb = img_for_tensor.convert("RGB")
        img_array = np.array(img_rgb).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(img_array)[None,]

        # For preview, use the original (after exif transpose)
        preview_image = ImageOps.exif_transpose(pil_image_original)

        return (image_tensor, [preview_image]) # Return tensor and list of PIL images for preview

    @classmethod
    def IS_CHANGED(cls, image_file, **kwargs): # Removed folder_path, added **kwargs
        """Force UI to refresh options when folder changes.""" # Comment might be slightly outdated
        return float("nan")

    @classmethod
    def VALIDATE_INPUTS(cls, image_file, **kwargs): # Removed folder_path, added **kwargs
        if not os.path.isdir(cls.DEFAULT_FOLDER_PATH): # Use constant
            return f"Folder does not exist: {cls.DEFAULT_FOLDER_PATH}"
        full_path = os.path.join(cls.DEFAULT_FOLDER_PATH, image_file) # Use constant
        if not os.path.isfile(full_path):
            return f"Image not found: {image_file} in {cls.DEFAULT_FOLDER_PATH}"
        return True

    @classmethod
    def INPUT_TYPES_GENERATOR(cls, **kwargs): # Removed inputs, added **kwargs
        folder_path = cls.DEFAULT_FOLDER_PATH # Use constant
        try:
            if not os.path.isdir(folder_path): # Check added for clarity, though listdir would fail too
                return {"image_file": ([f"<Folder not found: {folder_path}>"],)}
            files = os.listdir(folder_path)
            image_files = sorted([f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]) # Added webp and sorted
            return {
                "image_file": (image_files if image_files else ["<no images found>"],)
            }
        except Exception as e:
            print(f"[LoadImageFromCustomFolder] Error in INPUT_TYPES_GENERATOR: {e}")
            return {
                "image_file": (["<Error listing files. Check console.>"],)
            }

NODE_CLASS_MAPPINGS["LoadImageFromCustomFolder"] = LoadImageFromCustomFolder
NODE_DISPLAY_NAME_MAPPINGS["LoadImageFromCustomFolder"] = "📂 Load Image from Folder"