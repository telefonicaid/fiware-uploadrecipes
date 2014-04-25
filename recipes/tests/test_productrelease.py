# coding=utf-8
from django.test import TestCase
from recipes.productrelease import *


class ProductReleaseTest(TestCase):
    def test_to_product_xml(self):
        self.version = "2.0"
        xml_result = "<productReleaseDto><version>" + self.version + \
                     "</version></productReleaseDto>"
        product = Product("name", "description")
        product_release = ProductRelease(product, self.version)
        result = product_release.to_product_xml()
        self.assertEqual(tostring(result), xml_result)
        self.assertEqual(product_release.version, self.version)
        self.assertEqual(product_release.product.name, "name")
        self.assertEqual(product_release.product.description, "description")


class ProductTest(TestCase):
    def setUp(self):
        self.product = Product("name", "description")
        self.attribute = Attribute("key", "value", "description")
        self.metadata = Attribute("key", "value", "")


    def test_add_attribute(self):
        length_before = len(self.product.attributes)
        self.product.add_attribute(self.attribute)
        self.assertEqual(len(self.product.attributes), length_before + 1)

    def test_add_metadata(self):
        length_before = len(self.product.metadatas)
        self.product.add_metadata(self.metadata)
        self.assertEqual(len(self.product.metadatas), length_before + 1)

    def test_to_product_xml(self):
        self.product.add_metadata(self.metadata)
        self.product.add_attribute(self.attribute)
        xml_result = "<product><name>name</name><description>description" \
                     "</description><attributes><key>key</key><value>value" \
                     "</value><description>description</description>" \
                     "</attributes><metadatas><key>key</key><value>value" \
                     "</value></metadatas></product>"
        result = self.product.to_product_xml()
        self.assertEqual(xml_result, tostring(result))

    def test_to_product_xml_no_attributes(self):
        self.product.add_metadata(self.metadata)
        xml_result = "<product><name>name</name><description>description" \
                     "</description><metadatas><key>key</key><value>value" \
                     "</value></metadatas></product>"
        result = self.product.to_product_xml()
        self.assertEqual(xml_result, tostring(result))


