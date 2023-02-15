import mapnik, math, argparse, json, os
from pathlib import Path
from tools import *

# calac
# 'xmin': 350847,
# 'ymin': 6236028,
# 'xmax': 453610,
# 'ymax': 6278783,
# bretagne_st_jean
# 'xmin': 240324,
# 'ymin': 6725813,
# 'xmax': 279653,
# 'ymax': 6759683,
# embrun 
# 'xmin': 960000,
# 'ymin': 6360000,
# 'xmax': 1016737,
# 'ymax': 6400000,

# Creation of the map
def create_map(params):
    # Definition of parameters
    par = {
        'xmin': 960000,
        'ymin': 6360000,
        'xmax': 1016737,
        'ymax': 6400000,
        'pixel_size': 0.00028,
        'scale': params.scale_denominator,
        'width': params.width,
        'height': params.height,
        'style': params.style.replace(' ', '').split(',')
    }

    def calculate_tiles(row, col, params):
        # Calculate the size of a tile depending on the pixel size, the scale and the size of one pixel
        height_meters = params['scale']*(params['height']*params['pixel_size'])
        width_meters = params['scale']*(params['width']*params['pixel_size'])

        # This list will contain every tiles generated
        tiles = []
        col_num = 0
        while col_num < col:
            row_num = 0
            while row_num < row:
                # Calculate the bounding box of the tile
                x1 = params['xmin'] + col_num*(width_meters)
                x2 = x1 + (width_meters)
                y1 = params['ymin'] + row_num*(height_meters)
                y2 = y1 + (height_meters)

                # Create a dict with informations about the tile
                tile = {
                    'col': col_num + 1,
                    'row': row_num + 1,
                    'extent': [x1, y1, x2, y2]
                }

                # Append the dict to the list of tiles
                tiles.append(tile)
                
                row_num += 1
            col_num += 1
        return tiles

    def generate_tiles(map, tiles, name):
        for tile in tiles:
            e = tile['extent']
            extent_map = mapnik.Box2d(e[0], e[1], e[2], e[3])
            map.zoom_to_box(extent_map)
            mapnik.render_to_file(map, 'output/images/' + name + '_' + str(tile['col']) + '_' + str(tile['row']) + '.png', 'png')

    col = math.ceil(abs(par['xmax'] - par['xmin']) / (par['scale']*(par['width']*par['pixel_size'])))
    row = math.ceil(abs(par['ymax'] - par['ymin']) / (par['scale']*(par['height']*par['pixel_size'])))

    style_location = 'translator/styles/'
    xml_location =  style_location + 'xml_raw/'

    for style in par['style']:
        name = style
        file = name + '.xml'
        print('creating ' + str(col) + 'x' + str(row) + ' map tiles for ' + name)
        tiles = calculate_tiles(row, col, par)
        par['tiles'] = tiles

        with open(xml_location + file, 'r') as f:
            topo = add_toponyms_to_xml(f, name)
            layers = topo[0]
            if topo[1] is not None:
                toponyms = topo[1]
            # tree = ET.ElementTree(layers)
            # output = open(style_location + 'xml/' + file, "wb")
            # string = ET.tostring(tree.getroot(), 'utf-8')
            # output.write(minidom.parseString(string).toprettyxml(indent="    ", encoding="utf-8"))
            # output.close()

        map = mapnik.Map(par['width'], par['height'], '+init=epsg:2154')
        map.background = mapnik.Color('white')
        map.buffer_size = int(round(max([par['width'], par['height']])/3))
        mapnik.load_map(map, style_location + 'xml/' + file)

        create_label_extent(toponyms, par, name)

        ####################################
        # l = mapnik.Layer('extents')
        # l.datasource = mapnik.GeoJSON(file='output/' + name + '_labels-extents.geojson')
        # l.srsfor file in os.listdir(xml_location):
        # name = file.rsplit('.', 1)[0]
        # print('creating ' + str(col) + 'x' + str(row) + ' map tiles for ' + name)
        # tiles = calculate_tiles(row, col, par)
        # par['tiles'] = tiles

        # with open(xml_location + file, 'r') as f:
        #     topo = add_toponyms_to_xml(f, name)
        #     layers = topo[0]
        #     if topo[1] is not None:
        #         toponyms = topo[1]
        #     tree = ET.ElementTree(layers)
        #     output = open(style_location + 'xml/' + file, "wb")
        #     string = ET.tostring(tree.getroot(), 'utf-8')
        #     output.write(minidom.parseString(string).toprettyxml(indent="    ", encoding="utf-8"))
        #     output.close()

        # map = mapnik.Map(par['width'], par['height'], '+init=epsg:2154')
        # map.background = mapnik.Color('white')
        # map.buffer_size = int(round(max([par['width'], par['height']])/3))
        # mapnik.load_map(map, style_location + 'xml/' + file)

        # create_label_extent(toponyms, par, name)

        ####################################
        # l = mapnik.Layer('extents')
        # l.datasource = mapnik.GeoJSON(file='output/' + name + '_labels-extents.geojson')
        # l.srs = '+init=epsg:2154'

        # polygons = mapnik.PolygonSymbolizer()
        # polygons.fill = mapnik.Color('rgb(0,0,0)')
        # polygons.fill_opacity = 0.5

        # rules = mapnik.Rule()
        # rules.symbols.append(polygons)

        # style = mapnik.Style()
        # style.rules.append(rules)

        # map.append_style('extents', style)
        # l.styles.append('extents')
        # map.layers.append(l)
        ####################################

        generate_tiles(map, tiles, name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate custom map tiles.')
    parser.add_argument('-W', '--width', type=int, default=512, help='width of tiles')
    parser.add_argument('-H', '--height', type=int, default=512, help='height of tiles')
    parser.add_argument('-s', '--scale_denominator', type=int, default=25000, help='output map scale denominator')
    parser.add_argument('-e','--extent', nargs='+', help='full extent of the area of interest. Full data extent is taken if none is provided.')
    parser.add_argument('-I', '--srs_in', type=str, default='epsg:2154', help='SRS of input data')
    parser.add_argument('-O', '--srs_out', type=str, default='epsg:2154', help='SRS of output map')
    parser.add_argument('-S', '--style', type=str, default='standard, classic, google, openstreetmap', help='style of the map to produce (standard, classic, google, openstreetmap) - a comma-separated list of value is possible.')

    params = parser.parse_args()
    create_map(params)