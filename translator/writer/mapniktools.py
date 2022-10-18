import xml.etree.ElementTree as ET

def add_subelement_if_exists(parent, tag, value):
    if value is not None:
        child = ET.SubElement(parent, tag)
        child.text = value

def add_subelement_with_attrib(parent, tag, attrib):
    if attrib is not None:
        child = ET.SubElement(parent, tag)
        child.attrib = attrib