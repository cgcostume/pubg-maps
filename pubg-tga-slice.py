
import argparse
import math
import numpy
import os
import sys

from PIL import Image

# parse arguments

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--umodel_export_path', help = 'umodel export path', required=True)
parser.add_argument('-o', '--output_path', help = 'working directory for extracting and stitching assets', default = '.')
parser.add_argument('-m', '--map', help = 'map identifier, either erangel, erangelclassic, miramar, sanhok, vikendi, karakin, or jackal', default = 'erangel')
# parser.add_argument('-l', '--lod', help = 'level-of-detail, either 0, 1, or 2', default = '0')
parser.add_argument('-c', '--compress', help = 'compression level, number between 0 and 10', default = '10')
parser.add_argument('-t', '--thumbnail', help = 'also generate 512² thumbnails', action = 'store_true')

args = parser.parse_args()

heightmap_paths = {
	'erangel' : r'Game//Maps//Baltic//Art//HeightMap',
	'erangelclassic' : r'Game//Maps//Erangel//Art//Heightmap',
	'miramar' : r'Game//Maps//Desert//Art//Heightmap',
	'sanhok'  : r'Game//Maps//Savage//Art//Heightmap',
	'vikendi' : r'Game//Maps//DihorOtok//Art//Heightmap',
	'jackal'  : r'Game//Maps//Range//Art//Heightmap',
	'karakin' : r'Game//Maps//Summerland//Art//HeightMap',
    'taego' : r'Game//Maps//tiger//Art//HeightMap',

	#'rapide'  : r'Game//Maps//Test//Rapide//Art//HeightMap',
	#'airange' : r'Game//Maps//AI_ShootingRange//AI_ShootingRange'
}

# (width, height, indexRange)
map_size_data = {
	'erangel' : (16, 16, 4),
	'erangelclassic' : (16, 16, 4),
	'miramar' : (16, 16, 4),
	'sanhok'  : ( 8,  8, 4),
	'vikendi' : (12, 12, 3),
	'jackal'  : ( 8,  8, 4),
	'karakin' : ( 4,  4, 2),
    'taego' : (16, 16, 4)

	#'rapide'  : ( 8,  8, 4),
	#'airange' : ( 5,  1, 1)
}

map_identifier = args.map.lower()
if map_identifier not in heightmap_paths:
	sys.exit('Unknown map identifier \'' + map_identifier + '\'')

map_size = map_size_data[map_identifier]
map_size_max = max(map_size[0], map_size[1])
small_map = map_size_max <= 8
num_tiles = map_size[0] * map_size[1]


assert os.path.isdir(args.umodel_export_path)
umodel_heightmap_path = os.path.abspath(os.path.join(args.umodel_export_path, heightmap_paths[map_identifier]))
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

tile_size = int(tile_width * tile_height)
# tile_size_with_mipmaps = int(tile_size * tile_channels * (1.00 + 0.25 + 0.0625))


def extract_tiles(asset_path, offsets, height_target, normal_target):

	tile_indices = [[133, 141, 149, 157, 165]] if map_identifier == 'airange' else [[0, 1, 2, 3]] if small_map else [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
	num_indices = len(numpy.array(tile_indices).flatten())

	offset_scale = 2 if small_map else 4

	rjust_len = len(str(num_tiles))

	sequence_index = 0
	for i, indices in enumerate(tile_indices):
		for j, tile_index in enumerate(indices):

			if map_identifier == 'airange':
				tile_path = asset_path % (tile_index)
			elif small_map:
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

			# extract elevation

			channel_l = numpy.left_shift(numpy.asarray(tile_r, numpy.uint16()).flatten(), 8)
			channel_l = channel_l + numpy.asarray(tile_g).flatten()

			# refine stitching sequence

			if map_identifier == 'airange':
				x = j
				y = 0
			else:
				x = offsets[0] * offset_scale + (i % 2) * 2 + (j % 2)
				y = offsets[1] * offset_scale + int(i / 2) * 2 + int(j / 2)

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

			progress = (offsets[0] * map_size[2] + offsets[1]) * num_indices + sequence_index + 1

			print ('Processing', str(progress).rjust(rjust_len, '0'), 'of', num_tiles, 
				flush = True, end = ('\r' if progress < num_tiles else '\n'))

			sequence_index += 1

	# ubulk.close()



print ('Extracting', num_tiles, 'tiles (normal and height data) ...')

normal_composite = Image.new("RGB", (tile_width * map_size[0], tile_height * map_size[1]))
height_composite = Image.new("I", (tile_width * map_size[0], tile_height * map_size[1]))

for indices in [(a, b) for a in range(0, map_size[2]) for b in range(0, map_size[2])]:
	# example '.\UmodelExport\Game\Maps\Erangel\Art\Heightmap\Heightmap_x0_y0_00_sharedAssets\Texture2D_0.tga'

	path = ''
	if map_identifier != 'airange':
		path += 'Heightmap_x%d_y%d'
		if not small_map:
			path += '_0%d'
		if map_identifier != 'rapide':
			path += '_sharedAssets'
		path += '\\'
	path += 'Texture2D_%d.tga'

	asset_path = os.path.join(umodel_heightmap_path, path)
	extract_tiles(asset_path, indices, height_composite, normal_composite)


map_size_descriptor = str(int(map_size_max / 2) if (map_size_max / 2).is_integer else map_size_max / 2) + 'k'  # ['8k', '4k', '2k'][(lod + 1) if small_map else lod]

# export normal map

normal_stitched_path = os.path.join(output_path, 'pubg_' + map_identifier + '_' + normal_semantic + '_lod' + str(lod) + '.png')
print (normal_stitched_path, 'Saving', map_size_descriptor, 'normal map ... hang in there')
normal_composite.save(normal_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)

if args.thumbnail:
	normal_stitched_path = os.path.join(output_path, 'pubg_' + map_identifier + '_' + normal_semantic + '_preview.png')
	normal_composite.thumbnail((512, 512), Image.BILINEAR)
	normal_composite.save(normal_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)

# export height map

height_stitched_path = os.path.join(output_path, 'pubg_' + map_identifier + '_' + height_semantic + '_lod' + str(lod) + '.png')
print (height_stitched_path, 'Saving', map_size_descriptor, 'height map ... hang in there')
height_composite.save(height_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)

if args.thumbnail:
	height_stitched_path = os.path.join(output_path, 'pubg_' + map_identifier + '_' + height_semantic + '_preview.png')
	height_composite.thumbnail((512, 512), Image.BILINEAR)
	height_composite.save(height_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)

print('Done!')
