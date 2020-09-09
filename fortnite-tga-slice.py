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
parser.add_argument('-m', '--map', help = 'map identifier, apollo and papaya', default = 'apollo')
# parser.add_argument('-l', '--lod', help = 'level-of-detail, either 0, 1, or 2', default = '0')
parser.add_argument('-c', '--compress', help = 'compression level, number between 0 and 10', default = '0')
parser.add_argument('-t', '--thumbnail', help = 'also generate 512 thumbnails', action = 'store_true')

args = parser.parse_args()

tslHeightmapPathsByMap =  {
        'apollo' : r'Game\Athena\Apollo\Maps\Landscape',
        'papaya' : r'Game\Athena\Apollo\Maps\Special\Papaya\Landscape',
}


mapIdentifier = args.map.lower()
if mapIdentifier not in  { 'apollo', 'papaya' }:
    sys.exit('unknown map identifier \'' + mapIdentifier + '\'')

if mapIdentifier == 'apollo':
        numTiles = 256
elif mapIdentifier == 'papaya':
        numTiles = 64

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

if mapIdentifier == 'apollo':
        tile_scale = 16;
elif mapIdentifier == 'papaya':
        tile_scale = 8;

tile_size = int(tile_width * tile_height)
# tile_size_with_mipmaps = int(tile_size * tile_channels * (1.00 + 0.25 + 0.0625))


def extract_tiles(asset_path, offsets, height_target, normal_target, texture_key):

        global tile_width
        global tile_height

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
                #       tile_path = asset_path % (offsets[0], offsets[1], i, tile_index)

                tile = Image.open(tile_path)
                tile_r, tile_g, tile_b, tile_a = tile.split()

                # extract normal                
                
                channel_r = numpy.asarray(tile_b).flatten()
                channel_g = numpy.asarray(tile_a).flatten()

                channel_b = numpy.resize(numpy.uint8(), tile_size);
                channel_b.fill(255)

                rgb = numpy.dstack((channel_r, channel_g, channel_b)).flatten()

                # # extract elevation

                channel_l = numpy.left_shift(numpy.asarray(tile_r, numpy.uint16()).flatten(), 8)
                channel_l = channel_l + numpy.asarray(tile_g).flatten()
        
                # refine stitching sequence

                target_x = offset[0] * (tile_width - 1)
                target_y = offset[1] * (tile_height - 1)

                tile_width = { 0: 128 }[lod]; tile_height = { 0: 128 }[lod];
                normal_tile = Image.frombytes('RGB', (tile_width, tile_height), rgb);
                height_tile = Image.frombytes('I;16', (tile_width, tile_height), numpy.asarray(channel_l, order = 'C'));

                # ordered_index = y * 10 + x

                # paste data

                # target_x = (ordered_index % 16) * tile_width
                # target_y = math.floor(ordered_index / 16) * tile_height

                # write normal tile
                
                normal_target.paste(normal_tile, (target_x, target_y))

                # write height tile

                height_target.paste(height_tile, (target_x, target_y))

                # display progress

                progress = sequence_index + 1
                
                print ('processing', str(progress).rjust(2, '0'), 'of', numTiles, 
                        flush = True, end = ('\r' if progress < numTiles else '\n'))
                
                sequence_index += 1



print ('extracting', numTiles, 'tiles (normal and height data) ...')

normal_composite = Image.new("RGB", (tile_width * tile_scale, tile_height * tile_scale), (127, 127, 255))
height_composite = Image.new("I", (tile_width * tile_scale, tile_height * tile_scale), (26050))


