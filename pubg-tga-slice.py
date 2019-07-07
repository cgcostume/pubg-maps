
import argparse
import math
import numpy
import os
import sys

from PIL import Image

# parse arguments

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--umodel_export_path', help = 'umodel export path')
parser.add_argument('-o', '--output_path', help = 'working directory for extracting and stitching assets', default = '.')
parser.add_argument('-m', '--map', help = 'map identifier, either erangel, miramar, or savage', default = 'erangel')
# parser.add_argument('-l', '--lod', help = 'level-of-detail, either 0, 1, or 2', default = '0')
parser.add_argument('-c', '--compress', help = 'compression level, number between 0 and 10', default = '0')
parser.add_argument('-t', '--thumbnail', help = 'also generate 512² thumbnails', action = 'store_true')

args = parser.parse_args()

# pakFileNamesByMapNames = {
#     'erangel' : 'TslGame-WindowsNoEditor_erangel_heightmap.pak', 
#     'miramar' : 'TslGame-WindowsNoEditor_desert_heightmap.pak' }

tslHeightmapPathsByMap =  {
	'erangel' : r'Maps//Erangel//Art//Heightmap', 
	'miramar' : r'Maps//Desert//Art//Heightmap',
	'range' : r'Maps//Range//Art//Heightmap',
	'sanhok' :  r'Maps//Savage//Art//Heightmap',
	'vikendi' : r'Maps//DihorOtok//Art//HeightMap', }


mapIdentifier = args.map.lower()
if mapIdentifier not in  {'erangel', 'miramar', 'range', 'sanhok', 'vikendi' }:
    sys.exit('unknown map identifier \'' + mapIdentifier + '\'')

smallMap = mapIdentifier == 'sanhok' or mapIdentifier == 'range' 
mediumMap = mapIdentifier == 'vikendi'
numTiles = 64 if smallMap else 176 if mediumMap else 256


assert os.path.isdir(args.umodel_export_path)
umodel_heightmap_path = os.path.abspath(os.path.join(args.umodel_export_path, tslHeightmapPathsByMap[mapIdentifier]))
assert os.path.isdir(umodel_heightmap_path)

output_path = args.output_path
if not os.path.isdir(output_path):
    os.makedirs(output_path)
assert os.path.isdir(output_path)


normal_semantic = 'normal_rg8'
height_semantic = 'height_l16'

lod = 0 # int(args.lod)
compress = int(args.compress)

# slicing data

tile_width = { 0: 512, 1: 256, 2: 128 }[lod]
tile_height = { 0: 512, 1: 256, 2: 128 }[lod]
# tile_channels = 4
# tile_offset = int({ 0: 0, 1: 512 * 512 * 4 * (1.0), 2: 512 * 512 * 4 * (1.0 + 0.25)}[lod])

tile_scale = 8 if smallMap else 12 if mediumMap else 16;
tile_size = int(tile_width * tile_height)
# tile_size_with_mipmaps = int(tile_size * tile_channels * (1.00 + 0.25 + 0.0625))


def extract_tiles(asset_path, offsets, height_target, normal_target):

	tile_indices = [[0, 1, 2, 3]] if smallMap else [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
	num_indices = len(numpy.array(tile_indices).flatten())

	offset_scale = 2 if smallMap else 4

	sequence_index = 0
	for i, indices in enumerate(tile_indices):
		for tile_index in indices:

			if smallMap:
				tile_path = asset_path % (offsets[0], offsets[1], tile_index)
			else:
				tile_path = asset_path % (offsets[0], offsets[1], i, tile_index)
	
			tile = Image.open(tile_path)
			tile_r, tile_g, tile_b, tile_a = tile.split()

			# extract normal	
			
			channel_r = numpy.asarray(tile_b).flatten()
			channel_g = numpy.asarray(tile_a).flatten()

			channel_b = numpy.resize(numpy.uint8(), tile_size)
			channel_b.fill(255)

			rgb = numpy.dstack((channel_r, channel_g, channel_b)).flatten()

			# # extract elevation

			channel_l = numpy.left_shift(numpy.asarray(tile_r, numpy.uint16()).flatten(), 8)
			channel_l = channel_l + numpy.asarray(tile_g).flatten()
		
			# refine stitching sequence

			x = offsets[0] * offset_scale + int(i % 2) * 2 + int(tile_index % 2)
			y = offsets[1] * offset_scale + int(i / 2) * 2 + int(tile_index / 2)

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

			progress = (offsets[0] * 4 + offsets[1]) * num_indices + sequence_index + 1
			
			print ('processing', str(progress).rjust(2 if smallMap else 3, '0'), 'of', numTiles, 
				flush = True, end = ('\r' if progress < numTiles else '\n'))

			sequence_index += 1

	# 	ubulk.close()



print ('extracting', numTiles, 'tiles (normal and height data) ...')

normal_composite = Image.new("RGB", (tile_width * tile_scale, tile_height * tile_scale))
height_composite = Image.new("I", (tile_width * tile_scale, tile_height * tile_scale))

indicespos = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2),] if mediumMap else [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)]

for indices in indicespos:
 	# example '.\UmodelExport\Maps\Erangel\Art\Heightmap\Heightmap_x0_y0_00_sharedAssets\Texture2D_0.tga'
	
	path = 'Heightmap_x%d_y%d_'
	if not smallMap:
		path = path + '0%d_'
	path = path + 'sharedAssets\Texture2D_%d.tga'

	asset_path = os.path.join(umodel_heightmap_path, path)
	extract_tiles(asset_path, (indices[0], indices[1]), height_composite, normal_composite)


map_size_info  = ['8k', '4k', '2k'][(lod + 1) if smallMap else lod]


normal_stitched_path = os.path.join(output_path, 'pubg_' + mapIdentifier + '_' + normal_semantic + '_lod' + str(lod) + '.png')
print (normal_stitched_path, 'saving', map_size_info, 'normal map ... hang in there')
normal_composite.save(normal_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)

if args.thumbnail:
	normal_stitched_path = os.path.join(output_path, 'pubg_' + mapIdentifier + '_' + normal_semantic + '_preview.png')
	normal_composite.thumbnail((512, 512), Image.BILINEAR)
	normal_composite.save(normal_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)


height_stitched_path = os.path.join(output_path, 'pubg_' + mapIdentifier + '_' + height_semantic + '_lod' + str(lod) + '.png')
print (height_stitched_path, 'saving', map_size_info, 'height map ... hang in there')
height_composite.save(height_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)

if args.thumbnail:
	height_stitched_path = os.path.join(output_path, 'pubg_' + mapIdentifier + '_' + height_semantic + '_preview.png')
	height_composite.thumbnail((512, 512), Image.BILINEAR)
	height_composite.save(height_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)
