import argparse
import os.path
import shutil
import subprocess
import sys

parser = argparse.ArgumentParser()
# parser.add_argument('-pubg', '--pubg_path', help = 'PUBG path', default = r'C:\Program Files (x86)\Steam\steamapps\common\PUBG')
parser.add_argument('-tsl', '--pubg_tslgame_path', help = 'TslGame path', default = r'C:\TslGame')
parser.add_argument('-o', '--output_path', help = 'working directory for extracting and stitching assets', default = 'pubg-maps')
parser.add_argument('-m', '--map', help = 'map identifier, either Erangle or Miramar', default = 'erangle')
args = parser.parse_args()


# prepare for action

# pubgPaksPath = r'TslGame\Content\Paks'
# pakFileNamesByMapNames = {
#     'erangle' : 'TslGame-WindowsNoEditor_erangel_heightmap.pak', 
#     'miramar' : 'TslGame-WindowsNoEditor_desert_heightmap.pak' }

# ue4unpacker = 'ue4pakunpacker.exe'

# # assert preconditions

# mapIdentifier = args.map.lower()
# if mapIdentifier not in  {'erangle', 'miramar'}:
#     sys.exit('unknown map identifier \'' + mapIdentifier + '\'')

# assert os.path.isdir(args.pubg_path)
# assert os.path.isdir(os.path.join(args.pubg_path, pubgPaksPath))

# pakFilePath = os.path.abspath(os.path.join(args.pubg_path, pubgPaksPath, pakFileNamesByMapNames[mapIdentifier]))
# assert os.path.isfile(pakFilePath)

# outputPath = args.output_path
# if not os.path.isdir(outputPath):
#     os.makedirs(outputPath)
# assert os.path.isdir(outputPath)

# assert os.path.isfile(ue4unpacker)
# ue4unpackerPath = os.path.abspath(ue4unpacker)

# # copy relevant paks

# print ('copy relevant pak(s)')
# shutil.copy2(pakFilePath, outputPath) 
# pakFilePathCopied = os.path.join(outputPath, pakFileNamesByMapNames[mapIdentifier])

# # unpack paks

# print ('popen ue4pakunpacker in \'' + outputPath + '\' | wait for it')

# orig_cwd = os.getcwd() # remember our original working directory
# output_cwd = os.path.join(os.path.abspath(sys.path[0]), outputPath)
# os.chdir(output_cwd)

# process = subprocess.Popen(ue4unpackerPath + ' ' + pakFileNamesByMapNames[mapIdentifier])
# process.wait()

# os.chdir(orig_cwd)


