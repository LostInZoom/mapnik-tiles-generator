from cv2 import TonemapDrago
from reader.sldtools import *
import os, json, cv2

RULE_ATTRIBUTES = {
    'name': 'Name',
    'title': 'Title',
    'abstract': 'Abstract',
    'MinScaleDenominator': 'MinScaleDenominator',
    'MaxScaleDenominator': 'MaxScaleDenominator'
}

# mapping between SLD attribute names and SVG names
ATTRIBUTE_NAME_MAPPING = {
    'PolygonSymbolizer': {
        'fill': 'fill',
        'fill-opacity': 'fill-opacity',
        'opacity': 'fill-opacity'
    },
    'LineSymbolizer': {
        'stroke': 'stroke',
        'stroke-width': 'stroke-width',
        'width': 'stroke-width',
        'stroke-opacity': 'stroke-opacity',
        'opacity': 'stroke-opacity',
        'stroke-linejoin': 'stroke-linejoin',
        'stroke-linecap': 'stroke-linecap',
        'stroke-dasharray': 'stroke-dasharray',
    }
}

# mapping SLD operators to shortforms
COMPARISION_OPERATOR_MAPPING = {
    'PropertyIsEqualTo': '=',
    'PropertyIsNotEqualTo': '!=',
    'PropertyIsLessThan': '<',
    'PropertyIsGreaterThan': '>',
    'PropertyIsLessThanOrEqualTo': '<=',
    'PropertyIsGreaterThanOrEqualTo': '>=',
    #'PropertyIsNull': 'isNull',
    #'PropertyIsBetween'
    #'PropertyIsLike'
}

def get_marker_scale():
    pass

def resize_polygon_pattern(href, size, scale):
    href_real = '../' + href
    size = "{:.2f}".format(meter_to_pixel(float(size), scale))
    img = cv2.imread(href_real)
    return href


def get_css_value(elements, symbolizer, scale):
    r = []
    for e in elements:
        css_param = get_direct_elements_by_tag(e, 'CssParameter')
        css = {}
        for c in css_param:
            if c.attrib['name'] == 'stroke-dasharray':
                text = parse_dasharray(c.text, scale)
            else:                   
                text = parse_css_value(c.text, scale)
            if c.attrib['name'] in ATTRIBUTE_NAME_MAPPING[symbolizer]:
                css[ATTRIBUTE_NAME_MAPPING[symbolizer][c.attrib['name']]] = text
        r.append(css)
    return r

def get_symbolizer(rule, scale):
    polygon_symbolizer = get_first_element_by_tag(rule, 'PolygonSymbolizer')
    line_symbolizer = get_first_element_by_tag(rule, 'LineSymbolizer')
    point_symbolizer = get_first_element_by_tag(rule, 'PointSymbolizer')

    symbolizer = {}
    if polygon_symbolizer is not None:
        symbolizer['type'] = 'polygon'
        strokes = get_direct_elements_by_tag(polygon_symbolizer, 'Stroke')
        fills = get_direct_elements_by_tag(polygon_symbolizer, 'Fill')
        if len(strokes) > 0:
            symbolizer['stroke'] = get_css_value(strokes, 'LineSymbolizer', scale)
        if len(fills) > 0:
            graphics_fill = get_direct_elements_by_tag(fills[0], 'GraphicFill')
            if len(graphics_fill) > 0:
                href = get_all_elements_by_tag(graphics_fill[0], 'href')[0].text
                if href[:1] == "/":
                    href = href[1:]
                symbolizer['graphicfill'] = {
                    'file': resize_polygon_pattern(href, get_all_elements_by_tag(graphics_fill[0], 'Size')[0].text, scale),
                    # 'type': get_all_elements_by_tag(graphics_fill[0], 'Format')[0].text,
                    # 'height': get_all_elements_by_tag(graphics_fill[0], 'Size')[0].text,
                    # 'width': get_all_elements_by_tag(graphics_fill[0], 'Size')[0].text
                }
            else:
                symbolizer['fill'] = get_css_value(fills, 'PolygonSymbolizer', scale)
    elif line_symbolizer is not None:
        symbolizer['type'] = 'line'
        strokes = get_direct_elements_by_tag(line_symbolizer, 'Stroke')
        if len(strokes) > 0:
            symbolizer['stroke'] = get_css_value(strokes, 'LineSymbolizer', scale)
    elif point_symbolizer is not None:
        graphics = get_direct_elements_by_tag(point_symbolizer, 'Graphic')
        markers = get_direct_elements_by_tag(graphics[0], 'ExternalGraphic')
        if len(markers) > 0:
            symbolizer['type'] = 'marker'
            href = get_direct_elements_by_tag(markers[0], 'href')[0].text
            if href[:1] == "/":
                href = href[1:]
            symbolizer['object'] = {
                'file': href,
                # 'type': get_direct_elements_by_tag(markers[0], 'Format')[0].text      
                }
        else:
            symbolizer['type'] = 'point'
            strokes = get_direct_elements_by_tag(point_symbolizer, 'Stroke')
            fills = get_direct_elements_by_tag(point_symbolizer, 'Fill')
            if len(strokes) > 0:
                symbolizer['object']['stroke'] = get_css_value(strokes, 'LineSymbolizer', scale)
            if len(fills) > 0:
                symbolizer['object']['fill'] = get_css_value(fills, 'PolygonSymbolizer', scale)
        size = get_direct_elements_by_tag(graphics[0], 'Size')
        # if len(size) > 0:
        #     symbolizer['object']['height'] = size[0].text
        #     symbolizer['object']['width'] = size[0].text
        opacity = get_direct_elements_by_tag(graphics[0], 'opacity')
        if len(opacity) > 0:
            symbolizer['object']['opacity'] = opacity[0].text
    return symbolizer

