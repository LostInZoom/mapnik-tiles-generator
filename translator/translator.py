import argparse, csv
import reader.sldreader as reader
import writer.mapnikwriter as writer
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert SLD style to mapnik xml.')
    parser.add_argument('-i', '--input', type=str, default='styles/sld/', help='folder location of sld to translate')
    parser.add_argument('-o', '--output', type=str, default='styles/xml_raw/', help='location of output xml')
    parser.add_argument('-e', '--extension', type=str, default='xml', help='extension of sld files')
    parser.add_argument('-s', '--scale_denominator', type=int, default=15000, help='output map scale denominator')
    params = parser.parse_args()

    layer_order = {}
    with open('styles/layer_order.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            layer_order[row[0].rsplit(".", 1)[0]] = int(row[1])

    json_files = reader.read_sld(params.input, params.extension, params.scale_denominator)
    layers = {}
    for json_file in json_files:
        layers_unsorted = []
        for l in json_file['content']:
            if l[0]['Name'] != 'emprise':
                layers_unsorted.append([l, layer_order[l[0]['Name']]])
        layers_sorted = reader.sort_list(layers_unsorted)
        layers[json_file['name']] = layers_sorted

    xmls = writer.create_mapnik_xml(layers)

    for xml in xmls:
        tree = ET.ElementTree(xmls[xml])
        output = open(params.output + xml + '.xml', "wb")
        output.write(ET.tostring(tree.getroot(), 'utf-8'))
        output.close()