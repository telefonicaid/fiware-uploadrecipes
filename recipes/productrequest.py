from xml.etree.ElementTree import tostring
from recipes.productrelease import ProductRelease, Product, Attribute
from recipes.kingstion import *
from recipes.http import *
from recipes.loggers import *
import json


class ProductRequest:
    def __init__(self, token, tenant):
        """
        Initial parameters
        @param token: token
        @param tenant: tenant id
        """
        self.keystone_url = get_keystone()
        self.sdc_url = get_sdc()
        self.token = token
        self.products = []
        self.header2 = {'Content-Type': 'application/xml',
                        'X-Auth-Token': token, 'Tenant-Id': tenant}
        self.header = {"Accept": "application/json", 'X-Auth-Token': token,
                       'Tenant-Id': tenant}

    def delete_product_release(self, product_name, version):
        """
        Delete a release of a product
        @param product_name: the name of the product
        @param version:  the version of the product
        @return: None if all OK or an error on failure
        """
        my_url = "%s/%s/%s/%s/%s" % (
            self.sdc_url, "catalog/product", product_name,
            "release", version)
        response = delete(my_url, self.header)
        if response.status is not 200 and response.status is not 204:
            error = "error to delete the product release " \
                    + product_name + ' ' + str(response.status)
            return error
        return None

    def delete_product(self, product_name):
        """
        Delete a product
        @param product_name: the name of the product
        @return: None if all OK or an error on failure
        """
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
        """
        Add a prodduct to the SDC
        @param product_name:  the name of the product
        @param product_description: the description of the product
        @param attributes: the attributes of thw product
        @param metadatas: the metadata of teh product
        @return: (None if all OK / an error on failure),
                    (The product / None of error)
        """
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
        """
        Add a product release to the SDC
        @param product: A product into SDC
        @param product_name: The name of the product
        @param version: the version of the release
        @return: None if all OK / an error on failure
        """
        print(1)
        my_url = "%s/%s/%s/%s" % (
            self.sdc_url, "catalog/product", product_name, "release")
        product_release = ProductRelease(product, version)
        payload = product_release.to_product_xml()
        print(2)
        print(my_url)
        print(tostring(payload))
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
        """
        Processing the attribuetes
        @param attributes_string: the attributes into a string
        @return: an attributes list
        """
        attributes = []
        if attributes_string is None:
            return attributes
        attr = attributes_string.split(';')
        for att in attr:
            a = att.split('=')
            try:
                at = a[1].split(',')
                attribute = Attribute(a[0], at[0], at[1])
            except Exception:
                attribute = Attribute(a[0], a[1], '')
            attributes.append(attribute)
        return attributes

    def get_product_release(self, product_name):
        """
        Obtain the product release from a product
        @param product_name: the name of the product
        @return: The version of the software
        """
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
        """
        Obtain the information from a product release
        @param product_name: the product version
        @param product_version: the product release
        @return: The description of the product release
        """
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
                    attribute = Attribute(att['key'], att['version'],
                                          att['description'])
                    product.add_attribute(attribute)
            except Exception:
                pass
            product_release = ProductRelease(product, data['version'])
            set_info_log(product_release)
            return product_release

    def get_product_info(self, product_name):
        """
        return the information from a product
        @param product_name: the product name
        @return: the product description
        """
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
                    attribute = Attribute(att['key'], att['version'],
                                          att['description'])
                    product.add_attribute(attribute)
            except Exception:
                pass
            return product
