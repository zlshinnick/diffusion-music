import numpy as np
from pydub import AudioSegment
from PIL import Image
import requests
from pathlib import Path
import base64
import os
import random

from riffusion.spectrogram_converter import SpectrogramConverter
from riffusion.spectrogram_params import SpectrogramParams
from riffusion.spectrogram_image_converter import SpectrogramImageConverter
from riffusion.util import image_util

def generate_with_input_audio(prompt: str, randomness: str, path: str):
    # Load audio file
    segment = AudioSegment.from_file(path)

    # Creation of audio to spectrogram Converter
    params = SpectrogramParams()
    converter = SpectrogramImageConverter(params=params)

    # Convert audio to spectrogram
    spectrogram_image = converter.spectrogram_image_from_audio(segment)

    # Save the spectrogram image for use with the RiffusionPredictor server
    #!!! have to manually set path to seed image
    spectrogram_image_path_str = "/Users/willsaliba/Documents/Topics/diffusion-music/seed_images/spectrogram.png"
    spectrogram_image.save(spectrogram_image_path_str)

    # Convert the string path to a pathlib.Path object for JSON
    spectrogram_image_path = Path(spectrogram_image_path_str)

    data = {
        "start": {
            "prompt": prompt,
            "seed": random.randint(1, 100),
            "denoising": float(randomness),
        },
        "end": {
            "prompt": prompt,
            "seed": random.randint(1, 100),
            "denoising": float(randomness),
        },
        "alpha": 0.5, # Latent space interpolation of start image and end image
        "num_inference_steps": 50, # number of steps in diffusion process
        "seed_image_id": spectrogram_image_path.stem
    }

    response = requests.post("http://127.0.0.1:3013/run_inference/", json=data)
    newTrackPath = handle_response(response)
    return newTrackPath

def generate_without_input_audio(prompt: str, randomness: str):
    data = {
        "start": {
            "prompt": prompt,
            "seed": random.randint(1, 100),
            "denoising": float(randomness),
        },
        "end": {
            "prompt": prompt,
            "seed": random.randint(1, 100),
            "denoising": float(randomness),
        },
        "alpha": 0.5,
        "num_inference_steps": 1,
    }

    response = requests.post("http://127.0.0.1:3013/run_inference/", json=data)
    newTrackPath = handle_response(response, with_image=False)

    return newTrackPath

def handle_response(response, with_image=True):
    if response.status_code == 200:
        output = response.json()
        generated_audio = output['audio']

        #!!! have to manually set filepath for output track
        newTrackPath = "/Users/willsaliba/Documents/Topics/diffusion-music/outputs/generated_clip.mp3"
        with open(newTrackPath, 'wb') as audio_file:
            audio_file.write(base64.b64decode(generated_audio.split(',')[1]))

        return "SUCCESS"
    
    else:
        print(f"Error: {response.text}")
        return "error"
