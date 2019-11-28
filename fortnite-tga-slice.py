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
parser.add_argument('-m', '--map', help = 'map identifier, currently only apollo', default = 'apollo')
# parser.add_argument('-l', '--lod', help = 'level-of-detail, either 0, 1, or 2', default = '0')
parser.add_argument('-c', '--compress', help = 'compression level, number between 0 and 10', default = '0')
parser.add_argument('-t', '--thumbnail', help = 'also generate 512² thumbnails', action = 'store_true')

args = parser.parse_args()

tslHeightmapPathsByMap =  {
        'apollo' : r'Game\Athena\Apollo\Maps\Landscape',
}


mapIdentifier = args.map.lower()
if mapIdentifier not in  { 'apollo' }:
    sys.exit('unknown map identifier \'' + mapIdentifier + '\'')

numTiles = 361 # 10²


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

tile_scale = 19;
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

                # since lobby texture is 512*512
                if texture_key == 'LOBBY':
                    channel_b = numpy.resize(numpy.uint8(), int(512 * 512));
                else:
                    channel_b = numpy.resize(numpy.uint8(), tile_size);
                channel_b.fill(255)

                rgb = numpy.dstack((channel_r, channel_g, channel_b)).flatten()

                # # extract elevation

                channel_l = numpy.left_shift(numpy.asarray(tile_r, numpy.uint16()).flatten(), 8)
                channel_l = channel_l + numpy.asarray(tile_g).flatten()
        
                # refine stitching sequence

                target_x = offset[0] * (tile_width - 1)
                target_y = offset[1] * (tile_height - 1)

                # since lobby texture is 512*512
                if texture_key == 'LOBBY':
                    tile_width = { 0: 512 }[lod]; tile_height = { 0: 512 }[lod];
                    normal_tile = Image.frombytes('RGB', (tile_width, tile_height), rgb).crop((0, 0, 320, 320));
                    height_tile = Image.frombytes('I;16', (tile_width, tile_height), numpy.asarray(channel_l, order = 'C')).crop((0, 0, 320, 320));
                else:
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
    
        'AB12': {
                
                0: (16, 6), 8: (12, 4), 10: (13, 4), 16: (12, 5), 18: (13, 5), 26: (13, 6),
                28: (14, 6), 30: (15, 6), 120: (12, 6),
                 
                },
        
        'AB34': {
                
                0: (8, 3), 2: (9, 3), 4: (10, 3), 6: (11, 3), 8: (8, 4), 10: (9, 4), 12: (10, 4),
                14: (11, 4), 16: (8, 5), 18: (9, 5), 20: (10, 5), 22: (11, 5), 24: (8, 6),
                26: (9, 6), 28: (10, 6),  142: (11, 6), 
                 
                },

        'AB56': {
                
                30: (7, 6), 28: (6, 6), 26: (5, 6), 24: (4, 6), 22: (7, 5), 20: (6, 5), 28: (6, 6),
                2: (5, 3), 18: (5, 5), 16: (4, 5), 14: (7, 4), 12: (6, 4), 10: (5, 4), 6: (7, 3),
                4: (6, 3),
                 
                },

        'AB78': {
                
                20: (2, 5), 30: (3, 6), 28: (2, 6), 26: (1, 6), 22: (3, 5),
                
                },

        'CD12': {
                
                24: (12, 10), 22: (15, 9), 20: (14, 9), 2: (13, 7), 18: (13, 9), 16: (12, 9),
                14: (15, 8), 123: (12, 7), 12: (14, 8), 10: (13, 8), 8: (12, 8), 6: (15, 7),
                4: (14, 7), 30: (15, 10), 28: (14, 10), 24: (12, 10), 26: (13, 10), 
                
                },

        'CD34': {
                
                8: (8, 8), 4: (10, 7), 30: (11, 10), 28: (10, 10), 26: (9, 10), 24: (8, 10),
                22: (11, 9), 20: (10, 9), 2: (9, 7), 18: (9, 9), 16: (8, 9), 14: (11, 8),
                131: (11, 7), 12: (10, 8), 10: (9, 8), 0: (8, 7),
                
                },
        
        'CD56': {
                
                12: (6, 8), 10: (5, 8), 0: (4, 7), 8: (4, 8), 6: (7, 7), 4: (6, 7), 30: (7, 10),
                28: (6, 10), 26: (5, 10), 24: (4, 10), 22: (7, 9), 20: (6, 9), 2: (5, 7),
                18: (5, 9), 16: (4, 9), 14: (7, 8), 
                
                },

        'CD78': {
                
                4: (2, 7), 30: (3, 10), 28: (2, 10), 26: (1, 10), 24: (0, 10), 22: (3, 9),
                20: (2, 9), 2: (1, 7), 18: (1, 9), 16: (0, 9), 14: (3, 8), 12: (2, 8),
                10: (1, 8), 6: (3, 7), 
                
                },

        'EF12': {
                
                18: (12, 11), 16: (12, 12), 14: (12, 13), 12: (12, 14), 10: (13, 14), 0: (15, 11),
                8: (14, 14), 6: (15, 14), 4: (15, 13), 30: (13, 13), 28: (14, 13), 26: (13, 12),
                24: (14, 12), 22: (14, 11), 20: (13, 11), 
                
                },

        'EF34': {
                
                12: (10, 12), 10: (9, 12), 0: (8, 11), 8: (8, 12), 6: (11, 11), 4: (10, 11), 30: (11, 14),
                28: (10, 14), 26: (9, 14), 24: (8, 14), 22: (11, 13), 20: (10, 13), 2: (9, 11),
                18: (9, 13), 16: (8, 13), 14: (11, 12), 
                
                },

        'EF56': {
                
                6: (7, 11), 4: (6, 11), 30: (7, 14), 28: (6, 14), 26: (5, 14), 24: (4, 14), 22: (7, 13),
                20: (6, 13), 2: (5, 11), 18: (5, 13), 16: (4, 13), 14: (7, 12), 12: (6, 12), 10: (5, 12),
                0: (4, 11), 8: (4, 12), 
                
                },

        'EF78': {
                
                12: (2, 12), 10: (1, 12), 0: (0, 11), 8: (0, 12), 6: (3, 11), 4: (2, 11), 30: (3, 14),
                28: (2, 14), 26: (1, 14), 24: (0, 14), 22: (3, 13), 20: (2, 13), 2: (1, 11), 18: (1, 13),
                16: (0, 13), 14: (3, 12), 
                
                },
        
        'GH12': {
                
                10: (13, 15),  0: (15, 16), 8: (14, 15), 6: (15, 15), 30: (14, 16),  28: (13, 16),
                26: (13, 17),  24: (14, 17),  18: (12, 18),  16: (12, 17), 14: (12, 16), 12: (12, 15),     
                
                },

        'GH34': {
                
                12: (10, 16), 10: (9, 16), 0: (8, 15), 8: (8, 16), 6: (11, 15), 4: (10, 15),
                30: (11, 18), 28: (10, 18), 26: (9, 18), 24: (8, 18), 22: (11, 17), 20: (10, 17),
                2: (9, 15), 18: (9, 17), 16: (8, 17), 14: (11, 16), 
                
                },

        'GH56': {
                
                12: (6, 16), 10: (5, 16), 0: (4, 15), 8: (4, 16), 6: (7, 15), 4: (6, 15),
                30: (7, 18), 28: (6, 18), 26: (5, 18), 24: (4, 18), 22: (7, 17), 20: (6, 17),
                2: (5, 15), 18: (5, 17), 16: (4, 17), 14: (7, 16), 
                
                },

        'GH78': {
                
                2: (1, 15), 18: (1, 17), 16: (0, 17), 14: (3, 16), 12: (2, 16), 10: (1, 16),
                0: (0, 15), 8: (0, 16), 6: (3, 15), 4: (2, 15), 30: (3, 18), 28: (2, 18),
                26: (1, 18), 24: (0, 18), 22: (3, 17), 20: (2, 17), 
                
                },

        'LOBBY': {
                
                0: (15, 0),
                
                },

}


if mapIdentifier == 'apollo':
        offset_lookup = apollo_indices

for key in offset_lookup.keys():
        # example '.\UmodelExport\Athena\Apollo\Maps\Landscape\Apollo_Terrain_LS_AB12\Texture2D_0.tga'
        
        if mapIdentifier == 'apollo':
                path = 'Apollo_Terrain_LS_' + str(key) + '\Texture2D_%d.tga'

        asset_path = os.path.join(umodel_heightmap_path, path)
        extract_tiles(asset_path, offset_lookup[key], height_composite, normal_composite, str(key))


map_size_info  = ['2.432k'][0]

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