apollo_indices = { 

'A4': { 0: (8, 0), 10: (9, 0), 5: (8, 1), 15: (9, 1), }, 
'A3': { 0: (10, 0), 10: (11, 0), 5: (10, 1), 15: (11, 1), },
'A6': { 5: (5, 1), }, 
'A5': { 5: (6, 1), 15: (7, 1), }, 
'A2': { 5: (12, 1), 10: (13, 1), }, 
'B7': { 10: (3, 2), 5: (2, 3), 15: (3, 3), }, 
'B6': { 0: (4, 2), 10: (5, 2), 5: (4, 3), 15: (5, 3), }, 
'B5': { 0: (6, 2), 10: (7, 2), 5: (6, 3), 15: (7, 3), }, 
'B4': { 0: (8, 2), 10: (9, 2), 5: (8, 3), 15: (9, 3), }, 
'B3': { 0: (10, 2), 10: (11, 2), 5: (10, 3), 15: (11, 3), },
'B2': { 0: (12, 2), 10: (13, 2), 5: (12, 3), 15: (13, 3), }, 
'B1': { 14: (14, 2), 20: (15, 2), 0: (14, 3), 5: (15, 3), },
'C7': { 0: (2, 4), 10: (3, 4), 5: (2, 5), 15: (3, 5), }, 
'C6': { 0: (4, 4), 10: (5, 4), 5: (4, 5), 15: (5, 5), }, 
'C5': { 0: (6, 4), 10: (7, 4), 5: (6, 5), 15: (7, 5), },
'C4': { 0: (8, 4), 10: (9, 4), 5: (8, 5), 15: (9, 5), }, 
'C3': { 0: (10, 4), 10: (11, 4), 5: (10, 5), 15: (11, 5), }, 
'C2': { 0: (12, 4), 10: (13, 4), 5: (12, 5), 15: (13, 5), },
'C1': { 0: (14, 4), 10: (15, 4), 5: (14, 5), 15: (15, 5), }, 
'C8': { 5: (1, 5), }, 
'D8': { 0: (0, 6), 10: (1, 6), 5: (0, 7), 15: (1, 7), }, 
'D7': { 0: (2, 6), 10: (3, 6), 5: (2, 7), 15: (3, 7), }, 
'D6': { 0: (4, 6), 10: (5, 6), 5: (4, 7), 15: (5, 7), },
'D5': { 0: (6, 6), 10: (7, 6), 5: (6, 7), 15: (7, 7), }, 
'D4': { 0: (8, 6), 10: (9, 6), 5: (8, 7), 15: (9, 7), },
'D3': { 0: (10, 6), 10: (11, 6), 5: (10, 7), 15: (11, 7), }, 
'D2': { 0: (12, 6), 10: (13, 6), 5: (12, 7), 15: (13, 7), }, 
'D1': { 0: (14, 6), 10: (15, 6), 5: (14, 7), 15: (15, 7), }, 
'E8': { 0: (0, 8), 10: (1, 8), 5: (0, 9), 15: (1, 9), },
'E7': { 0: (2, 8), 10: (3, 8), 5: (2, 9), 15: (3, 9), }, 
'E6': { 0: (4, 8), 10: (5, 8), 5: (4, 9), 15: (5, 9), }, 
'E5': { 0: (6, 8), 10: (7, 8), 5: (6, 9), 15: (7, 9), }, 
'E4': { 0: (8, 8), 10: (9, 8), 5: (8, 9), 15: (9, 9), }, 
'E3': { 0: (10, 8), 10: (11, 8), 5: (10, 9), 15: (11, 9), }, 
'E2': { 0: (12, 8), 10: (13, 8), 5: (12, 9), 15: (13, 9), }, 
'E1': { 0: (14, 8), 10: (15, 8), 5: (14, 9), }, 
'F8': { 0: (0, 10), 10: (1, 10), 5: (0, 11), 15: (1, 11), }, 
'F7': { 0: (2, 10), 10: (3, 10), 5: (2, 11), 15: (3, 11), },
'F6': { 0: (4, 10), 10: (5, 10), 5: (4, 11), 15: (5, 11), }, 
'F5': { 0: (6, 10), 10: (7, 10), 5: (6, 11), 15: (7, 11), }, 
'F4': { 0: (8, 10), 10: (9, 10), 5: (8, 11), 15: (9, 11), },
'F3': { 0: (10, 10), 10: (11, 10), 5: (10, 11), 15: (11, 11), }, 
'F2': { 0: (12, 10), 10: (13, 10), 5: (12, 11), 15: (13, 11), }, 
'F1': { 0: (14, 10), 10: (15, 10), 5: (14, 11), 15: (15, 11), }, 
'G8': { 0: (0, 12), 10: (1, 12), 5: (0, 13), 15: (1, 13), },
'G7': { 0: (2, 12), 10: (3, 12), 5: (2, 13), 15: (3, 13), }, 
'G6': { 0: (4, 12), 10: (5, 12), 5: (4, 13), 15: (5, 13), }, 
'G5': { 0: (6, 12), 10: (7, 12), 5: (6, 13), 15: (7, 13), }, 
'G4': { 0: (8, 12), 10: (9, 12), 5: (8, 13), 15: (9, 13), }, 
'G3': { 0: (10, 12), 10: (11, 12), 5: (10, 13), 15: (11, 13), }, 
'G2': { 0: (12, 12), 10: (13, 12), 5: (12, 13), 15: (13, 13), },
'G1': { 0: (14, 12), 5: (14, 13), }, 
'H8': { 10: (1, 14), 15: (1, 15), },
'H7': { 0: (2, 14), 10: (3, 14), 5: (2, 15), 15: (3, 15), }, 
'H6': { 0: (4, 14), 10: (5, 14), 5: (4, 15), 15: (5, 15), }, 
'H5': { 0: (6, 14), 10: (7, 14), 5: (6, 15), 15: (7, 15), }, 
'H4': { 0: (8, 14), 10: (9, 14), 5: (8, 15), 15: (9, 15), }, 
'H3': { 0: (10, 14), 10: (11, 14), 5: (10, 15), 15: (11, 15), }, 
'H2': { 0: (12, 14), 10: (13, 14), 5: (12, 15), },
'H1': { 0: (14, 14), }, 

}

