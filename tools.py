from matplotlib.patches import Polygon
from PIL import ImageFont
from mapnik import register_fonts, FontEngine
from shapely.geometry import Polygon
import json
import psycopg2 as pg
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# Dummy tool to display available fonts
fonts = 'fonts/'
register_fonts(fonts)
for face in FontEngine.face_names():
    # print(face)
    pass

# Dict to link font name to their respective files
FONTS_CORRELATION = {
    'DejaVu Sans Book': 'DejaVuSans.ttf',
    'DejaVu Sans Oblique': 'DejaVuSans-Oblique.ttf',
    'DejaVu Sans Bold': 'DejaVuSans-Bold.ttf',
    'DejaVu Sans Bold Oblique': 'DejaVuSans-BoldOblique.ttf',
    'DejaVu Sans Condensed': 'DejaVuSansCondensed.ttf',
    'DejaVu Sans Condensed Oblique': 'DejaVuSansCondensed-Oblique.ttf',
    'DejaVu Sans Condensed Bold': 'DejaVuSansCondensed-Bold.ttf',
    'DejaVu Sans Condensed Bold Oblique': 'DejaVuSansCondensed-BoldOblique.ttf',
    'DejaVu Sans ExtraLight': 'DejaVuSans-ExtraLight.ttf',
    'Formata Regular': 'formata-regular.otf',
    'Formata Condensed': 'formata-condensed.otf',
    'Formata Bold Condensed': 'formata-boldcondensed.otf',
    'Formata Condensed Italic': 'formata-condenseditalic.otf',
    'Calibri Regular': 'Calibri Regular.ttf',
    'Calibri Bold': 'Calibri Bold.ttf',
    'Calibri Italic': 'Calibri Italic.ttf',
    'Calibri Bold Italic': 'Calibri Bold Italic.ttf',
    'Harrington Regular': 'HARNGTON.TTF',
    'Viner Hand ITC Regular': 'VINERITC.TTF',
    'Stencil Regular': 'STENCIL.TTF',
    'Kristen ITC Regular': 'ITCKRIST.TTF',
    'Goudy Stout Regular': 'GOUDYSTO.TTF'
}

SYMBOLIZATION_RULES = {
    'classic': {
        'all' : {
            'placement': 'point',
            'allow-overlap': 'true',
            'label-position-tolerance': '0',
        },
        'main-cities': {
            'face-name': 'Formata Condensed',
            'size': '22',
            'fill': 'black',
            'halo-fill': 'white',
            'halo-radius': '2'
        },
        'minor-cities': {
            'face-name': 'Formata Condensed',
            'size': '14',
            'fill': 'black',
            'halo-fill': 'white',
            'halo-radius': '1.5'
        },
        'roads': {
            'face-name': 'Formata Regular',
            'size': '12',
            'fill': 'black',
            'halo-fill': 'white',
            'halo-radius': '1.5'
        },
        'roads-name': {
            'face-name': 'Formata Condensed',
            'size': '14',
            'fill': 'black',
            'halo-fill': 'white',
            'halo-radius': '1.5'
        },
        'amenity': {
            'face-name': 'Formata Condensed Italic',
            'size': '14',
            'fill': 'black',
            'halo-fill': 'white',
            'halo-radius': '1.5'
        },
        'elevation': {
            'face-name': 'Formata Condensed',
            'size': '14',
            'fill': '#997d54',
        }
    },
    'standard': {
        'all' : {
            'placement': 'point',
            'allow-overlap': 'true',
            'label-position-tolerance': '0',
        },
        'main-cities': {
            'face-name': 'Formata Condensed',
            'size': '22',
            'fill': 'black',
            'halo-fill': 'white',
            'halo-radius': '2'
        },
        'minor-cities': {
            'face-name': 'Formata Condensed',
            'size': '14',
            'fill': 'black',
            'halo-fill': 'white',
            'halo-radius': '1.5'
        },
        'roads': {
            'face-name': 'Formata Regular',
            'size': '12',
            'fill': 'black',
            'halo-fill': 'white',
            'halo-radius': '1.5'
        },
        'roads-name': {
            'face-name': 'Formata Condensed',
            'size': '14',
            'fill': 'black',
            'halo-fill': 'white',
            'halo-radius': '1.5'
        },
        'amenity': {
            'face-name': 'Formata Condensed Italic',
            'size': '14',
            'fill': 'black',
            'halo-fill': 'white',
            'halo-radius': '1.5'
        },
        'elevation': {
            'face-name': 'Formata Condensed',
            'size': '14',
            'fill': '#997d54',
        }
    },
    'google': {
        'all' : {
            'placement': 'point',
            'allow-overlap': 'true',
            'label-position-tolerance': '0',
        },
        'main-cities': {
            'face-name': 'Calibri Bold',
            'size': '22',
            'fill': '#897B5A',
            'halo-fill': 'white',
            'halo-radius': '2'
        },
        'minor-cities': {
            'face-name': 'Calibri Bold Italic',
            'size': '14',
            'fill': '#897B5A',
            'halo-fill': 'white',
            'halo-radius': '1.5'
        },
        'roads': {
            'face-name': 'Formata Regular',
            'size': '12',
            'fill': 'black',
            'halo-fill': '#FFDB34',
            'halo-radius': '2'
        }
    },
    'openstreetmap': {
        'all' : {
            'placement': 'point',
            'allow-overlap': 'true',
            'label-position-tolerance': '0',
        },
        'main-cities': {
            'face-name': 'Calibri Bold',
            'size': '22',
            'fill': '#7F7F7F',
            'halo-fill': 'white',
            'halo-radius': '2'
        },
        'minor-cities': {
            'face-name': 'Calibri Italic',
            'size': '14',
            'fill': '#7F7F7F',
            'halo-fill': 'white',
            'halo-radius': '1.5'
        },
        'roads': {
            'face-name': 'Formata Regular',
            'size': '12',
            'fill': 'white',
            'halo-fill': '#BA7B7E',
            'halo-radius': '2'
        },
        'elevation': {
            'face-name': 'Formata Condensed',
            'size': '14',
            'fill': '#997d54',
        }
    }
}

