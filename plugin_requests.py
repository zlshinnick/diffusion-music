import warnings
import os
import sys 
from scripts.generate import generate_without_input_audio as riff_generate
from scripts.generate import generate_with_input_audio as riff_replace

#ensuring model can be run by plugin

warnings.simplefilter("ignore")
os.environ['PATH'] += ":/Users/willsaliba/opt/anaconda3/envs/riffusion/bin" #!!! have to set virtual environment path
original_stdout = sys.stdout 
sys.stdout = open(os.devnull, 'w')

#checking for correct number of arguments
if len(sys.argv) != 5:
    print("Incorrect number of arguments provided.")
    sys.exit(1)

#extracting arguments from command line
prompt = sys.argv[1].strip('"')
action = sys.argv[2].strip('"')
random = sys.argv[3].strip('"')
path = sys.argv[4].strip('"')
#time = sys.argv[5].strip('"')
#side = sys.argv[6].strip('"')
#path2 = = sys.argv[7].strip('"')

newTrackPath = ""

if action == "Generate": 
    newTrackPath = riff_generate(prompt, random)

else:
    #trim segment if needed

    if action == "Replace": newTrackPath = riff_replace(prompt, random, path)

    elif action == "Extend": pass #riff_extend(prompt, random, path, time, side)

    elif action == "Infill": pass #riff_infill(prompt, random, path1, path2?, start?, end?)

sys.stdout = original_stdout
#print result so plugin can capture it
if newTrackPath == "":
    print("Reached End But Failed")
else:
    print(newTrackPath)

