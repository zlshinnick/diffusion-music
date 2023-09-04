import numpy as np
from pydub import AudioSegment
from PIL import Image
import requests
from pathlib import Path
import base64
import os

from riffusion.spectrogram_converter import SpectrogramConverter
from riffusion.spectrogram_params import SpectrogramParams
from riffusion.spectrogram_image_converter import SpectrogramImageConverter
from riffusion.util import image_util

def generate_with_input_audio(prompt: str, random: str, path: str):
    # Load audio file
    audio_path = path
    segment = AudioSegment.from_file(audio_path)

    # Creation of audio to spectrogram Converter
    params = SpectrogramParams()
    converter = SpectrogramImageConverter(params=params)

    # Convert audio to spectrogram
    spectrogram_image = converter.spectrogram_image_from_audio(segment)

    # Save the spectrogram image for use with the RiffusionPredictor server
    spectrogram_image_path_str = "seed_images/spectrogram.png"
    spectrogram_image.save(spectrogram_image_path_str)

    # Convert the string path to a pathlib.Path object for JSON
    spectrogram_image_path = Path(spectrogram_image_path_str)

    data = {
        "start": {
            "prompt": prompt,
            "seed": 42,
            "denoising": random,
        },
        "end": {
            "prompt": prompt,
            "seed": 43,
            "denoising": random,
        },
        "alpha": 0.5,
        "num_inference_steps": 50,
        "seed_image_id": spectrogram_image_path.stem
    }

    response = requests.post("http://127.0.0.1:3013/run_inference/", json=data)
    handle_response(response)

def generate_without_input_audio(prompt: str, random: str):
    data = {
        "start": {
            "prompt": prompt,
            "seed": 42,
            "denoising": float(random),
        },
        "end": {
            "prompt": prompt,
            "seed": 43,
            "denoising": float(random),
        },
        "alpha": 0.5,
        "num_inference_steps": 3,
    }

    response = requests.post("http://127.0.0.1:3013/run_inference/", json=data)
    newTrackPath = handle_response(response, with_image=False)

    return newTrackPath

def handle_response(response, with_image=True):
    if response.status_code == 200:
        output = response.json()
        generated_audio = output['audio']

        # Save generated audio in correct location
        newTrackPath = os.getcwd() + "/outputs/generated_clip.mp3"
        with open(newTrackPath, 'wb') as audio_file:
            audio_file.write(base64.b64decode(generated_audio.split(',')[1]))

        return newTrackPath
    
    else:
        print(f"Error: {response.text}")
        return "error"
