import warnings
import os
import sys 
from pydub import AudioSegment
import base64
from scripts.generate import generate_without_input_audio as riff_generate
from scripts.generate import generate_with_input_audio as riff_replace
from scripts.inpaint import riff_extend
from scripts.inpaint import riff_infill

#ensuring model can be run by plugin
warnings.simplefilter("ignore")
os.environ['PATH'] += ":/Users/willsaliba/opt/anaconda3/envs/riffusion/bin" #!!! have to set virtual environment path
original_stdout = sys.stdout 
sys.stdout = open(os.devnull, 'w')
path_to_curr_dir = "/Users/willsaliba/Documents/Topics/diffusion-music"     #!!! have to set path to curr directory

# extracting arguments from command line
prompt = sys.argv[1].strip('"')
action = sys.argv[2].strip('"')
random = sys.argv[3].strip('"')
path = sys.argv[4].strip('"')
path2 = sys.argv[5].strip('"')
time = sys.argv[6].strip('"')
side = sys.argv[7].strip('"')
firstStart = sys.argv[8].strip('"')
firstEnd = sys.argv[9].strip('"')
secStart = sys.argv[10].strip('"')
secEnd = sys.argv[11].strip('"')

newTrackPath = ""
path1_extension = os.path.splitext(path)[1][1:]
path2_extension = os.path.splitext(path2)[1][1:]

#calling respective action
if action == "Generate": 
    newTrackPath = riff_generate(prompt, random)

else:
    #trimming first input segment if needed
    if int(firstStart) != 0 or int(firstEnd) != 100 :
        firstSegment = AudioSegment.from_file(path)
        startDurationToCut = (len(firstSegment) * (int(firstStart) / 100))
        endDurationToCut = (len(firstSegment) * ((100 - int(firstEnd)) / 100))
        trimmed_firstSegment = firstSegment[startDurationToCut:(len(firstSegment) - endDurationToCut)]
        #save trimmed segment to updated path
        path = os.path.join(path_to_curr_dir, f"outputs/firstSegment.{path1_extension}")
        trimmed_firstSegment.export(path, format=path1_extension)

    if action == "Replace": newTrackPath = riff_replace(prompt, random, path)

    elif action == "Extend": newTrackPath = riff_extend(prompt, path, time, side)

    elif action == "Fill": 
        #trimming second input segment if needed
        if secStart != 0 or secEnd != 100 :
            secSegment = AudioSegment.from_file(path)
            startDurationToCut = (len(secSegment) * (int(secStart) / 100))
            endDurationToCut = (len(secSegment) * ((100 - int(secEnd)) / 100))
            trimmed_secSegment = secSegment[startDurationToCut:(len(secSegment) - endDurationToCut)]
            #save trimmed segment to updated path
            path2 = os.path.join(path_to_curr_dir, f"outputs/secSegment.{path2_extension}")
            trimmed_secSegment.export(path2, format=path2_extension)

        newTrackPath = riff_infill(prompt, path, path2, time)

#reset teriminal
sys.stdout = original_stdout

#print result so plugin can capture it
if newTrackPath == "":
    print("---REACHED END BUT FAILED---")
else:
    print(newTrackPath)
