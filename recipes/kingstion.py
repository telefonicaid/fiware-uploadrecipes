from recipes.http import *
from xml.dom.minidom import parseString
import json
from recipes.models import *
from recipes.loggers import *

headers = {'Accept': "application/xml", 'Content-Type': "application/json"}
url = str(Data.objects.get(key="openstack_url"))
tenant_name = str(Data.objects.get(key="openstack_tenant"))
password = str(Data.objects.get(key="openstack_name"))
username = str(Data.objects.get(key="openstack_password"))
region = str(Data.objects.get(key="openstack_region"))


def get_payload():
    payload = '{"auth":{"tenantName":"' + tenant_name + \
              '","passwordCredentials":{"username":"' + username + \
              '","password":"' + password + '"}}}'
    return payload


def get_data():
    response = post(url, headers, get_payload())
    if response.status != 200:
        set_error_log(response.read())
        return None
    return response.read()


def get_service(name):
    e = json
    s = json
    data = get_data()
    payload = parseString(data)
    catalog = (payload.getElementsByTagName("serviceCatalog"))[0]
    services = (catalog.getElementsByTagName("service"))
    for s in services:
        if name == s.attributes["name"].value:
            break
    endpoints = s.getElementsByTagName("endpoint")
    for e in endpoints:
        if region == e.attributes["region"].value:
            break
    return e.attributes["adminURL"].value


def get_tenant_from_token(token):
    my_headers = {'Content-Type': "application/xml",
                  'Accept': "application/xml",
                  'X-Auth-Token': get_token()}
    my_url = url + "/" + token
    response = get(my_url, my_headers)
    payload = parseString(response.read())
    token = (payload.getElementsByTagName("token"))[0]
    tenant = (token.getElementsByTagName("tenant"))[0].attributes["id"].value
    set_info_log("Tenant: " + tenant)
    return tenant


def get_tenant():
    data = get_data()
    payload = parseString(data)
    token = (payload.getElementsByTagName("token"))[0]
    tenant = (token.getElementsByTagName("tenant"))[0].attributes["id"].value
    set_info_log("Tenant: " + tenant)
    return tenant


def get_token():
    data = get_data()
    payload = parseString(data)
    token = ((payload.getElementsByTagName("token"))[0]).attributes["id"].value
    set_info_log("token: " + token)
    return token


def get_paas():
    paas = get_service("paas")
    set_info_log("PaasManager URL: " + paas)
    return paas


def get_sdc():
    """
    sdc = get_service("sdc")
    set_info_log("SDC URL: " + sdc)
    return sdc
    """
    return "http://130.206.80.119:8087/sdc/rest"


def get_chef_server():
    chef = get_service("chefserver")
    set_info_log("Chef server: " + chef)
    return chef


def get_chef_server_ip():
    chef = get_service("chefserver")
    chef = (chef.split("//")[1]).split(":")[0]
    set_info_log("Chef Server IP: " + chef)
    return chef


def get_keystone():
    keystone = get_service("keystone")
    set_info_log("keystone URL: " + keystone)
    return keystone


def get_openstack():
    openstack = get_service("nova")
    set_info_log("Openstack URL: " + openstack)
    return openstack


def get_glance():
    glance = get_service("glance")
    set_info_log("Glance URL: " + glance)
    return glance


def get_images_list():
    #my_url = get_glance() + "/images/detail"
    my_url = "http://130.206.80.58:9292/v1/images/detail"
    set_info_log("Images list URL: " + my_url)
    my_headers = {'Content-Type': "application/json",
                  'X-Auth-Token': get_token()}
    response = get(my_url, my_headers)
    if response.status is not 200:
        return None
    return response.read()


def get_image_name(img):
    return img[0]


def get_image_id(img):
    return img[1]


def get_image(img_id):
    images_list = get_images_list()
    set_info_log(images_list)
    img_name = ""
    for image in images_list:
        if img_id == get_image_id(image):
            img_name = get_image_name(image)
            break
    return img_name
