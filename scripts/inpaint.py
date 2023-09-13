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

def calculate_pixels_to_extend(time_to_extend, rate=102.4):
    return round(time_to_extend * rate)

def extend_spectrogram(image: Image.Image, time: int, side: str) -> Image.Image:
    """
    Extend the spectrogram by adding white space on the specified side.
    """
    pixels_to_extend = calculate_pixels_to_extend(time) # Converting time to pixels
    width, height = image.size
    new_width = width + pixels_to_extend  
    extended_image = Image.new('RGB', (new_width, height), 'white')
    
    if side == 'left':
        print("left")
        extended_image.paste(image, (pixels_to_extend, 0))
    elif side == 'right':
        extended_image.paste(image, (0, 0))
    
    return extended_image

def infill_spectrogram(left_image: Image.Image, right_image: Image.Image, time: int) -> Image.Image:
    pixels_to_infill = calculate_pixels_to_extend(time)  # Converting time to pixels

    width_left, height_left = left_image.size
    width_right, height_right = right_image.size
    
    if height_left != height_right:
        raise ValueError("The heights of the left and right spectrograms must be the same.")
    
    new_width = width_left + width_right + pixels_to_infill
    infilled_image = Image.new('RGB', (new_width, height_left), 'white')
    
    infilled_image.paste(left_image, (0, 0))
    infilled_image.paste(right_image, (width_left + pixels_to_infill, 0))
    
    return infilled_image

def run_inference_and_save_outputs(spectrogram_image: Image, prompt: str, alpha: float = 0.5, num_inference_steps: int = 50):
    noisy_spectrogram, mask_image = gaussian_paint(spectrogram_image)

    noisy_spectrogram_path_str = "seed_images/noisy_spectrogram.png"
    mask_image_path_str = "seed_images/mask.png"
    noisy_spectrogram.save(noisy_spectrogram_path_str)
    mask_image.save(mask_image_path_str)

    spectrogram_image_path = Path(noisy_spectrogram_path_str)
    mask_image_path = Path(mask_image_path_str)

    data = {
        "start": {
            "prompt": prompt,
            "seed": random.randint(1, 100),
            "denoising": 1,
        },
        "end": {
            "prompt": prompt,
            "seed": random.randint(1, 100),
            "denoising": 1,
        },
        "alpha": alpha,
        "num_inference_steps": num_inference_steps,
        "seed_image_id": spectrogram_image_path.stem,
        "mask_image_id": mask_image_path.stem
    }

    response = requests.post("http://127.0.0.1:3013/run_inference/", json=data)

    if response.status_code == 200:
        output = response.json()
        generated_audio = output['audio']
        generated_image = output['image']
        
        with open('outputs/generated2.mp3', 'wb') as audio_file:
            audio_file.write(base64.b64decode(generated_audio.split(',')[1]))
        
        with open('outputs/generated.jpg', 'wb') as image_file:
            image_file.write(base64.b64decode(generated_image.split(',')[1]))
        
        print("Generated extended audio and image saved successfully.")
    else:
        print(f"Error: {response.text}")

def riff_extend(prompt: str, path: str, time: str, side: str):
    time = int(time)
    segment = AudioSegment.from_file(path)
    params = SpectrogramParams()
    converter = SpectrogramImageConverter(params=params)
    spectrogram_image = converter.spectrogram_image_from_audio(segment)    
    extended_spectrogram = extend_spectrogram(spectrogram_image, time, side)
    extended_spectrogram.save(f"outputs/extended_spectrogram.png") # This holds the exteneded spectro gram
    run_inference_and_save_outputs(extended_spectrogram, prompt)

def riff_infill(prompt: str, left_audio: str, right_audio: str, time: str):
    time = int(time)
    # Load audio segments
    left_segment = AudioSegment.from_file(left_audio)
    right_segment = AudioSegment.from_file(right_audio)
    
    # Convert audio to spectrogram images
    params = SpectrogramParams()
    converter = SpectrogramImageConverter(params=params)
    
    left_spectrogram = converter.spectrogram_image_from_audio(left_segment)
    right_spectrogram = converter.spectrogram_image_from_audio(right_segment)
    
    # Create infilled spectrogram
    infilled_spectrogram = infill_spectrogram(left_spectrogram, right_spectrogram, time)
    
    # Save infilled spectrogram
    infilled_spectrogram.save(f"outputs/infilled_spectrogram.png") # This holds the infilled spectrogram
    
    # Run inference and save outputs
    run_inference_and_save_outputs(infilled_spectrogram, prompt)

riff_infill("piano","sample_audios/piano.mp3","sample_audios/piano.mp3", 1)

"""
Script to run these @Will

# prompt, left audio, right audio, time to infill
riff_infill("piano","sample_audios/piano.mp3","sample_audios/piano.mp3", 1)

# prompt, audio path, time to extend, side of audio to extend on
riff_extend("piano", "sample_audios/piano.mp3", 1, "right")
"""