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
	'athena' : r'Game\Athena\Maps\Landscape',
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
                
                0: (7, 0), 123: (0, 2), 107: (7, 1),  99: (0, 1), 96: (2, 0),
                78: (7, 2), 75: (1, 1), 45: (1, 2), 25: (0, 0), 23: (1, 0),
                 
		},
        1: {
        
                1: (5, 4), 2: (6, 4), 3: (7, 4), 5: (5, 5), 6: (6, 5),10: (6, 6), 
                25: (11, 10), 40: (11, 11),  49: (9, 4), 11: (8, 4), 4: (7, 5),
                53: (7, 6), 36: (8, 5), 43: (9, 5),
                
                },
        2: {

                11: (3, 3), 10: (3, 2), 9:(3, 1), 8: (3, 0), 7: (4, 1), 6: (4, 0),
                5: (5, 1), 4: (6, 1), 3: (5, 0), 0: (6, 0), 63: (2, 3), 22: (2, 4),
                21: (2, 2), 20: (2, 1), 19: (6, 3), 18: (4, 4), 17: (3, 4),
                16: (5, 3), 15: (6, 2), 14: (5, 2), 13: (4, 2), 12: (4, 3),

            },
        
        3: {

                52: (11, 4), 42: (11, 3), 22: (11, 2), 1: (11, 1), 164: (11, 5),
                160: (8, 0), 158: (9, 0), 156: (10, 0), 154: (10, 1), 150: (10, 2),
                147: (9, 1), 144: (8, 1), 141: (10, 3), 136: (10, 4), 133: (9, 2),
                128: (9, 3), 70: (8, 3), 65: (8, 2), 61: (7, 3),
                
                },
        4: {
            
                0: (4, 7), 8: (3, 8), 21: (2, 6), 23: (3, 7), 24: (3, 6), 26: (5, 7), 
                27: (4, 8), 32: (4, 9), 36: (6, 7), 39: (5, 6), 42: (4, 6), 45: (2, 5),
                49: (3, 5), 52: (4, 5),  10: (6, 8), 11: (6, 9), 12: (5, 8), 13: (5, 9),
                
                },
        5: {

                142: (11, 8), 139: (10, 8), 136: (10, 7), 129: (11, 7), 131:(11, 6),
                126: (8, 8), 123: (7, 9), 117: (8, 9), 187: (10, 5), 184: (9, 6),
                181: (10, 6), 172: (8, 7), 169: (8, 6), 160: (7, 7), 157: (7, 8),
                154: (9, 7), 151: (9, 8), 149: (9, 9), 147: (10, 9), 

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
