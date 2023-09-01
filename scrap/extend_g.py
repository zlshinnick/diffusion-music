import numpy as np
from pydub import AudioSegment
from PIL import Image
import os
from pathlib import Path
import requests
import json
import base64
import torch
import torchvision
import torchvision.transforms as transforms

from riffusion.spectrogram_converter import SpectrogramConverter
from riffusion.spectrogram_params import SpectrogramParams
from riffusion.spectrogram_image_converter import SpectrogramImageConverter
from riffusion.util import image_util



def noise_fill_image(image: Image.Image) -> (Image.Image, Image.Image):
    """
    Extend the spectrogram by filling in white regions with Gaussian noise and create a mask.
    """

    # Convert image to grayscale
    grayscale_image = image.convert('L')

    # Convert grayscale image to numpy array
    image_np = np.array(grayscale_image)

    # Create a mask with the same shape as the image and initialize with zeros
    mask_np = np.zeros_like(image_np)

    # Find the column where all pixels are white
    for col in range(20, image_np.shape[1]):
        if np.all(image_np[:, col] == 255):
            
            # Update the mask for the original white pixels
            mask_np[:, col:] = 255

            # Fill the white areas with Gaussian noise
            noise = np.random.normal(loc=128, scale=30, size=(image_np.shape[0], image_np.shape[1] - col)).astype(np.uint8)
            image_np[:, col:] = np.clip(noise, 0, 255)
            break  # Exit the loop once we find the first all-white column

    return Image.fromarray(image_np, mode='L'), Image.fromarray(mask_np, mode='L')

audio_path = "trial.mp3"
segment = AudioSegment.from_file(audio_path)

params = SpectrogramParams()
converter = SpectrogramImageConverter(params=params)

spectrogram_image = converter.spectrogram_image_from_audio(segment)

noisy_spectrogram, mask_image = noise_fill_image(spectrogram_image)


noisy_spectrogram_path_str = "seed_images/noisy_spectrogram.png"
mask_image_path_str = "seed_images/mask.png"
noisy_spectrogram.save(noisy_spectrogram_path_str)
mask_image.save(mask_image_path_str)

# Convert the string paths to pathlib.Path objects
spectrogram_image_path = Path(noisy_spectrogram_path_str)
mask_image_path = Path(mask_image_path_str)


data = {
    "start": {
        "prompt": "guitar",
        "seed": 69,
        "denoising": 1,
    },
    "end": {
        "prompt": "guitar",
        "seed": 35,
        "denoising": 1,
    },
    "alpha": 0.5,
    "num_inference_steps": 50,
    "seed_image_id": spectrogram_image_path.stem,
    "mask_image_id": mask_image_path.stem
}

# Send a POST request to the server
response = requests.post("http://127.0.0.1:3013/run_inference/", json=data)

# Parse the response
if response.status_code == 200:
    output = response.json()
    generated_audio = output['audio']
    generated_image = output['image']
    
    # Save generated audio to a file
    with open('generated_audio_extended.mp3', 'wb') as audio_file:
        audio_file.write(base64.b64decode(generated_audio.split(',')[1]))
    
    # Save generated image to a file
    with open('generated_image_extended.jpg', 'wb') as image_file:
        image_file.write(base64.b64decode(generated_image.split(',')[1]))
    
    print("Generated extended audio and image saved successfully.")
else:
    print(f"Error: {response.text}")