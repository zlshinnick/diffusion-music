import numpy as np
from pydub import AudioSegment
from PIL import Image
import os
from pathlib import Path
import requests
import json
import base64

from riffusion.spectrogram_converter import SpectrogramConverter
from riffusion.spectrogram_params import SpectrogramParams
from riffusion.spectrogram_image_converter import SpectrogramImageConverter
from riffusion.util import image_util

# blend two columns using linear interpolation.
def blend_columns(col1, col2, alpha):
    """
    creates a new column which is a blend of col1 and col . Alpha ranges from 0-1 and controlls how much each column influences

    creates a smooth transition from left to right segments
    """
    return (1 - alpha) * col1 + alpha * col2

def mirror_infill_image(image: Image.Image, fade_width: int = 50, mix_ratio: float = 0.5, blend_width: int = 20) -> (Image.Image, Image.Image):
    """
    Fill the gap in the spectrogram by mirroring the content from both left and right sides 
    and create a mask with a gradient. Additionally, blends the mirrored sections to create smooth flow transition.
    """

    # convert image to grayscale
    grayscale_image = image.convert('L')

    # grayscale image to numpy array
    image_np = np.array(grayscale_image)

    # mask with the same shape as the image and initialize with zeros
    mask_np = np.zeros_like(image_np)

    start_col = None
    end_col = None

    # find cols with all white for start and end postions of infill
    for col in range(10, image_np.shape[1]):
        if np.all(image_np[:, col] > 225):
            start_col = col if start_col is None else start_col 
            end_col = col
    gap_width = end_col - start_col + 1

    # calculate portions of infill from left and right
    left_width = int(gap_width * mix_ratio) # mix ratio is decided by user if they want more influence from left or right segments (0.0 is all right, 1.0 is all left)
    right_width = gap_width - left_width

    # fill from the left
    if left_width > 0:
        mirrored_content_left = image_np[:, start_col-left_width:start_col][:, ::-1]
        image_np[:, start_col:start_col+left_width] = mirrored_content_left

    # fill from the right
    if right_width > 0:
        mirrored_content_right = image_np[:, end_col+1:end_col+1+right_width][:, ::-1]
        image_np[:, end_col+1-right_width:end_col+1] = mirrored_content_right

    # blending connecting parts 
    for col_offset in range(blend_width):
        alpha = col_offset / blend_width
        blended_col = blend_columns(                
            image_np[:, start_col + left_width - blend_width + col_offset],
            image_np[:, end_col - right_width + col_offset + 1],
            alpha
        )
        image_np[:, start_col + left_width - blend_width + col_offset] = blended_col

    # update mask 
    fade_array_left = np.linspace(0, 255, fade_width).astype(np.uint8) 
    fade_array_right = np.linspace(255, 0, fade_width).astype(np.uint8)  
    mask_np[:, start_col-fade_width:start_col] = fade_array_left
    mask_np[:, end_col+1:end_col+fade_width+1] = fade_array_right
    mask_np[:, start_col:end_col+1] = 255

    # infilled spectrogram + corresponding mask
    return Image.fromarray(image_np, mode='L'), Image.fromarray(mask_np, mode='L')



audio_path = "edm_for_infill.mp3"
segment = AudioSegment.from_file(audio_path)

params = SpectrogramParams()
converter = SpectrogramImageConverter(params=params)

spectrogram_image = converter.spectrogram_image_from_audio(segment)
print(spectrogram_image.size)

noisy_spectrogram, mask_image = mirror_infill_image(spectrogram_image)


noisy_spectrogram_path_str = "seed_images/noisy_spectrogram.png"
mask_image_path_str = "seed_images/mask.png"
noisy_spectrogram.save(noisy_spectrogram_path_str)
mask_image.save(mask_image_path_str)

spectrogram_image_path = Path(noisy_spectrogram_path_str)
mask_image_path = Path(mask_image_path_str)

data = {
    "start": {
        "prompt": "electric dance music",
        "seed": 50,
        "denoising": 0.75,
    },
    "end": {
        "prompt": "electric dance music",
        "seed": 43,
        "denoising": 0.75,
    },
    "alpha": 0.5,
    "num_inference_steps": 50,
    "seed_image_id": spectrogram_image_path.stem,
    "mask_image_id": mask_image_path.stem
}

response = requests.post("http://127.0.0.1:3013/run_inference/", json=data)

if response.status_code == 200:
    output = response.json()
    generated_audio = output['audio']
    generated_image = output['image']
    
    with open('generated_audio_extended.mp3', 'wb') as audio_file:
        audio_file.write(base64.b64decode(generated_audio.split(',')[1]))
    
    with open('generated_image_extended.jpg', 'wb') as image_file:
        image_file.write(base64.b64decode(generated_image.split(',')[1]))
    
    print("Generated extended audio and image saved successfully.")
else:
    print(f"Error: {response.text}")