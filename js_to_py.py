import js2py

translated = js2py.translate_js6("export function xmlToString($xml) {var transformer = TransformerFactory.newInstance().newTransformer();var result = new StreamResult(new java.io.StringWriter());var source = new DOMSource($xml);transformer.transform(source, result);return result.getWriter().toString();}")
print(translated)
# js2py.translate_file('javascript/lib/utils.js', 'python/mapnikwriter.py')