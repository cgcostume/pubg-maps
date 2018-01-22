
import argparse
import glob
import math
import numpy
import os
import png
import sys

import PIL
from PIL import Image

# parse arguments

parser = argparse.ArgumentParser()
parser.add_argument('-tsl', '--tslgame_path', help = 'TslGame path', default = r'C:\TslGame')
parser.add_argument('-o', '--output_path', help = 'working directory for extracting and stitching assets', default = 'pubg-maps')
parser.add_argument('-m', '--map', help = 'map identifier, either Erangel or Miramar', default = 'erangel')
args = parser.parse_args()

# pakFileNamesByMapNames = {
#     'erangel' : 'TslGame-WindowsNoEditor_erangel_heightmap.pak', 
#     'miramar' : 'TslGame-WindowsNoEditor_desert_heightmap.pak' }

tslHeightmapPathsByMap =  {
	'erangel' : r'Content\Maps\Erangel\Art\Heightmap', 
	'miramar' : r'Content\Maps\Desert\Art\Heightmap' }

mapIdentifier = args.map.lower()
if mapIdentifier not in  {'erangel', 'miramar'}:
    sys.exit('unknown map identifier \'' + mapIdentifier + '\'')


assert os.path.isdir(args.tslgame_path)
tsl_heightmap_path = os.path.abspath(os.path.join(args.tslgame_path, tslHeightmapPathsByMap[mapIdentifier]))
assert os.path.isdir(tsl_heightmap_path)

output_path = args.output_path
if not os.path.isdir(output_path):
    os.makedirs(output_path)
assert os.path.isdir(output_path)


normal_semantic = 'normal_rg8'
normal_path = os.path.join(output_path, '.normal_' + mapIdentifier)

height_semantic = 'height_l16'
height_path = os.path.join(output_path, '.height_' + mapIdentifier)

if not os.path.isdir(normal_path):
	os.makedirs(normal_path)
if not os.path.isdir(height_path):
	os.makedirs(height_path)


# slicing data

tile_width = 512
tile_height = 512
tile_channels = 4

tile_size = int(tile_width * tile_height)

tile_size_with_mipmaps = int(tile_size * tile_channels * (1.00 + 0.25 + 0.0625))
tile_offset = int(tile_size * tile_channels * (0.25 + 0.0625))


ubulk_indices = [ 
	  (0, 0, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (0, 1, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (0, 2, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (0, 3, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (1, 0, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (1, 1, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (1, 2, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (1, 3, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (2, 0, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (2, 1, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (2, 2, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (2, 3, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (3, 0, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (3, 1, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (3, 2, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
	, (3, 3, [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ])
]

tile_sequence = [
	  (3, 3), (2, 3), (1, 3), (0, 3), (3, 2), (2, 2), (1, 2), (0, 2)
	, (3, 1), (2, 1), (1, 1), (0, 1), (3, 0), (2, 0), (1, 0), (0, 0)]

progress_length = 32




def slice_tiles(asset_path, offsets, indices):

	sequence_index = 0
	for tile_index in indices:
	
		ubulk_path = os.path.abspath(os.path.join(asset_path, 'Texture2D_%d.ubulk' % (tile_index)))

		ubulk = open(ubulk_path, "rb")

		tile = ubulk.read(tile_size * tile_channels)
		if not tile:
	 		print('index not found', asset_path, tile_index)
	 		break


		# extract normal

		normal_uint8 = numpy.fromstring(tile, numpy.uint8)

		channel_r = normal_uint8[0::4]
		channel_g = normal_uint8[3::4]

		channel_b = numpy.resize(numpy.uint8(), tile_size)
		channel_b.fill(255)

		rgb = numpy.dstack((channel_r, channel_g, channel_b)).flatten()


		# extract elevation

		height_uint16 = numpy.fromstring(tile[1:] + b'\x00', numpy.uint16)

		channel_l = height_uint16[0::2]


		# refine stitching sequence

		x  = offsets[0] * 4 + tile_sequence[sequence_index][0]
		y  = offsets[1] * 4 + tile_sequence[sequence_index][1]
		ordered_index = y * 16 + x

		tile_identifier = '_' + '{0:03}'.format(ordered_index) 
		normal_tile_path = os.path.join(normal_path, normal_semantic + tile_identifier + '.png')
		height_tile_path = os.path.join(height_path, height_semantic + tile_identifier + '.png')

		
		# write normal tile

		tile_png = open(normal_tile_path, "wb")
		png_writer = png.Writer(width = tile_width, height = tile_height, bitdepth = 8, compression = 9)
		png_writer.write_array(tile_png, rgb)
		tile_png.close()


		# write height tile

		tile_png = open(height_tile_path, "wb")
		png_writer = png.Writer(width = tile_width, height = tile_height, greyscale = True,  bitdepth = 16, compression = 9)
		png_writer.write_array(tile_png, channel_l)
		tile_png.close()


		# display progress

		progress = (offsets[0] * 4 + offsets[1]) * 16 + sequence_index + 1
		print (normal_tile_path + ', ' + height_tile_path, '(' + str(progress).rjust(3, '0'), 'of 256)', flush = True, end = ('\r' if progress < 256 else '\n'))

		sequence_index += 1

		ubulk.close()




for indices in ubulk_indices:
 	# example 'C:\TslGame\Content\Maps\Erangel\Art\Heightmap\Heightmap_x0_y0_sharedAssets\Texture2D_0.ubulk'
  	asset_path = os.path.join(tsl_heightmap_path, 'Heightmap_x%d_y%d_sharedAssets' % (indices[0], indices[1]))
  	slice_tiles(asset_path, (indices[0], indices[1]), indices[2])




print ('stitching 256 normal tiles ...')
ubulk_composite = Image.new("RGB", (tile_width * 16, tile_height * 16))

tile_index = 0
for file_path in glob.glob(os.path.join(normal_path, normal_semantic + '_*.png')):

	tile = Image.open(file_path)

	x = (tile_index % 16) * tile_width
	y = math.floor(tile_index / 16) * tile_height

	ubulk_composite.paste(tile, (x, y))
	tile_index += 1

normal_stitched_path = os.path.join(output_path, 'pubg_' + mapIdentifier + '_' + normal_semantic + '.png')
print (normal_stitched_path, 'saving 8k normal map ... hang in there')
ubulk_composite.save(normal_stitched_path)




print ('stitching 256 height tiles ...')
ubulk_composite = Image.new("I", (tile_width * 16, tile_height * 16))

tile_index = 0
for file_path in glob.glob(os.path.join(height_path, height_semantic + '_*.png')):
	
 	tile = Image.open(file_path)
	
 	x = (tile_index % 16) * tile_width
 	y = math.floor(tile_index / 16) * tile_height

 	ubulk_composite.paste(tile, (x, y))
 	tile_index += 1


height_stitched_path = os.path.join(output_path, 'pubg_' + mapIdentifier + '_' + height_semantic + '.png')
print (height_stitched_path, 'saving 8k height map ... hang in there')
ubulk_composite.save(height_stitched_path)
