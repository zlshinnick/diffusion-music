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

if response.status_code == 200:
    output = response.json()
    generated_audio = output['audio']
    
    with open('generated_audio.mp3', 'wb') as audio_file:
        audio_file.write(base64.b64decode(generated_audio.split(',')[1]))
    
    print("Generated audio saved successfully.")
else:
    print(f"Error: {response.text}")
