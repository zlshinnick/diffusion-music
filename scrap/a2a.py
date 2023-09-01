import numpy as np
from pydub import AudioSegment
from PIL import Image
import requests
import os
from pathlib import Path
import requests
import json
import base64

from riffusion.spectrogram_converter import SpectrogramConverter
from riffusion.spectrogram_params import SpectrogramParams
from riffusion.spectrogram_image_converter import SpectrogramImageConverter
from riffusion.util import image_util

# load audio file
audio_path = "trial.mp3"  
segment = AudioSegment.from_file(audio_path)

# creation of audio to spectogram Converter
params = SpectrogramParams()
converter = SpectrogramImageConverter(params=params)

# convert audio to spectrogram
spectrogram_image = converter.spectrogram_image_from_audio(segment)

# save the spectrogram image for use with the RiffusionPredictor server
spectrogram_image_path_str = "seed_images/spectrogram.png"
spectrogram_image.save(spectrogram_image_path_str)

# convert the string path to a pathlib.Path object for JSON
spectrogram_image_path = Path(spectrogram_image_path_str)

data = {
    "start": {
        "prompt": "minimal emotional atmospheric synth techno beat jungle drum bass beat drop",
        "seed": 42,  # this can change and be random
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

# send a POST request to the server
response = requests.post("http://127.0.0.1:3013/run_inference/", json=data)

if response.status_code == 200:
    output = response.json()
    generated_audio = output['audio']
    generated_image = output['image']
    
    # save generated audio 
    with open('generated.mp3', 'wb') as audio_file:
        audio_file.write(base64.b64decode(generated_audio.split(',')[1]))
    
    # save generated image 
    with open('generated.jpg', 'wb') as image_file:
        image_file.write(base64.b64decode(generated_image.split(',')[1]))
    
    print("Generated audio and image saved successfully.")
else:
    print(f"Error: {response.text}")

