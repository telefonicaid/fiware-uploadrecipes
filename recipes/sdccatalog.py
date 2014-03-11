from recipes.error import *
from recipes.productrequest import *
from recipes.kingstion import *
from recipes.loggers import *
import json


class Catalog:
    def __init__(self, name, version, desc):
        self.name = name
        self.version = version
        self.attr = None
        self.desc = desc
        self.meta = None

    def set_attributes(self, attr):
        """
        Separate correctly the attributes of the cookbook to store them
        @return: attributes
        """
        self.attr = attr
        return attr

    def get_metadata(self, manager, uri, sos, depend, ports, repo):
        meta = "installator=" + manager
        if ports == "":
            meta += ";open_ports=22     "
        else:
            meta += ";open_ports=22 " + ports
        meta += ";cloud=yes"
        meta += ";repository=" + repo
        meta += ";public=no"
        meta += ";cookbook_url=" + uri
        images = ""
        for so in sos:
            if images != "":
                images += " " + get_image(so)
            else:
                images = get_image(so)
        meta += ";image=" + images

        if depend is not None:
            meta += ";" + depend
        self.meta = meta
        return meta

    def load_data(self):
        f = open('tester/' + self.name)
        json_data = f.read()
        return json.loads(json_data)

    def remove_catalog(self, request):
        try:
            g = ProductRequest(get_keystone(), get_sdc())
            err = g.delete_product_release(self.name, self.version)
            if err is not None:
                return final_error('Error deleting the product release', 6,
                                   request)
            err = g.delete_product(self.name)
            if err is not None:
                return final_error("Error deleting the product ", 6, request)
        except Exception:
            msg = "Error updating the recipes to SDC server"
            return final_error(msg, 6, request)

    def add_catalog(self, request):
        try:
            g = ProductRequest(get_keystone(), get_sdc())
            err, product = g.add_product(self.name, self.desc, self.attr,
                                         self.meta)
            if err is not None:
                return final_error("Error adding the product", 6, request)
            err = g.add_product_release(product, self.name, self.version)
            if err is not None:
                return final_error("Error adding the product release", 6,
                                   request)
        except Exception:
            msg = "Error updating the recipes to SDC server"
            return final_error(msg, 6, request)
        return None


def process_data(data):
    return " ".join(
        " ".join(" ".join(
            " ".join(" ".join(
                " ".join(data.split(
                    ",")).split(";")).split(
                "-")).split("    ")).split(
            "   ")).split("  "))


def my_list_catalog(request):
    """
    Obtain the current product list in the SDC server
    @param request: Http request
    @return: The list of product or the error if yo cannot ibtain it
    """
    try:
        g = ProductRequest(get_keystone(), get_sdc())
        err, msg = g.get_products()
        if err is not None:
            set_error_log(msg)
            return "Error", final_error(msg, 6, request)
    except Exception:
        msg = "Error getting product list"
        set_error_log(msg)
        return "Error", final_error(msg, 6, request)
    set_info_log(
        "Product list obtained correctly from SDC-Server: " + str(msg))
    return None, msg
