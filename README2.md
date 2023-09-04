???

//setup virtual python environment
conda create --name riffusion python=3.9
conda activate riffusion

//install python dependencies
python -m pip install -r requirements_all.txt

//accept other audio formats
brew install ffmpeg

???

step 1: run "python3 setup.py install"

step 2: run "python3 riffusion/server.py"

step 3: run either "python3 scripts/inpaint.py" or "python3 scripts/generate.py" depending on which actions 

step 4: check outputs in the outputs folder


Folder Guide:

OUTPUTS - contains all the outputs from the model

SAMPLE_AUDIOS - contains all the sample mp3 tracks to use with the model (add more here if want to use them)

SCRIPTS - contains the scrips for running generations


Model Guide:

inpaint can:
    - left and right extend
    - infill
    - multiple infills

generate can:
    - text to audio
    - text & audtio to audio


