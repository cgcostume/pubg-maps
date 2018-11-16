
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
parser.add_argument('-m', '--map', help = 'map identifier, currently only athena', default = 'athena')
# parser.add_argument('-l', '--lod', help = 'level-of-detail, either 0, 1, or 2', default = '0')
parser.add_argument('-c', '--compress', help = 'compression level, number between 0 and 10', default = '0')
parser.add_argument('-t', '--thumbnail', help = 'also generate 512² thumbnails', action = 'store_true')

args = parser.parse_args()

tslHeightmapPathsByMap =  {
	'athena' : r'Athena\Maps\Landscape',
}


mapIdentifier = args.map.lower()
if mapIdentifier not in  { 'athena' }:
    sys.exit('unknown map identifier \'' + mapIdentifier + '\'')

numTiles = 144 # 10²


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

tile_width = { 0: 128 }[lod]
tile_height = { 0: 128 }[lod]
# tile_channels = 4
# tile_offset = int({ 0: 0, 1: 512 * 512 * 4 * (1.0), 2: 512 * 512 * 4 * (1.0 + 0.25)}[lod])

tile_scale = 12;
tile_size = int(tile_width * tile_height)
# tile_size_with_mipmaps = int(tile_size * tile_channels * (1.00 + 0.25 + 0.0625))


def extract_tiles(asset_path, offsets, height_target, normal_target):

	# tile_indices = [[0, 1, 2, 3]] if smallMap else [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
	tile_indices = offsets.keys()
	num_indices = len(numpy.array(tile_indices).flatten())

	# offset_scale = 2 if smallMap else 4

	sequence_index = 0
	for tile_index in tile_indices:
		offset = offsets[tile_index]

		#if smallMap:
		tile_path = asset_path % (tile_index)
		#else:
		#	tile_path = asset_path % (offsets[0], offsets[1], i, tile_index)

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

		target_x = offset[0] * tile_width
		target_y = offset[1] * tile_height

		# ordered_index = y * 10 + x

		# paste data

		# target_x = (ordered_index % 16) * tile_width
		# target_y = math.floor(ordered_index / 16) * tile_height

		# write normal tile
		
		normal_tile = Image.frombytes('RGB', (tile_width, tile_height), rgb)
		normal_target.paste(normal_tile, (target_x, target_y))

		# write height tile

		height_tile = Image.frombytes('I;16', (tile_width, tile_height), numpy.asarray(channel_l, order = 'C'))
		height_target.paste(height_tile, (target_x, target_y))

		# display progress

		progress = sequence_index + 1
		
		print ('processing', str(progress).rjust(2, '0'), 'of', numTiles, 
			flush = True, end = ('\r' if progress < numTiles else '\n'))
		
		sequence_index += 1



print ('extracting', numTiles, 'tiles (normal and height data) ...')

normal_composite = Image.new("RGB", (tile_width * tile_scale, tile_height * tile_scale))
height_composite = Image.new("I", (tile_width * tile_scale, tile_height * tile_scale))


athena_indices = {
	0: {
            
		 0: (1, 2), 1: (0, 2), 2: (0, 1), 3: (1, 1), 4: (0, 0), 5: (1, 0),
                 10: (6, 1), 14: (6, 2), 9: (6, 0), 13: (7, 2), 15: (6, 3), 12: (7, 1),
                 6: (7, 0), 28: (4, 3), 16: (5, 3), 29: (3, 3), 30: (3, 4), 31: (4, 4),
                 32: (2, 3), 33: (2, 4), 34: (3, 2), 35: (4, 2), 36: (5, 2), 37: (5, 1),
                 
		},
        1: {
            
                 1: (5, 4), 2: (6, 4), 3: (7, 4), 5: (5, 5), 6: (6, 5), 7: (7, 5),
                 10: (6, 6), 11: (7, 6), 15: (7, 7),
                 
                },
        3: {

                0: (11, 5), 1: (10, 5), 2: (9, 5), 3: (8, 5), 4: (11, 4), 5: (8, 0),
                6: (9, 0), 7: (10, 0), 9: (8, 1), 10: (9, 1), 11: (10, 1), 12: (11, 1),
                13: (8, 2), 14: (9, 2), 15: (10, 2), 16: (11, 2), 17: (8, 3), 18: (9, 3),
                19: (10, 3), 20: (11, 3), 25: (10, 4), 26: (9, 4), 27: (8, 4), 29: (7, 3),
                
                },
        4: {
            
                0: (4, 7), 8: (3, 8), 21: (2, 6), 23: (3, 7), 24: (3, 6), 26: (5, 7), 
                27: (4, 8), 32: (4, 9), 36: (6, 7), 39: (5, 6), 42: (4, 6), 45: (2, 5),
                49: (3, 5), 52: (4, 5),
                
                },
        5: {

                2: (6, 9), 4: (7, 8), 5: (7, 9), 7: (8, 8), 8: (9, 8), 9: (10, 8),
                10: (11, 8), 11: (8, 9), 12: (9, 9), 13: (10, 9), 21: (6, 8), 23: (8, 6),
                24: (9, 6), 25: (10, 6), 26: (11, 6), 27: (8, 7), 28: (9, 7), 29: (10, 7),
                30: (11, 7), 37: (5, 9), 39: (5, 8)

                }
}


if mapIdentifier == 'athena':
	offset_lookup = athena_indices

for key in offset_lookup.keys():
 	# example '.\UmodelExport\Athena\Maps\Landscape\Athena_Terrain_LS_00\Texture2D_0.tga'
	
	if mapIdentifier == 'athena':
		path = 'Athena_Terrain_LS_0' + str(key) + '\Texture2D_%d.tga'

	asset_path = os.path.join(umodel_heightmap_path, path)
	extract_tiles(asset_path, offset_lookup[key], height_composite, normal_composite)


map_size_info  = ['1.536k'][0]

normal_stitched_path = os.path.join(output_path, 'fortnite_' + mapIdentifier + '_' + normal_semantic + '_lod' + str(lod) + '.png')
print (normal_stitched_path, 'saving', map_size_info, 'normal map ... hang in there')
# normal_composite = normal_composite.transpose(Image.ROTATE_90)
normal_composite.save(normal_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)

if args.thumbnail:
	normal_stitched_path = os.path.join(output_path, 'fortnite_' + mapIdentifier + '_' + normal_semantic + '_preview.png')
	normal_composite.thumbnail((512, 512), Image.BILINEAR)
	normal_composite.save(normal_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)


height_stitched_path = os.path.join(output_path, 'fortnite_' + mapIdentifier + '_' + height_semantic + '_lod' + str(lod) + '.png')
print (height_stitched_path, 'saving', map_size_info, 'height map ... hang in there')
# height_composite = height_composite.transpose(Image.ROTATE_90)
height_composite.save(height_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)

if args.thumbnail:
	height_stitched_path = os.path.join(output_path, 'fortnite_' + mapIdentifier + '_' + height_semantic + '_preview.png')
	height_composite.thumbnail((512, 512), Image.BILINEAR)
	height_composite.save(height_stitched_path, 'PNG', compress_level = min(9, compress), optimize = compress == 10)
