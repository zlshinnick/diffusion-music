import numpy as np
from pydub import AudioSegment
from PIL import Image
import requests
from pathlib import Path
import base64

from riffusion.spectrogram_converter import SpectrogramConverter
from riffusion.spectrogram_params import SpectrogramParams
from riffusion.spectrogram_image_converter import SpectrogramImageConverter
from riffusion.util import image_util

def generate_with_input_audio():
    # Load audio file
    audio_path = "tril.mp3"
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
            "prompt": "minimal emotional atmospheric synth techno beat jungle drum bass beat drop",
            "seed": 42,
            "denoising": 0.75,
        },
        "end": {
            "prompt": "minimal emotional atmospheric synth techno beat jungle drum bass beat drop",
            "seed": 43,
            "denoising": 0.75,
        },
        "alpha": 0.5,
        "num_inference_steps": 50,
        "seed_image_id": spectrogram_image_path.stem
    }

    response = requests.post("http://127.0.0.1:3013/run_inference/", json=data)
    
    handle_response(response)

def generate_without_input_audio():
    data = {
        "start": {
            "prompt": "minimal emotional atmospheric synth techno beat jungle drum bass beat drop",
            "seed": 42,
            "denoising": 0.75,
        },
        "end": {
            "prompt": "minimal emotional atmospheric synth techno beat jungle drum bass beat drop",
            "seed": 43,
            "denoising": 0.75,
        },
        "alpha": 0.5,
        "num_inference_steps": 50,
    }

    response = requests.post("http://127.0.0.1:3013/run_inference/", json=data)
    
    handle_response(response, with_image=False)

def handle_response(response, with_image=True):
    if response.status_code == 200:
        output = response.json()
        generated_audio = output['audio']
        
        # Save generated audio
        with open('generated.mp3', 'wb') as audio_file:
            audio_file.write(base64.b64decode(generated_audio.split(',')[1]))


        print("Generation completed successfully.")
    else:
        print(f"Error: {response.text}")

generate_without_input_audio()