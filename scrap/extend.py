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
def mirror_extend_image(image: Image.Image, fade_width: int = 50) -> (Image.Image, Image.Image):
    """
    Extend the spectrogram by mirroring the existing content and create a mask with a gradient.
    """

    # convert image to grayscale
    grayscale_image = image.convert('L')

    # convert grayscale image to numpy array
    image_np = np.array(grayscale_image)

    # create a mask with the same shape as the image and initialize with zeros
    mask_np = np.zeros_like(image_np)

    # find the column where all pixels are white (needs the image has a grayscale format)
    for col in range(image_np.shape[1]):
        if np.all(image_np[:, col] == 255):
            
            # create a gradient that fades from 0 to 255
            fade_array = np.linspace(0, 255, fade_width).astype(np.uint8)
            
            # set the gradient on the mask
            mask_np[:, col:col+fade_width] = fade_array
            
            # update the mask after the gradient to white so still effected by diffusion
            mask_np[:, col+fade_width:] = 255

            # starting from this column, copy the mirrored content
            num_cols_to_mirror = image_np.shape[1] - col
            mirrored_content = image_np[:, col-num_cols_to_mirror:col][:, ::-1]  # flip 
            image_np[:, col:] = mirrored_content
            break  
            # mirrored image + mask w gradient
    return Image.fromarray(image_np, mode='L'), Image.fromarray(mask_np, mode='L')

audio_path = "trial.mp3"
segment = AudioSegment.from_file(audio_path)

params = SpectrogramParams()
converter = SpectrogramImageConverter(params=params)

spectrogram_image = converter.spectrogram_image_from_audio(segment)

noisy_spectrogram, mask_image = mirror_extend_image(spectrogram_image)


noisy_spectrogram_path_str = "seed_images/noisy_spectrogram.png"
mask_image_path_str = "seed_images/mask.png"
noisy_spectrogram.save(noisy_spectrogram_path_str)
mask_image.save(mask_image_path_str)

# Convert the string paths to pathlib.Path objects
spectrogram_image_path = Path(noisy_spectrogram_path_str)
mask_image_path = Path(mask_image_path_str)


data = {
    "start": {
        "prompt": "upbeat electronic dance music",
        "seed": 42,
        "denoising": 0.75,
    },
    "end": {
        "prompt": "upbeat electronic dance music",
        "seed": 43,
        "denoising": 0.75,
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