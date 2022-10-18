import json
import xml.etree.ElementTree as ET
from writer.mapniktools import *

DB_PARAMETERS = {
    'type': 'postgis',
    'host': 'localhost',
    'port': '5432',
    'dbname': 'calac',
    'user': 'postgres',
    'password': 'postgres'
}

def get_toponym_field(rule):
    if rule['filter'] is not None:
        return rule['filter']['comparisions'][0]['literal']
    else:
        return None

def create_filter(rule):
    if rule['filter'] is not None:
        if rule['filter']['operator'] is None:
            comp = rule['filter']['comparisions'][0]
            if comp['property'] == 'symbolisat':
                prop = 'symbolisation'
            else:
                prop = comp['property']
            filter = '([' + prop + '] ' + comp['operator'] + ' "' + comp['literal'] + '")'
        else:
            ope = rule['filter']['operator']
            comp = rule['filter']['comparisions']
            filter = ''
            index = 0
            for c in comp:
                if c['property'] == 'symbolisat':
                    prop = 'symbolisation'
                else:
                    prop = c['property']
                if index == 0:
                    value = '([' + prop + '] ' + c['operator'] + ' "' + c['literal'] + '")'
                else:
                    value = " " + ope + ' ([' + prop + '] ' + c['operator'] + ' "' + c['literal'] + '")'
                filter += value
                index += 1
        return filter
    else:
        return None

def create_symbolizer(element, rule):
    def populate_css_symbolizer(symbolizer, type, element, tag):
        if type in symbolizer:
            if tag == 'PointSymbolizer' or tag == 'PolygonPatternSymbolizer' or tag == 'LinePatternSymbolizer':
                if symbolizer[type]:
                    ET.SubElement(element, tag, symbolizer[type])
            else:
                for s in symbolizer[type]:
                    if s:
                        ET.SubElement(element, tag, s)

    sym = rule['symbolizer']
    if sym:
        type = sym['type']
        if type == 'line':
            populate_css_symbolizer(sym, 'stroke', element, 'LineSymbolizer')
            populate_css_symbolizer(sym, 'graphicstroke', element, 'LinePatternSymbolizer')
        elif type == 'polygon':
            populate_css_symbolizer(sym, 'stroke', element, 'LineSymbolizer')
            populate_css_symbolizer(sym, 'fill', element, 'PolygonSymbolizer')
            populate_css_symbolizer(sym, 'graphicfill', element, 'PolygonPatternSymbolizer')

        elif type == 'marker':
            populate_css_symbolizer(sym, 'object', element, 'PointSymbolizer')
        elif sym['type'] == 'point':
            populate_css_symbolizer(sym, 'object', element, 'MarkerSymbolizer')

def create_mapnik_xml(json_files):
    result = {}
    srs = '+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
    for json_file in json_files:
        map = ET.Element('Map')
        map.attrib['srs'] = srs
        toponyms = []
        for file in json_files[json_file]:
            file_content = file[0]
            for f in file_content:
                style = ET.SubElement(map, 'Style')
                style.attrib['name'] = f['Name']
                if f['Name'] != 'emprise':
                    for feature_style in f['UserStyle']['FeatureTypeStyle']:
                        for r in feature_style['Rules']:
                            if 'symbolizer' in r:
                                rule = ET.SubElement(style, 'Rule')
                                add_subelement_if_exists(rule, 'MinScaleDenominator', r['MinScaleDenominator'])
                                add_subelement_if_exists(rule, 'MaxScaleDenominator', r['MaxScaleDenominator'])
                                filter = create_filter(r)
                                add_subelement_if_exists(rule, 'Filter', filter)
                                create_symbolizer(rule, r)
                                if f['Name'] == 'toponyme_droit_25':
                                    toponyms.append(get_toponym_field(r))
                    layer = ET.SubElement(map, 'Layer')
                    layer.attrib['name'] = f['Name']
                    layer.attrib['srs'] = srs
                    stylename = ET.SubElement(layer, 'StyleName')
                    stylename.text = f['Name']
                    datasource = ET.SubElement(layer, 'Datasource')
                    for p in DB_PARAMETERS:
                        parameter = ET.SubElement(datasource, 'Parameter')
                        parameter.attrib['name'] = p
                        parameter.text = DB_PARAMETERS[p]
                    
                    table = f['Name']
                    if table == 'limite_administrative_decal_25':
                        l = 'limite_adm_decale_25'
                    elif table == 'reservoir_surfacique_25':
                        l = 'reservoir_surf_25'
                    elif table == 'reservoir_ponctuel_25':
                        l = 'reservoir_ponct_25'
                    else:
                        l = table
                    tableparam = ET.SubElement(datasource, 'Parameter')
                    tableparam.attrib['name'] = 'table'
                    tableparam.text = l
        # print(ET.tostring(map))
        if len(toponyms) > 0:
            json_object = json.dumps(toponyms, indent = 4)
            with open("toponyms.json", "w") as outfile:
                outfile.write(json_object)
        result[json_file] = map
    return result