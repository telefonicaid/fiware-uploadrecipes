# coding=utf-8
from xml.etree.ElementTree import Element, SubElement, tostring


class Attribute:

    """
    Attribute Class
    """
    def __init__(self, att_name, att_value, att_desc):
        self.key = att_name
        self.value = att_value
        self.description = att_desc


class Product:

    """
    Product Class
    """

    def __init__(self, product_name, product_description):
        """
        Initial parameters
        @param product_name: the product name
        @param product_description: the product description
        """
        self.name = product_name
        self.description = product_description
        self.attributes = []
        self.metadatas = []


    def add_attribute(self, attribute):
        """
        Add an attribute to a product
        @param attribute: the attribute
        """
        self.attributes.append(attribute)

    def add_metadata(self, metadata):
        """
        Add a metadata to a product
        @param metadata: the metadata
        """
        self.metadatas.append(metadata)

    def to_product_xml(self):
        """
        Convert the product to an xml
        @return: xml product
        """
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
            desc = SubElement(attribute, "description")
            desc.text = att.description
        for meta in self.metadatas:
            metadata = SubElement(product, "metadatas")
            key = SubElement(metadata, "key")
            key.text = meta.key
            value = SubElement(metadata, "value")
            value.text = meta.value
        return product


class ProductRelease:

    """
    Product release class
    """

    def __init__(self, product, product_version):
        """
        Initial parameters
        @param product: the product
        @param product_version: the product version
        """
        self.product = product
        self.version = product_version

    def to_product_xml(self):
        """
        Convert a product release into a xml
        @return: xml product release
        """
        product_release = Element('productReleaseDto')
        version = SubElement(product_release, 'version')
        version.text = self.version
        return product_release
