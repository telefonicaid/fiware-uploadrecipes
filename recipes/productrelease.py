from xml.etree.ElementTree import Element, SubElement, tostring


class Attribute:
    def __init__(self, att_name, att_value):
        self.key = att_name
        self.value = att_value


class Product:
    def __init__(self, product_name, product_description):
        self.name = product_name
        self.description = product_description
        self.attributes = []
        self.metadatas = []

    def add_attribute(self, attribute):
        self.attributes.append(attribute)

    def add_metadata(self, metadata):
        self.metadatas.append(metadata)

    def add_attributes(self, attributes):
        self.attributes = attributes

    def add_metadatas(self, metadatas):
        self.metadatas = metadatas

    def to_product_xml(self):
        product = Element('product')
        name = SubElement(product, 'name')
        name.text = self.name
        description = SubElement(product, "description")
        description.text = self.description
        if self.attributes is None:
            return tostring(product)
        for att in self.attributes:
            attribute = SubElement(product, "attributes")
            key = SubElement(attribute, "key")
            key.text = att.key
            value = SubElement(attribute, "value")
            value.text = att.value
        for meta in self.metadatas:
            metadata = SubElement(product, "metadatas")
            key = SubElement(metadata, "key")
            key.text = meta.key
            value = SubElement(metadata, "value")
            value.text = meta.value
        return product


class ProductRelease:
    def __init__(self, product, product_version):
        self.product = product
        self.version = product_version

    def to_product_xml(self):
        product_release = Element('productReleaseDto')
        version = SubElement(product_release, 'version')
        version.text = self.version
        return product_release
