# PlayerUnknown's Battlegrounds | Terrain Maps

PlayerUnknown's Battlegrounds currently features two maps: `Erangel` and `Miramar`. This repository provides information and scripts for extracting elevation and normal maps from the game's sources. In addition, the extracted maps are available as well in full, losless detail.

#### Erangel Elevation/Height Map

Download [8192px x 8192px, 16bit, grayscale, png](https://github.com/cgcostume/pubg-maps/blob/master/erangel/pubg_erangel_elevation_l16.png)

![pubg_erangel_elevation_preview](https://github.com/cgcostume/pubg-maps/blob/master/erangel/pubg_erangel_elevation_l16_preview.png)

Please note that the preview image is downscaled to 8bit 512x512 and contrast is enhanced.


#### Erangel Normal Map

Download [8192px x 8192px, 8bit, rgb, png](https://github.com/cgcostume/pubg-maps/blob/master/erangel/pubg_erangel_normal_r8g8.png)

![pubg_erangel_elevation_preview](https://github.com/cgcostume/pubg-maps/blob/master/erangel/pubg_erangel_normal_r8g8_preview.png)

Please note that the preview image is downscaled to 512x512.

#### Miramar Elevation/Height Map

ToDo

#### Miramar Normap Map

ToDo


## How-To/DIY

Please not that the following steps might change with respect to the PUBG version, asset provisioning and structure.

1. **Download** the UE4 pak-file Unpacker by Haoose v0.5 (`ue4pakunpacker.exe`) - google for it, the sha256 hash of my file is (`A00A579504D0594BE15377DB5DE07D916AD5E1047D15AD555B5A109E71219B5E`) and it seems to be legit.
2. **Locate** your PUBG directory, e.g., `C:\Program Files (x86)\Steam\steamapps\common\PUBG`.
3. **Unpack** `TslGame-WindowsNoEditor_erangel_heightmap.pak` or `TslGame-WindowsNoEditor_desert_heightmap.pak` for Erangel or Miramar respectively. This should create a `TslGame` folder directly in `C:`, i.e., `C:\TslGame\Content\Maps\Erangel\Art\Heightmap` or `C:\TslGame\Content\Maps\Desert\Art\Heightmap` respectively comprising all resources required.

I tried to run steps 1. to 3. via a script as well but couldn't settle on how to provide and handle ue4pakunpacker yet. Feel free to have a look in `pubg-pak-unpack.py`. 

4. **Run** `pubg-ubulk-slice.py` for extracting and encoding the relevant tile data into losless 16bit and 8bit pngs.
```
.\pubg-ubulk-slice.py --map erangel -tsl C:\TslGame
```
5. **Run** `


#### Details on the Map Encoding

Elevation and normals are packed into 512px x 512px x 32bit tiles. The first byte and the fourth byte are the 8bit coefficients of the normal. The second and third bytes encode a 16bit elevation/height. Moreover, every `.ubulk` tile file encodes the 512x512 tile as well as additional downscaled variations (mipmaps), probably LOD1 and LOD2 with interleaving rows. The binary size of each tile file accumulates to: 512px [width] x 512px [height] x 4bytes [1byte per channel] x (1 [lod0] + 0.25 [lod1] + 0.0625 [lod2]) = 1376256bytes = 1.31MiB

The following paragraphs enumerate the relevant tiles: the first two indices identify the `Heightmap_x#_y#_sharedAssets` group/directory, the following array contains the indices of tiles with normal/elevation data encoded.

###### Erangel Stitch Indices

The following indices are derived manually and are subject to change based on the actual PUBGs asset structure:

```
ubulk_indices  = [ 
    (0, 0, [0,  1,  2,  3,  4,  5,  6,  7, 10, 19, 30, 36, 37, 38, 39, 40])
  , (0, 1, [0,  1,  2,  3,  4,  5,  6,  7,  9, 19, 30, 36, 40, 43, 44, 45])
  , (0, 2, [0,  1,  2,  3,  4,  5,  6,  7, 10, 18, 26, 37, 48, 50, 51, 52])
  , (0, 3, [0,  1,  2,  3,  4,  5,  6,  7, 11, 18, 19, 20, 21, 22, 23, 24])
  , (1, 0, [0,  1,  2,  3,  4,  5,  6,  7, 11, 21, 30, 36, 38, 39, 40, 41])
  , (1, 1, [0,  1,  2,  3,  4,  5,  6,  7, 10, 19, 27, 36, 47, 54, 57, 58])
  , (1, 2, [0,  1,  2,  3,  4,  5,  6,  7, 11, 20, 27, 36, 47, 55, 61, 62])
  , (1, 3, [0,  1,  2,  3,  4,  5,  6,  7, 11, 18, 26, 28, 29, 30, 31, 32])
  , (2, 0, [0,  1,  2,  3,  4,  5,  6,  7, 12, 20, 29, 38, 41, 42, 43, 44])
  , (2, 1, [0,  1,  2,  3,  4,  5,  6,  7, 10, 21, 22, 27, 34, 42, 50, 59])
  , (2, 2, [0,  1,  2,  3,  4,  8,  9, 10, 15, 20, 31, 37, 45, 50, 52, 54])
  , (2, 3, [0,  1,  2,  3,  4,  5,  6,  7, 10, 19, 27, 35, 39, 40, 41, 42])
  , (3, 0, [0,  1,  2,  3,  4,  5,  6,  7, 10, 18, 28, 33, 34, 35, 36, 37])
  , (3, 1, [0,  1,  2,  3,  4,  5,  6,  7, 10, 19, 28, 34, 35, 36, 37, 38])
  , (3, 2, [0,  1,  2,  3,  4,  5,  6,  7, 12, 19, 24, 30, 38, 42, 47, 48])
  , (3, 3, [0,  1,  2,  3,  4,  5,  6,  7,  9, 18, 19, 20, 21, 22, 23, 24]) ]
  
ubulk_sequence = [ 
      (0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3)
    , (2, 0), (2, 1), (2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3) ]

tile_sequence  = [
      (3, 3), (2, 3), (1, 1), (0, 1), (3, 0), (2, 0), (1, 0), (0, 0)
    , (1, 3), (0, 3), (3, 2), (2, 2), (1, 2), (0, 2), (3, 1), (2, 1) ]
```  

###### Miramar Stitch Indices

The following indices are derived manually and are subject to change based on the actual PUBGs asset structure:

```
ubulk_indices  = [ ]
  
ubulk_sequence = [ ]

tile_sequence  = [ ]
```  
