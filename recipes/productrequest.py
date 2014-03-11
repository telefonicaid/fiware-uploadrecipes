from xml.etree.ElementTree import tostring
from recipes.productrelease import ProductRelease, Product, Attribute
from recipes.kingstion import *
from recipes.http import *
import json


class ProductRequest:
    def __init__(self, keystone_url, sdc_url):
        self.keystone_url = keystone_url
        self.sdc_url = sdc_url
        self.token = get_token()
        self.products = []
        self.header2 = {'Content-Type': 'application/xml'}
        self.header = {"Accept": "application/json"}

    def delete_product_release(self, product_name, version):
        my_url = "%s/%s/%s/%s/%s" % (
            self.sdc_url, "catalog/product", product_name,
            "release", version)
        response = delete(my_url, self.header)
        if response.status is not 200 and response.status is not 204:
            error = "error to delete the product release " \
                    + product_name + ' ' + str(response.status)
            return error
        else:
            return None

    def delete_product(self, product_name):
        version = self.get_product_release(product_name)
        if version is not None:
            self.delete_product_release(product_name, version)
        my_url = "%s/%s" % (self.sdc_url, "catalog/product/" + product_name)
        response = delete(my_url, self.header)
        if response.status is not 200 and response.status is not 204:
            error = 'error deleting the product ' + product_name + ' ' + str(
                response.status)
            return error
        return None

    def get_products(self):
        """
        Obtain a list of the product's name
        @return:List od products
        """
        my_url = "%s/%s" % (self.sdc_url, "catalog/product")
        set_info_log(my_url)
        response = get(my_url, self.header)
        if response.status != 200:
            msg = "Error obtaining the token"
            set_error_log(msg)
            return "Error", msg
        else:
            data = json.loads(response.read())
            products = data["product"]
            my_products = []
            for product in products:
                var = product['name']
                my_products.append(var)
            set_info_log(my_products)
        return None, my_products

    def add_product(self, product_name, product_description, attributes,
                    metadatas):
        my_url = "%s/%s" % (self.sdc_url, "catalog/product")
        set_info_log(my_url)
        product = Product(product_name, product_description)
        if attributes is not None:
            attributes = self.process_attributes(attributes)
            for att in attributes:
                product.add_attribute(att)
        metadatas = self.process_attributes(metadatas)
        for meta in metadatas:
            product.add_metadata(meta)
        payload = product.to_product_xml()
        response = post(my_url, self.header2, tostring(payload))
        if response.status is not 200:
            error = 'error to add the product sdc ' + str(response.status)
            set_error_log(error)
            return error, None
        else:
            self.products.append(product)
        return None, product

    def add_product_release(self, product, product_name, version):
        my_url = "%s/%s/%s/%s" % (
            self.sdc_url, "catalog/product", product_name, "release")
        product_release = ProductRelease(product, version)
        payload = product_release.to_product_xml()
        response = post(my_url, self.header2, tostring(payload))
        if response.status != 200:
            return (
                'Error to add the product release to sdc ' + str(
                    response.status))
        else:
            self.products.append(product)
        return None

    @staticmethod
    def process_attributes(attributes_string):
        attributes = []
        if attributes_string is None:
            return attributes
        attr = attributes_string.split(';')
        for att in attr:
            a = att.split('=')
            attribute = Attribute(a[0], a[1])
            attributes.append(attribute)
        return attributes

    def get_product_release(self, product_name):
        my_url = "%s/%s/%s/%s" % (
            self.sdc_url, "catalog/product", product_name, "release")
        response = get(my_url, self.header)
        if response.status is not 200:
            error = 'error to get the product ' + product_name + ' ' + str(
                response.status)
            set_error_log(error)
            return error
        else:
            data = json.loads(response.read())
            set_info_log(data)
            if data is None:
                return None
        return data['productRelease']['version']

    def get_product_release_info(self, product_name, product_version):
        my_url = "%s/%s/%s/%s/%s" % (
            self.sdc_url, "catalog/product", product_name, "release",
            product_version)
        response = get(my_url, self.header)
        if response.status != 200:
            error = 'error to get the product ' + product_name + ' ' + str(
                response.status)
            set_error_log(error)
            return None
        else:
            data = json.loads(response.read())
            if data is None:
                return None
            product = Product(data['product']['name'], data['description'])
            try:
                for att in data['attributes']:
                    attribute = Attribute(att['key'], att['version'])
                    product.add_attribute(attribute)
            except Exception:
                pass
            product_release = ProductRelease(product, data['version'])
            set_info_log(product_release)
            return product_release

    def get_product_info(self, product_name):
        the_url = "%s/%s/%s" % (self.sdc_url, "catalog/product", product_name)
        response = get(the_url, self.header)
        if response.status != 200:
            set_error_log('error to get the product ' + product_name + ' '
                          + str(response.status))
            return None
        else:
            data = json.loads(response.read())
            set_info_log(data)
            if data is None:
                return None
            product = Product(data['name'], data['description'])
            try:
                for att in data['attributes']:
                    attribute = Attribute(att['key'], att['version'])
                    product.add_attribute(attribute)
            except Exception:
                pass
            return product
