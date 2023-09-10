import os
#!!! have to virtual environment path
os.environ['PATH'] += ":/Users/willsaliba/opt/anaconda3/envs/riffusion/bin"

import sys
from scripts.generate import generate_without_input_audio as riff_generate
#replace

#checking for correct number of arguments
if len(sys.argv) != 5:
    print("Incorrect number of arguments provided.")
    sys.exit(1)

#extracting arguments from command line
prompt = sys.argv[1].strip('"')
action = sys.argv[2].strip('"')
random = sys.argv[3].strip('"')
path = sys.argv[4].strip('"')

#use model to generate clip
newTrackPath = ""

if action == "Generate": newTrackPath = riff_generate(prompt, random)
    
elif action == "Replace": pass #riff_replace(prompt, random, path)
    
elif action == "Extend": pass #riff_extend(prompt, random, path, time, side)
    
elif action == "Infill": pass #riff_infill(prompt, random, path1, path2?, start?, end?)

#print result so plugin can capture it
if newTrackPath == "":
    print("Reached End But Failed")
else:
    print(newTrackPath)