papaya_indices = {
    
        'A1': { 0: (6, 0), 10: (6, 1), 15: (7, 1), 5: (7, 0) },
        
        'A2': { 0: (5, 0), 10: (4, 0), 15: (5, 1), 5: (4, 1) },

        'A3': { 0: (2, 0), 10: (2, 1), 15: (3, 1), 5: (3, 0) },

        'A4': { 0: (0, 0), 10: (1, 0), 15: (1, 1), 5: (0, 1) },

        'B1': { 0: (6, 2), 10: (7, 2), 15: (7, 3), 5: (6, 3) },
        
        'B2': { 0: (4, 2), 10: (5, 2), 15: (5, 3), 5: (4, 3) },
        
        'B3': { 0: (2, 2), 10: (3, 2), 15: (3, 3), 5: (2, 3) },
        
        'B4': { 0: (0, 2), 10: (1, 2), 15: (1, 3), 5: (0, 3) },
        
        'C1': { 0: (6, 4), 10: (6, 5), 15: (7, 5), 5: (7, 4) },
        
        'C2': { 0: (5, 4), 14: (4, 5), 20: (4, 4), 8: (5, 5) },
        
        'C3': { 0: (3, 4), 12: (2, 5), 17: (3, 5), 7: (2, 4) },
        
        'C4': { 0: (1, 4), 12: (0, 5), 17: (1, 5), 7: (0, 4) },

        'D1': { 0: (7, 6), 12: (6, 7), 17: (7, 7), 7: (6, 6) },
        
        'D2': { 0: (5, 6), 12: (4, 7), 17: (5, 7), 7: (4, 6) },
        
        'D3': { 0: (3, 6), 12: (2, 7), 17: (3, 7), 7: (2, 6) },
        
        'D4': { 0: (1, 6), 12: (0, 7), 17: (1, 7), 7: (0, 6) },

}


if mapIdentifier == 'apollo':
        offset_lookup = apollo_indices
elif mapIdentifier == 'papaya':
        offset_lookup = papaya_indices

for key in offset_lookup.keys():
        # example '.\UmodelExport\Athena\Apollo\Maps\Landscape\Apollo_Terrain_LS_AB12\Texture2D_0.tga'
        
        if mapIdentifier == 'apollo':
                path = 'Apollo_Terrain_LS_' + str(key) + '\Texture2D_%d.tga'
        elif mapIdentifier == 'papaya':
                path = 'Apollo_Papaya_LS_' + str(key) + '\Texture2D_%d.tga'
        

        asset_path = os.path.join(umodel_heightmap_path, path)
        extract_tiles(asset_path, offset_lookup[key], height_composite, normal_composite, str(key))


if mapIdentifier == 'apollo':
        map_size_info  = ['2.048k'][0]
elif mapIdentifier == 'papaya':
        map_size_info  = ['1.024k'][0]

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
