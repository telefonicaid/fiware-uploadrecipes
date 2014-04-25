# coding=utf-8
from recipes import productrelease
import xml.etree.ElementTree as EL
from recipes import http, loggers, kingstion
import json


class ProductRequest:
    def __init__(self, token, tenant):
        """
        Initial parameters
        @param token: token
        @param tenant: tenant id
        """
        self.tenant = tenant
        self.sdc_url = kingstion.get_sdc()
        self.token = token
        self.products = []
        self.header2 = {'Content-Type': 'application/xml',
                        'X-Auth-Token': token, 'Tenant-Id': tenant}
        self.header = {"Accept": "application/json", 'X-Auth-Token': token,
                       'Tenant-Id': tenant}

    def delete_product(self, product_name):
        """
        Delete a product
        @param product_name: the name of the product
        @return: None if all OK or an error on failure
        """
        prr = ProductReleaseRequest(self.token, self.tenant)
        version = prr.get_product_release(product_name)
        if version is not None:
            prr.delete_product_release(product_name, version)
        my_url = "%s/%s" % (self.sdc_url, "catalog/product/" + product_name)
        response = http.delete(my_url, self.header)
        if response.status() is not 200 and response.status() is not 204:
            error = 'error deleting the product ' + product_name + ' ' + str(
                response.status())
            return error
        return None

    def get_products(self):
        """
        Obtain a list of the product's name
        @return:List od products
        """
        my_url = "%s/%s" % (self.sdc_url, "catalog/product")
        loggers.set_info_log(my_url)
        response = http.get(my_url, self.header)
        if response.status() != 200:
            msg = "Error obtaining the token"
            loggers.set_error_log(msg)
            return "Error", msg
        else:
            data = json.loads(response.read())
            products = data["product"]
            my_products = []
            for product in products:
                var = product['name']
                my_products.append(var)
            loggers.set_info_log(my_products)
        return None, my_products

    def get_product_info(self, product_name):
        """
        return the information from a product
        @param product_name: the product name
        @return: the product description
        """
        the_url = "%s/%s/%s" % (self.sdc_url, "catalog/product", product_name)
        response = http.get(the_url, self.header)
        if response.status() != 200:
            loggers.set_error_log('error to get the product ' + product_name
                                  + ' ' + str(response.status()))
            return None
        else:
            data = json.loads(response.read())
            loggers.set_info_log(data)
            try:
                description = data['description']
            except Exception:
                return None
            return description

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
        loggers.set_info_log(my_url)
        product = productrelease.Product(product_name, product_description)
        if attributes is not None:
            attributes_list = productrelease.process_attributes(attributes)
            for att in attributes_list:
                product.add_attribute(att)
        metadatas_list = productrelease.process_attributes(metadatas)
        for meta in metadatas_list:
            product.add_metadata(meta)
        payload = product.to_product_xml()
        print(EL.tostring(payload))
        print(my_url)
        response = http.post(my_url, self.header2, EL.tostring(payload))
        if response.status() is not 200:
            error = 'error to add the product sdc ' + str(response.status())
            loggers.set_error_log(error)
            return error, None
        else:
            self.products.append(product)
        return None, product


class ProductReleaseRequest:

    def __init__(self, token, tenant):
        """
        Initial parameters
        @param token: token
        @param tenant: tenant id
        """
        self.sdc_url = kingstion.get_sdc()
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
        response = http.delete(my_url, self.header)
        if response.status() is not 200 and response.status() is not 204:
            error = "error to delete the product release " \
                    + product_name + ' ' + str(response.status())
            return error
        return None

    def add_product_release(self, product, product_name, version):
        """
        Add a product release to the SDC
        @param product: A product into SDC
        @param product_name: The name of the product
        @param version: the version of the release
        @return: None if all OK / an error on failure
        """
        my_url = "%s/%s/%s/%s" % (
            self.sdc_url, "catalog/product", product_name, "release")
        product_release = productrelease.ProductRelease(product, version)
        payload = product_release.to_product_xml()
        response = http.post(my_url, self.header2, EL.tostring(payload))
        if response.status() != 200:
            return (
                'Error to add the product release to sdc ' + str(
                    response.status()))
        else:
            self.products.append(product)
        return None

    def get_product_release(self, product_name):
        """
        Obtain the product release from a product
        @param product_name: the name of the product
        @return: The version of the software
        """
        my_url = "%s/%s/%s/%s" % (
            self.sdc_url, "catalog/product", product_name, "release")
        response = http.get(my_url, self.header)
        if response.status() != 200:
            error = 'error to get the product ' + product_name + ' ' + str(
                response.status())
            loggers.set_error_log(error)
            return None
        else:
            data = json.loads(response.read())
            loggers.set_info_log(data)
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
        response = http.get(my_url, self.header)
        if response.status() != 200:
            error = 'error to get the product ' + product_name + ' ' + str(
                response.status())
            loggers.set_error_log(error)
            return None
        else:
            data = json.loads(response.read())
            try:
                description = data['productRelease']['product']['description']
            except Exception:
                return None
        return description
