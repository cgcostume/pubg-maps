
import argparse
import math
import numpy
import os
import sys

from PIL import Image

# parse arguments

parser = argparse.ArgumentParser()
parser.add_argument('-tsl', '--tslgame_path', help = 'TslGame path', default = r'C:\TslGame')
parser.add_argument('-o', '--output_path', help = 'working directory for extracting and stitching assets', default = '.')
parser.add_argument('-m', '--map', help = 'map identifier, either Erangel or Miramar', default = 'erangel')
parser.add_argument('-l', '--lod', help = 'level-of-detail, either 0, 1, or 2', default = '0')
parser.add_argument('-c', '--compress', help = 'compression level, number between 0 and 10', default = '0')

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
height_semantic = 'height_l16'

lod = int(args.lod)
compress = int(args.compress)

# slicing data

tile_width = { 0: 512, 1: 256, 2: 128 }[lod]
tile_height = { 0: 512, 1: 256, 2: 128 }[lod]
tile_channels = 4
tile_offset = int({ 0: 0, 1: 512 * 512 * 4 * (1.0), 2: 512 * 512 * 4 * (1.0 + 0.25)}[lod])

tile_size = int(tile_width * tile_height)
# tile_size_with_mipmaps = int(tile_size * tile_channels * (1.00 + 0.25 + 0.0625))


ubulk_indices_erangel_in_sequence = [	
	  (0, 0, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (0, 1, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (0, 2, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (0, 3, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (1, 0, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (1, 1, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (1, 2, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (1, 3, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (2, 0, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (2, 1, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (2, 2, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (2, 3, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (3, 0, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (3, 1, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (3, 2, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
	, (3, 3, [15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0])
]

ubulk_indices_miramar_in_sequence = [	
	  (0, 0, [ 5,  7,  8, 31, 11, 14, 12, 13, 16, 15,  2,  3,  4, 32,  6, 39])
	, (0, 1, [64, 65, 66,  0, 11, 12, 14, 70, 15, 28, 29,  3, 32, 33, 35,  7])
	, (0, 2, [ 0,  1, 20,  9, 10, 11, 22, 23, 14, 15,  2,  3,  4,  5, 38, 49])
	, (0, 3, [ 0,  1, 37, 41, 10, 11, 12, 57, 14, 15,  2,  3,  4,  5,  6,  7])
	, (1, 0, [ 0,  1,  8,  9, 10, 11, 12, 13, 14, 15,  2,  3, 16, 17,  6,  7])
	, (1, 1, [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 26, 10, 11, 12, 32, 13])
	, (1, 2, [ 0,  1,  8,  9, 10, 11, 12, 13, 14, 15,  2,  3,  4,  5,  6,  7])
	, (1, 3, [ 0,  1,  8,  9, 10, 11, 12, 13, 14, 15,  2,  3,  4,  5,  6,  7])
	, (2, 0, [ 0,  1,  8,  9, 10, 11, 12, 13, 14, 15, 20, 24, 25,  5, 28, 34])
	, (2, 1, [ 0,  1,  8,  9, 15, 11, 12, 13, 14, 25, 34, 35, 36, 37, 66,  7])
	, (2, 2, [ 0,  1,  8,  9, 10, 11, 12, 13, 14, 15,  2,  3,  4,  5,  6,  7])
	, (2, 3, [ 0,  1,  8,  9, 10, 11, 12, 13, 14, 15,  2,  3,  4,  5,  6,  7])
	, (3, 0, [ 0,  1,  8,  9, 10, 11, 12, 13, 14, 15,  2,  3,  4,  5,  6,  7])
	, (3, 1, [ 0,  1,  8,  9, 10, 11, 12, 13, 14, 15,  2,  3,  4,  5,  6,  7])
	, (3, 2, [ 0,  1,  8,  9, 10, 11, 12, 13, 14, 15,  2,  3, 31,  5,  6,  7])
	, (3, 3, [41,  1,  8,  9, 10, 11, 12, 13, 14, 15,  2,  3,  4,  5,  6,  7])
]

ubulk_indices_in_sequence = { 
	'erangel' : ubulk_indices_erangel_in_sequence, 
	'miramar' : ubulk_indices_miramar_in_sequence }[mapIdentifier]


def extract_tiles(asset_path, offsets, indices, height_target, normal_target):

	
	sequence_index = 0
	for i, tile_index in enumerate(indices):
	
		ubulk_path = os.path.abspath(os.path.join(asset_path, 'Texture2D_%d.ubulk' % (tile_index)))

		ubulk = open(ubulk_path, "rb")

		ubulk.seek(tile_offset)
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

		x  = offsets[0] * 4 + int(i % 4)
		y  = offsets[1] * 4 + int(i / 4)
		ordered_index = y * 16 + x

		# paste data

		target_x = (ordered_index % 16) * tile_width
		target_y = math.floor(ordered_index / 16) * tile_height

		# write normal tile

		normal_tile = Image.frombytes('RGB', (tile_width, tile_height), rgb)
		normal_target.paste(normal_tile, (target_x, target_y))

		# write height tile

		height_tile = Image.frombytes('I;16', (tile_width, tile_height), numpy.asarray(channel_l, order = 'C'))
		height_target.paste(height_tile, (target_x, target_y))

		# display progress

		progress = (offsets[0] * 4 + offsets[1]) * 16 + sequence_index + 1
		print ('processing', str(progress).rjust(3, '0'), 'of 256', flush = True, end = ('\r' if progress < 256 else '\n'))

		sequence_index += 1

		ubulk.close()



print ('extracting 256 tiles (normal and height data) ...')

normal_composite = Image.new("RGB", (tile_width * 16, tile_height * 16))
height_composite = Image.new("I", (tile_width * 16, tile_height * 16))


for indices in ubulk_indices_in_sequence:
 	# example 'C:\TslGame\Content\Maps\Erangel\Art\Heightmap\Heightmap_x0_y0_sharedAssets\Texture2D_0.ubulk'
	asset_path = os.path.join(tsl_heightmap_path, 'Heightmap_x%d_y%d_sharedAssets' % (indices[0], indices[1]))
	extract_tiles(asset_path, (indices[0], indices[1]), indices[2], height_composite, normal_composite)


normal_stitched_path = os.path.join(output_path, 'pubg_' + mapIdentifier + '_' + normal_semantic + '_lod' + str(lod) + '.png')
print (normal_stitched_path, 'saving', ['8k', '4k', '2k'][lod], 'normal map ... hang in there')
normal_composite.save(normal_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)

height_stitched_path = os.path.join(output_path, 'pubg_' + mapIdentifier + '_' + height_semantic + '_lod' + str(lod) + '.png')
print (normal_stitched_path, 'saving', ['8k', '4k', '2k'][lod], 'height map ... hang in there')
height_composite.save(height_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)
