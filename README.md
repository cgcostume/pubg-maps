# PUBG & Fortnite | Terrain Maps

*PlayerUnknown's Battlegrounds* currently features seven maps: Erangel, Erangel Classic, Miramar, Sanhok, Vikendi, Karakin, and Camp Jackal. This repository provides information and scripts for extracting elevation and normal maps from the game's sources. 

Please note that all preview images are downscaled to 8-bit 512px &times; 512px and should not be used for rendering (normal data is downsampled using bicubic resampling).

| Erangel Height Map | Erangel Normal Map |
|--------------------|--------------------|
| ![PUBG - Erangel elevation preview](https://github.com/cgcostume/pubg-maps/blob/master/erangel/pubg_erangel_height_l16_preview.png) | ![PUBG - Erangel normal preview](https://github.com/cgcostume/pubg-maps/blob/master/erangel/pubg_erangel_normal_rg8_preview.png) |

| Erangel Classic Height Map | Erangel Classic Normal Map |
|----------------------------|----------------------------|
| ![PUBG - Erangel Classic elevation preview](https://github.com/cgcostume/pubg-maps/blob/master/erangelclassic/pubg_erangelclassic_height_l16_preview.png) | ![PUBG - Erangel Classic normal preview](https://github.com/cgcostume/pubg-maps/blob/master/erangelclassic/pubg_erangelclassic_normal_rg8_preview.png) |

| Miramar Height Map | Miramar Normal Map |
|--------------------|--------------------|
| ![PUBG - Miramar elevation preview](https://github.com/cgcostume/pubg-maps/blob/master/miramar/pubg_miramar_height_l16_preview.png) | ![PUBG - Miramar normal preview](https://github.com/cgcostume/pubg-maps/blob/master/miramar/pubg_miramar_normal_rg8_preview.png) |

| Sanhok Height Map | Sanhok Normal Map |
|-------------------|-------------------|
| ![PUBG - Sanhok elevation preview](https://github.com/cgcostume/pubg-maps/blob/master/sanhok/pubg_sanhok_height_l16_preview.png) | ![PUBG - Sanhok normal preview](https://github.com/cgcostume/pubg-maps/blob/master/sanhok/pubg_sanhok_normal_rg8_preview.png) |

| Vikendi Height Map | Vikendi Normal Map |
|--------------------|--------------------|
| ![PUBG - Vikendi elevation preview](https://github.com/cgcostume/pubg-maps/blob/master/vikendi/pubg_vikendi_height_l16_preview.png) | ![PUBG - Vikendi normal preview](https://github.com/cgcostume/pubg-maps/blob/master/vikendi/pubg_vikendi_normal_rg8_preview.png) |

| Karakin Height Map | Karakin Normal Map |
|--------------------|--------------------|
| ![PUBG - Karakin elevation preview](https://github.com/cgcostume/pubg-maps/blob/master/karakin/pubg_karakin_height_l16_preview.png) | ![PUBG - Karakin normal preview](https://github.com/cgcostume/pubg-maps/blob/master/karakin/pubg_karakin_normal_rg8_preview.png) |

| Camp Jackal Height Map | Camp Jackal Normal Map |
|------------------------|------------------------|
| ![PUBG - Camp Jackal elevation preview](https://github.com/cgcostume/pubg-maps/blob/master/jackal/pubg_jackal_height_l16_preview.png) | ![PUBG - Camp Jackal normal preview](https://github.com/cgcostume/pubg-maps/blob/master/jackal/pubg_jackal_normal_rg8_preview.png) |

| Taego Height Map | Taego Normal Map |
|------------------------|------------------------|
| ![PUBG - Taego elevation preview](https://github.com/cgcostume/pubg-maps/blob/master/taego/pubg_taego_height_l16_preview.png) | ![PUBG - Taego normal preview](https://github.com/cgcostume/pubg-maps/blob/master/taego/pubg_taego_normal_rg8_preview.png) |


#### Fortnite

| Apollo Height Map | Apollo Normal Map |
|-------------------|-------------------|
| ![Fortnite - Apollo elevation preview](https://github.com/cgcostume/pubg-maps/blob/master/apollo/fortnite_apollo_height_l16_preview.png) | ![Fortnite - Apollo normal preview](https://github.com/cgcostume/pubg-maps/blob/master/apollo/fortnite_apollo_normal_rg8_preview.png) |

| Papaya Height Map | Papaya Normal Map |
|-------------------|-------------------|
| ![Fortnite - Papaya elevation preview](https://github.com/cgcostume/pubg-maps/blob/master/papaya/fortnite_papaya_height_l16_preview.png) | ![Fortnite - Papaya normal preview](https://github.com/cgcostume/pubg-maps/blob/master/papaya/fortnite_papaya_normal_rg8_preview.png) |

Please note that the *Fortnite* map should be rotated by 90° counter clockwise (and the normals converted accordingly).


## How-To/DIY

Please note that the following steps might change with respect to the *PUBG* version, asset provisioning, and structure.

1. **Download** [UE Viewer by Gildor](https://www.gildor.org/en/projects/umodel) (`umodel.exe`).
2. **Locate** your *PUBG* directory, e.g., `C:\Program Files (x86)\Steam\steamapps\common\PUBG`.
3. **Open** your *PUBG* directory in UE Viewer, overriding game detection to 'Unreal engine 4.16'. Please note that the PAK files are AES encrypted (try Googling for the AES key, e.g., on Reddit or Gildor's forums).
4. **Filter** for `HeightMap` or `Texture2D_` (optional step)
5. **Export** all heightmaps. This should create a `UmodelExport\Game\Maps\Baltic\Art\HeightMap` (Erangel), `UmodelExport\Game\Maps\Erangel\Art\Heightmap` (Erangel Classic), `UmodelExport\Game\Maps\Desert\Art\Heightmap` (Miramar), `UmodelExport\Game\Maps\Savage\Art\Heightmap` (Sanhok), `UmodelExport\Game\Maps\DihorOtok\Art\Heightmap` (Vikendi), `UmodelExport\Game\Maps\Summerland\Art\HeightMap` (Karakin), or `UmodelExport\Game\Maps\Range\Art\Heightmap` (Camp Jackal) folder in your current working directory.
6. **Run** `pubg-tga-slice.py` for extracting and encoding the relevant tile data into lossless 16-bit and 8-bit pngs:
```
.\pubg-tga-slice.py -p .\UmodelExport\ -m erangel
.\pubg-tga-slice.py -p .\UmodelExport\ -m erangelclassic
.\pubg-tga-slice.py -p .\UmodelExport\ -m miramar
.\pubg-tga-slice.py -p .\UmodelExport\ -m sanhok
.\pubg-tga-slice.py -p .\UmodelExport\ -m vikendi
.\pubg-tga-slice.py -p .\UmodelExport\ -m jackal
.\pubg-tga-slice.py -p .\UmodelExport\ -m taego
```
...or for *Fortnite* extraction:
```
.\fortnite-tga-slice.py -p .\UmodelExport\ -m apollo
.\fortnite-tga-slice.py -p .\UmodelExport\ -m papaya
.\fortnite-tga-slice-athena.py -p .\UmodelExport\ -m athena
```
That's it. If the script exits without errors there should be lossless height and normal maps in the current working directory.


## How-To/DIY | DEPRECATED (ubulk approach)

Please note that the following steps might change with respect to the PUBG version, asset provisioning and structure.

1. **Download** the UE4 pak-file Unpacker by Haoose v0.5 (`ue4pakunpacker.exe`) - google for it, the sha256 hash of my file (latest) is (`925565C55FF849BFAF6D1702BB69958D36325126099B4953384B772601CEB913`) and it seems to be legit.
2. **Locate** your PUBG directory, e.g., `C:\Program Files (x86)\Steam\steamapps\common\PUBG`.
3. **Unpack** `TslGame-WindowsNoEditor_erangel_heightmap.pak` or `TslGame-WindowsNoEditor_desert_heightmap.pak` for Erangel or Miramar respectively. This should create a `TslGame` folder directly in `C:`, i.e., `C:\TslGame\Content\Maps\Erangel\Art\Heightmap` or `C:\TslGame\Content\Maps\Desert\Art\Heightmap` respectively comprising all resources required.

I tried to run steps 1. to 3. via a script as well but couldn't settle on how to provide and handle ue4pakunpacker yet. Feel free to have a look in `pubg-pak-unpack.py`. The following script requires the pip packages: `numpy`, `pypng`, and `Pillow`.

4. **Run** `pubg-ubulk-slice.py` for extracting and encoding the relevant tile data into losless 16bit and 8bit pngs:
```
.\pubg-ubulk-slice.py --map erangel -tsl C:\TslGame --lod 0
.\pubg-ubulk-slice.py --map miramar -tsl C:\TslGame --lod 0
```
That's it. If the script exits without errors there shoud be 8192px &times; 8192px losless height and normal maps. The `--lod` parameter can be used for level of detail of `--lod 0` (8k map), `--lod 1` (4k map), and `--lod 2` (2k map).


#### Details on the Map Encoding

Elevation and normals are packed into 512px &times; 512px &times; 32bit tiles. The first byte and the fourth byte are the 8bit coefficients of the normal. The second and third bytes encode a 16bit elevation/height. Moreover, every `.ubulk` tile file encodes the 512px &times; 512px tile as well as additional downscaled variations (mipmaps), probably LOD1 and LOD2. The binary size of each tile file accumulates to: 512px [width] &times; 512px [height] &times; 4bytes [1byte per channel] &times; (1 [lod0] + 0.25 [lod1] + 0.0625 [lod2]) = 1376256bytes = 1.31MiB

The following paragraphs enumerate the relevant tiles: the first two indices identify the `Heightmap_x#_y#_sharedAssets` group/directory, the following array contains the indices of tiles with normal/elevation data encoded.
