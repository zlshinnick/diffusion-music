import numpy as np
from pydub import AudioSegment
from PIL import Image
import os
from pathlib import Path
import requests
import json
import base64
import random

from riffusion.spectrogram_converter import SpectrogramConverter
from riffusion.spectrogram_params import SpectrogramParams
from riffusion.spectrogram_image_converter import SpectrogramImageConverter
from riffusion.util import image_util

import numpy as np
from PIL import Image

def gaussian_paint(image: Image.Image, fade_width: int = 50) -> (Image.Image, Image.Image):
    """
    Fill all the gaps in the spectrogram with Gaussian noise and create a mask.
    """

    # Convert image to grayscale
    grayscale_image = image.convert('L')

    # Convert grayscale image to numpy array
    image_np = np.array(grayscale_image)

    # Create a mask with the same shape as the image and initialize with zeros
    mask_np = np.zeros_like(image_np)

    start_col = None
    end_col = None

    for col in range(0, image_np.shape[1]):
        is_gap = np.all(image_np[:, col] > 225)

        if is_gap:
            start_col = col if start_col is None else start_col
            end_col = col
        else:
            # Check if we just exited a gap
            if start_col is not None:
                gap_width = end_col - start_col + 1

                # Generate Gaussian noise to fill the gap
                noise = np.random.normal(loc=128, scale=30, size=(image_np.shape[0], gap_width)).astype(np.uint8)
                image_np[:, start_col:end_col+1] = np.clip(noise, 0, 255)

                # Update mask with boundary check
                fade_start_left = max(0, start_col - fade_width)
                fade_end_right = min(image_np.shape[1], end_col + fade_width + 1)

                fade_array_left = np.linspace(0, 255, start_col - fade_start_left).astype(np.uint8)
                fade_array_right = np.linspace(255, 0, fade_end_right - end_col - 1).astype(np.uint8)

                mask_np[:, fade_start_left:start_col] = fade_array_left
                mask_np[:, end_col + 1:fade_end_right] = fade_array_right
                mask_np[:, start_col:end_col+1] = 255

                # Reset start and end columns
                start_col = None
                end_col = None

    # Check if the last gap extended to the end of the image
    if start_col is not None:
        gap_width = end_col - start_col + 1
        noise = np.random.normal(loc=128, scale=30, size=(image_np.shape[0], gap_width)).astype(np.uint8)
        image_np[:, start_col:end_col+1] = np.clip(noise, 0, 255)

        fade_start_left = max(0, start_col - fade_width)
        fade_array_left = np.linspace(0, 255, start_col - fade_start_left).astype(np.uint8)
        
        mask_np[:, fade_start_left:start_col] = fade_array_left
        mask_np[:, start_col:end_col+1] = 255

    return Image.fromarray(image_np, mode='L'), Image.fromarray(mask_np, mode='L')

audio_path = "sample_audios/piano_for_extend.mp3"
segment = AudioSegment.from_file(audio_path)

params = SpectrogramParams()
converter = SpectrogramImageConverter(params=params)

spectrogram_image = converter.spectrogram_image_from_audio(segment)
print(spectrogram_image.size)

noisy_spectrogram, mask_image = gaussian_paint(spectrogram_image)


noisy_spectrogram_path_str = "outputs/noisy_spectrogram.png"
mask_image_path_str = "outputs/mask.png"
noisy_spectrogram.save(noisy_spectrogram_path_str)
mask_image.save(mask_image_path_str)

spectrogram_image_path = Path(noisy_spectrogram_path_str)
mask_image_path = Path(mask_image_path_str)

data = {
    "start": {
        "prompt": "upbeat classical piano",
        "seed": random.randint(1, 100),
        "denoising": 1,
    },
    "end": {
        "prompt": "upbeat classical piano",
        "seed": random.randint(1, 100),
        "denoising": 1,
    },
    "alpha": 0.5,
    "num_inference_steps": 100,
    "seed_image_id": spectrogram_image_path.stem,
    "mask_image_id": mask_image_path.stem
}

response = requests.post("http://127.0.0.1:3013/run_inference/", json=data)

if response.status_code == 200:
    output = response.json()
    generated_audio = output['audio']
    generated_image = output['image']
    
    with open('outputs/generated.mp3', 'wb') as audio_file:
        audio_file.write(base64.b64decode(generated_audio.split(',')[1]))
    
    with open('outputs/generated.jpg', 'wb') as image_file:
        image_file.write(base64.b64decode(generated_image.split(',')[1]))
    
    print("Generated extended audio and image saved successfully.")
else:
    print(f"Error: {response.text}")