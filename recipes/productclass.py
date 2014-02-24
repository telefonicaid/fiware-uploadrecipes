from xml.etree.ElementTree import Element, SubElement, tostring


class Attribute:
    def __init__(self, att_name, att_value):
        self.name = att_name
        self.value = att_value


class Product:
    def __init__(self, product_name, product_description, product_version):
        self.name = product_name
        self.product_description = product_description
        self.version = product_version
        self.attributes = None

    def to_product_xml(self):
        product = Element('productReleaseDto')
        name = SubElement(product, 'productName')
        name.text = self.name
        description = SubElement(product, "description")
        description.text = self.product_description
        version = SubElement(product, 'version')
        version.text = self.version
        if self.attributes is None:
            return tostring(product)
        for att in self.attributes:
            attribute = SubElement(product, "attributes")
            key = SubElement(attribute, "key")
            key.text = att.key
            value = SubElement(attribute, "value")
            value.text = att.value
        return tostring(product)

    def add_attribute(self, attribute):
        self.attributes.append(attribute)