SYMBOLIZATION = {
    'main-cities': ['100', '101', '102'],
    'minor-cities': ['110', '111', '112', '113', '114', '210', '220', '221', '222', '230', '231', '232', '233', '234', '340', '341', '342', '350', '351', '352', '353', '354', '355', '440', '441', '442', '450', '451', '452', '453', '454', '455', '220_LD', '221_LD', '222_LD', '230_LD', '231_LD', '232_LD', '233_LD', '234_LD'],
    'roads-name': ['NOM_CABLE', 'NOM_CHEMIN', 'NOM_ROUTE'],
    'roads': ['NUM_AUTOROUTE', 'NUM_ROUTE'],
    'amenity': ['DES', 'DET', 'DETB', 'DETBF', 'TOT', 'TOTB', 'TOTBF'],
    'elevation': ['COTE', 'COURBE', 'COURBE_GLACIER', 'COURBE_ROCHER', 'COURBE_BATHY'],
}

MARKER_SYMBOLIZER = {
    'allow-overlap': 'true',
    'fill': 'black',
    'stroke': 'white',
    'stroke-width': '1.5',
    'width': '5',
    'height': '5',
    'placement': 'point',
}

DB_PARAMETERS = """
    host=localhost
    port=5432
    dbname=embrun
    user=postgres
    password=postgres
"""

def get_symbolization_rule(symbolisation, basemap):
    category = ''
    for s in SYMBOLIZATION:
        for value in SYMBOLIZATION[s]:
            if symbolisation == value:
                category = s
    return {**SYMBOLIZATION_RULES[basemap]['all'], **SYMBOLIZATION_RULES[basemap][category]}


def calculate_text_extent(font, size, value):
    font = ImageFont.truetype(font, int(size))
    #font = ImageFont.FreeTypeFont(font, int(size))
    size = font.getsize(value)
    return size

def get_full_extent(tiles):
    xmin = tiles[0]['extent'][0]
    ymin = tiles[0]['extent'][1]
    xmax = tiles[0]['extent'][2]
    ymax = tiles[0]['extent'][3]
    marginx = (xmax - xmin)/3
    marginy = (ymax - ymin)/3
    for tile in tiles:
        x1 = tile['extent'][0]
        y1 = tile['extent'][1]
        x2 = tile['extent'][2]
        y2 = tile['extent'][3]
        if x1 < xmin:
            xmin = x1
        if y1 < ymin:
            ymin = y1
        if x2 > xmax:
            xmax = x2
        if y2 > ymax:
            ymax = y2
    return [xmin - marginx, ymin - marginy, xmax + marginx, ymax + marginy]

def create_geojson_header(name, epsg):
    return {
        'type': 'FeatureCollection',
        'name': name,
        'crs': {
            'type': 'name',
            'properties': {
                'name': epsg
            }
        }
    }

def create_rectangle(xmin, ymin, xmax, ymax, properties):
    return {
        'type': 'Feature',
        'properties': properties,
        'geometry': {
            'type': 'Polygon',
            'coordinates': [[
                [xmin, ymin],
                [xmax, ymin],
                [xmax, ymax],
                [xmin, ymax],
                [xmin, ymin]
            ]]
        }
    }

