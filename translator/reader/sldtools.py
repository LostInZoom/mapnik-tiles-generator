import xml.etree.ElementTree as ET
import cv2

def resize_image(href, size):
    img = cv2.imread(href, cv2.IMREAD_UNCHANGED)
    print('Original Dimensions : ',img.shape)
    width = 350
    height = 450
    dim = (width, height)

    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    print('Resized Dimensions : ',resized.shape)

    cv2.imshow("Resized image", resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def sort_list(list):
    list.sort(key = lambda x: x[1])
    return list

def meter_to_pixel(value, scale):
    return round(value/(0.00028*scale), 2)

def parse_css_value(str, scale):
    isfloat = True
    try:
        float(str)
    except ValueError:
        isfloat = False

    if isfloat:
        return "{:.2f}".format(meter_to_pixel(float(str), scale))
    else:
        return str

def parse_dasharray(str, scale):
    dasharray = ''
    index = 0
    for value in str.split():
        if (index + 1) != len(str.split()):
            dasharray += "{:.2f}".format(meter_to_pixel(float(value), scale)) + ", "
        else:
            dasharray += "{:.2f}".format(meter_to_pixel(float(value), scale))
        index += 1
    return dasharray

def xml_from_string(str):
    return ET.fromstring(str)

def get_direct_elements_by_tag(element, tag_name):
    elements = []
    for e in element:
        if clear_string_between_char(e.tag, '{', '}') == tag_name:
            elements.append(e)
    return elements

def get_first_element_by_tag(element, tag_name):
    for e in element:
        if clear_string_between_char(e.tag, '{', '}') == tag_name:
            return e
            
def get_all_elements_by_tag(element, tag_name):
    elements = []
    for e in element.iter():
        if clear_string_between_char(e.tag, '{', '}') == tag_name:
            elements.append(e)
    return elements

def get_text_from_tag(element, tag_name):
    e = get_direct_elements_by_tag(element, tag_name)
    if len(e) > 0:
        if e[0].text != '':
            return e[0].text
        else:
            return None
    else:
        return None

# Clear a string by removing all characters located between two specified characters.
# Specified characters are also removed.
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
