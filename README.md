# PlayerUnknown's Battlegrounds | Terrain Maps

PlayerUnknown's Battlegrounds currently features two maps: `Erangel` and `Miramar`. This repository provides information and scripts for extracting elevation and normal maps from the game's sources. In addition, the extracted maps are available as well in full, losless detail.

#### Erangel Elevation/Height Map

Download [8192px x 8192px, 16bit, grayscale, png](https://github.com/cgcostume/pubg-maps/blob/master/erangel/pubg_erangel_height_l16.png)

![pubg_erangel_elevation_preview](https://github.com/cgcostume/pubg-maps/blob/master/erangel/pubg_erangel_height_l16_preview.png)

Please note that the preview image is downscaled to 8bit 512px &times; 512px.


#### Erangel Normal Map

Download [8192px x 8192px, 8bit, rgb, png](https://github.com/cgcostume/pubg-maps/blob/master/erangel/pubg_erangel_normal_rg8.png)

![pubg_erangel_elevation_preview](https://github.com/cgcostume/pubg-maps/blob/master/erangel/pubg_erangel_normal_rg8_preview.png)

Please note that the preview image is downscaled to 512px &times; 512px.

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

4. **Run** `pubg-ubulk-slice.py` for extracting and encoding the relevant tile data into losless 16bit and 8bit pngs:
```
.\pubg-ubulk-slice.py --map erangel -tsl C:\TslGame
.\pubg-ubulk-slice.py --map miramar -tsl C:\TslGame
```

That's it. If the script exits without errors there shoud be 8192px &times; 8192px losless height and normal maps.


#### Details on the Map Encoding

Elevation and normals are packed into 512px &times; 512px &times; 32bit tiles. The first byte and the fourth byte are the 8bit coefficients of the normal. The second and third bytes encode a 16bit elevation/height. Moreover, every `.ubulk` tile file encodes the 512px &times; 512px tile as well as additional downscaled variations (mipmaps), probably LOD1 and LOD2 with interleaving rows. The binary size of each tile file accumulates to: 512px [width] &times; 512px [height] &times; 4bytes [1byte per channel] &times; (1 [lod0] + 0.25 [lod1] + 0.0625 [lod2]) = 1376256bytes = 1.31MiB

The following paragraphs enumerate the relevant tiles: the first two indices identify the `Heightmap_x#_y#_sharedAssets` group/directory, the following array contains the indices of tiles with normal/elevation data encoded.