def generate_tiles(tiles, name):
    features = []
    polygons = []
    for tile in tiles:
        xmin = tile['extent'][0]
        xmax = tile['extent'][2]
        ymin = tile['extent'][1]
        ymax = tile['extent'][3]
        polygons.append({
            'name': str(tile['col']) + 'x' + str(tile['row']),
            'col': tile['col'],
            'row': tile['row'],
            'xmin': xmin,
            'ymin': ymin,
            'xmax': xmax,
            'ymax': ymax,
            'geometry': Polygon([(xmin, ymin),(xmax, ymin),(xmax, ymax),(xmin, ymax),(xmin, ymin)])
        })
        properties = {
            'name': str(tile['col']) + 'x' + str(tile['row']),
            'col': tile['col'],
            'row': tile['row'],
            'xmin': xmin,
            'ymin': ymin,
            'xmax': xmax,
            'ymax': ymax
        }
        features.append(create_rectangle(xmin, ymin, xmax, ymax, properties))
    geojson = create_geojson_header('tiles-extent', 'epsg:2154')
    geojson['features'] = features
    json_object = json.dumps(geojson, indent = 4)
    with open("output/" + name + "_tiles-extents.geojson", "w") as outfile:
        outfile.write(json_object)
    return polygons

def tile_exists(tiles, row, col):
    exists = False
    for tile in tiles:
        if tile['row'] == row and tile['col'] == col:
            exists = True
    return exists

def generate_labels(dataset, tiles, scale, basemap):
    polygons = []
    for data in dataset:
        name = data[0]
        symbolisation = data[1]
        x = data[2]
        y = data[3]
        rule = get_symbolization_rule(symbolisation, basemap)
        px = calculate_text_extent('fonts/' + FONTS_CORRELATION[rule['face-name']], rule['size'], name)
        w = (((px[0] + 5)/2)*0.00028*scale)
        h = (((px[1] + 5)/2)*0.00028*scale)
        xmin = x - w
        xmax = x + w
        ymin = y - h
        ymax = y + h
        col = row = None
        for tile in tiles:
            x1 = tile['extent'][0]
            x2 = tile['extent'][2]
            y1 = tile['extent'][1]
            y2 = tile['extent'][3]
            if x > x1 and x < x2 and y > y1 and y < y2:
                col = tile['col']
                row = tile['row']
        if (col != None and row != None):
            polygons.append({
                'name': name,
                'col': col,
                'row': row,
                'xmin': xmin,
                'ymin': ymin,
                'xmax': xmax,
                'ymax': ymax,
                'geometry': Polygon([(xmin, ymin),(xmax, ymin),(xmax, ymax),(xmin, ymax),(xmin, ymin)])
            })
    return polygons

def construct_labels_csv(tiles, polygons, params, basemap):
    def x_to_px(x1, x2, scale):
        return str(round((x1 - x2)/scale/0.00028))

    def y_to_px(y1, y2, height, scale):
        return str(height - round((y1 - y2)/scale/0.00028))

    t = {}
    for tile in tiles:
        if tile['col'] in t.keys():
            t[tile['col']][tile['row']] = tile
        else:
            t[tile['col']] = {tile['row']: tile}
    for polygon in polygons:
        col = polygon['col']
        row = polygon['row']
        tile = t[col][row]
        xminpx = x_to_px(polygon['xmin'], tile['xmin'], params['scale'])
        yminpx = y_to_px(polygon['ymin'], tile['ymin'], params['height'], params['scale'])
        xmaxpx = x_to_px(polygon['xmax'], tile['xmin'], params['scale'])
        ymaxpx = y_to_px(polygon['ymax'], tile['ymin'], params['height'], params['scale'])
        name = polygon['name']
        if 'value' in t[col][row]:
            t[col][row]['value'] += "\n" + xminpx + ',' + yminpx + ',' + xmaxpx + ',' + yminpx + ',' + xmaxpx + ',' + ymaxpx + ',' + xminpx + ',' + ymaxpx + ',' + name
        else:
            t[col][row]['value'] = xminpx + ',' + yminpx + ',' + xmaxpx + ',' + yminpx + ',' + xmaxpx + ',' + ymaxpx + ',' + xminpx + ',' + ymaxpx + ',' + name
    
    for col in t:
        for row in t[col]:
            if 'value' in t[col][row]:
                text = t[col][row]['value']
            else:
                text = ''
            with open('output/labels/' + basemap + '_' + str(col) + '_' + str(row) + '.txt', 'w') as outfile:
                outfile.write(text)