def get_filter(filter):
    def get_operator(filter):
        has_and = len(get_direct_elements_by_tag(filter, 'And'))
        has_or = len(get_direct_elements_by_tag(filter, 'Or'))
        return 'and' if has_and else 'or' if has_or else None

    def get_comparisions(filter):
        comparisions = []
        for key in COMPARISION_OPERATOR_MAPPING:
            comparision_elements = get_all_elements_by_tag(filter, key)
            comparision_operator = COMPARISION_OPERATOR_MAPPING[key]
            for comparision_element in comparision_elements:
                property = get_text_from_tag(comparision_element, 'PropertyName')
                literal = get_text_from_tag(comparision_element, 'Literal')
                if property == 'placement_':
                    property = 'placement_ok'
                comparisions.append({
                    'operator': comparision_operator,
                    'property': property,
                    'literal': literal
                })
        return comparisions

    if filter is None:
        return None
    else:
        return {
            'operator': get_operator(filter),
            'comparisions': get_comparisions(filter),
        }

def get_rule_attributes(rule):
    attributes = RULE_ATTRIBUTES.keys()
    result = {}
    for a in list(attributes):
        element = get_first_element_by_tag(rule, RULE_ATTRIBUTES[a])
        if element is not None:
            result[a] = element.text
        else:
            result[a] = None
    return result

def get_rule(rule, scale):
    attributes = get_rule_attributes(rule)
    attributes['filter'] = get_filter(get_first_element_by_tag(rule, 'Filter'))
    attributes['symbolizer'] = get_symbolizer(rule, scale)
    return attributes

def get_style(layer, scale):
    s = {}
    style = get_first_element_by_tag(layer, 'UserStyle')
    s['Name'] = get_text_from_tag(style, 'Name')
    s['IsDefault'] = get_text_from_tag(style, 'IsDefault')
    feature_type_style = get_direct_elements_by_tag(style, 'FeatureTypeStyle')
    if len(feature_type_style) > 0:
        ft = []
        for feat in feature_type_style:
            rules = get_direct_elements_by_tag(feat, 'Rule')
            if len(rules) > 0:
                r = []
                for rule in rules:
                    ru = get_rule(rule, scale)
                    r.append(ru)
            else:
                r = None
            ft.append({
                'Rules': r
            })
    else:
        ft = None

    s['FeatureTypeStyle'] = ft
    return s


def parse(sldStringOrXml, scale):
    xml_doc = sldStringOrXml
    if isinstance(xml_doc, str):
        xml_doc = xml_from_string(sldStringOrXml)

    result = []
    layers = get_direct_elements_by_tag(xml_doc, 'NamedLayer')
    for layer in layers:
        l = {}
        name = get_text_from_tag(layer, 'Name')
        l['Name'] = name
        l['UserStyle'] = get_style(layer, scale)
        result.append(l)
    return result

def read_sld(folder, extension, scale):
    json_files = []
    for subfolder in os.listdir(folder):
        json_file = []
        for file in os.listdir(folder + subfolder):
            if file.endswith(extension):
                name = file.rsplit('.', 1)[0]
                with open(folder + subfolder + '/' + file, 'r') as f:
                    xml = f.read()
                    json_file.append(parse(xml, scale))
        json_files.append({
            'name': subfolder,
            'content': json_file
        })
    return json_files