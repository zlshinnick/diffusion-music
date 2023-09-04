import sys

from scripts.generate import generate_without_input_audio as riff_generate
# from scripts.generate import generate_with_input_audio as riff_replace

#checking for correct number of arguments
if len(sys.argv) != 5:
    print("Incorrect number of arguments provided.")
    sys.exit(1)

#extracting arguments from command line
prompt = sys.argv[1]
action = sys.argv[2]
random = sys.argv[3]
path = sys.argv[4]

#use model to generate clip
newTrackPath = ""

if action == "Generate": riff_generate(prompt, random)
    
elif action == "Replace": pass #riff_replace(prompt, random, path)
    
elif action == "Extend": pass #riff_extend(prompt, random, path, time, side)
    
elif action == "Infill": pass #riff_infill(prompt, random, path1, path2?, start?, end?)

#print result so c++ can capture it
print(newTrackPath)