def construct_labels_geojson(polygons, name):
    geojson = create_geojson_header('labels-extent', 'epsg:2154')
    features = []
    for polygon in polygons:
        properties = {
            'name': polygon['name'],
            'col': polygon['col'],
            'row': polygon['row'],
            'xmin': polygon['xmin'],
            'ymin': polygon['ymin'],
            'xmax': polygon['xmax'],
            'ymax': polygon['ymax'],
        }
        features.append(create_rectangle(polygon['xmin'], polygon['ymin'], polygon['xmax'], polygon['ymax'], properties))
    geojson['features'] = features
    json_object = json.dumps(geojson, indent = 4)
    with open("output/" + name + "_labels-extents.geojson", "w") as outfile:
        outfile.write(json_object)

def get_polygon_coordinates(polygon):
    polypoints = list(polygon.exterior.coords)
    xs = []
    ys = []
    for point in polypoints:
        xs.append(point[0])
        ys.append(point[1])
    return {
        'xmin': min(xs),
        'ymin': min(ys),
        'xmax': max(xs),
        'ymax': max(ys)
    }

def intersection(labels, tiles):
    clip = []
    for label in labels:
        for tile in tiles:
            l_geom = label['geometry']
            t_geom = tile['geometry']
            if l_geom.intersects(t_geom):
                intersect = l_geom.intersection(t_geom)
                if intersect.geom_type == 'Polygon':
                    coordinates = get_polygon_coordinates(intersect)
                    clip.append({
                        'name': label['name'],
                        'col': tile['col'],
                        'row': tile['row'],
                        'xmin': coordinates['xmin'],
                        'ymin': coordinates['ymin'],
                        'xmax': coordinates['xmax'],
                        'ymax': coordinates['ymax'],
                        'geometry': intersect
                    })
    return clip

def clear_string_between_char(str, char1, char2):
    result = ''
    keep = True
    for ch in str:
        if ch == char1:
            keep = False
        elif ch == char2:
            keep = True
            continue
        if keep:
            result += ch
    return result

def get_direct_elements_by_tag(element, tag_name):
    elements = []
    for e in element:
        if clear_string_between_char(e.tag, '{', '}') == tag_name:
            elements.append(e)
    return elements

def add_subelement_if_exists(parent, tag, value):
    if value is not None:
        child = ET.SubElement(parent, tag)
        child.text = value

def add_subelement_with_attrib(parent, tag, attrib):
    if attrib is not None:
        child = ET.SubElement(parent, tag)
        child.attrib = attrib

def add_toponyms_to_xml(xml, basemap):
    str = " ".join(xml.read().split())
    layers = ET.fromstring(str)
    styles = get_direct_elements_by_tag(layers, 'Style')
    for style in styles:
        if style.attrib['name'] == 'toponyme_droit_25':
            toponyms = []
            rules = get_direct_elements_by_tag(style, 'Rule')
            for rule in rules:
                filter = get_direct_elements_by_tag(rule, 'Filter')[0]
                symbolisation = filter.text.split("\"")[1]
                toponyms.append(symbolisation)
                symbo_rule = get_symbolization_rule(symbolisation, basemap)
                symbolizer = ET.SubElement(rule, 'TextSymbolizer', symbo_rule)
                symbolizer.text = '[ref_ecriture]'
                #point = ET.SubElement(rule, 'MarkersSymbolizer', MARKER_SYMBOLIZER)
        else:
            toponyms = None
    return [layers, toponyms]

def create_label_extent(toponyms, params, basemap):
    symbo = '('
    index = 0
    for topo in toponyms:
        symbo += "'" + topo + "'"
        if index + 1 < len(toponyms):
            symbo += ", "
        else:
            symbo += ")"
        index += 1

    extent = get_full_extent(params['tiles'])
    con = pg.connect(DB_PARAMETERS)
    cur = con.cursor()
    query = """
        SELECT ref_ecriture as name, symbolisation, ST_X(geometrie) as x, ST_Y(geometrie) as y
        FROM toponyme_droit_25
        WHERE (symbolisation in %s) AND (placement_ok = 'true') AND (ST_X(geometrie) BETWEEN %f AND %f) AND (ST_Y(geometrie) BETWEEN %f AND %f)
    """%(symbo, extent[0], extent[2], extent[1], extent[3])
    cur.execute(query)
    data = cur.fetchall()
    labels = generate_labels(data, params['tiles'], params['scale'], basemap)
    tiles = generate_tiles(params['tiles'], basemap)
    if (len(labels) > 0):
        clipped = intersection(labels, tiles)
        construct_labels_geojson(clipped, basemap)
        construct_labels_csv(tiles, clipped, params, basemap)