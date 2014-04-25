# coding=utf-8
import datetime
from django.http import HttpResponseNotAllowed
from recipes.download import *
from recipes.mchef import MIChef
from recipes.openstack import OpenstackActions
from recipes.data_input import *
from recipes.sdc import *
from recipes.mpuppet import MIPuppetMaster
from recipes.error import *
from recipes.kingstion import *
from xml.etree.ElementTree import parse
#Incluir description en los attributes


def home(request):
    """
    The principal management
    @param request: the user request
    @return: an error or an Http Response
    """
    init_log()
    #Deberi a ser solo distinto de POST, pero lo tengo para simplificar
    #mis pruebas
    if (request.method != 'GET') and (request.method != 'POST'):
        set_error_log(request.method + ": Status -> 403. Method not allowed.")
        HttpResponseNotAllowed("Methods are GET or POST")

    if request.method == 'POST':
        set_info_log(request.method + " request in home")
        #request_parsed = parse(
        #"/Users/beatriz.munoz/xifi-uploadrecipes/recipes/xmltest_puppet.xml")
        #"/Users/beatriz.munoz/xifi-uploadrecipes/recipes/xmltest_chef.xml")
        #"/root/xifi-uploadrecipes/recipes/xmltest_puppet.xml")
        # Parseamos el xml que recibimos para obtener los datos
        request_parsed = parse(request)
        root = request_parsed.getroot()
        name = get_name(root)
        version = get_version(root)
        cookbook_url = get_cookbook(root)
        desc = get_description(root)
        dependencies, depends_string = get_dependencies(root)
        sos = get_sos(root)
        who, chef_manager, pupet = get_manager(root)
        svn, git_repo, repo = get_repository(root)
        tcp = get_ports(root, "tcp_ports")
        udp = get_ports(root, "udp_ports")
        attr = get_attr(root)
        token = get_token_request(request)
        cookbook = Download(cookbook_url, repo, name, version, who)
        catalog = Catalog(name, version, desc, token)
        catalog.get_metadata(who, cookbook_url, sos, depends_string,
                             tcp, udp, repo, token)
        if attr != "":
            catalog.set_attributes(attr)
        ##1.Descargamos el Cookbook

        set_debug_log("Antes del GET COOKBOOK")
        r = cookbook.get_cookbook()
        if r is not None:
            set_error_log("Error downloading the cookbook from the repository")
            return r
        set_debug_log("Correctly download the software from repository")

        ##2.Check the install
        r = cookbook.check_cookbook()
        if r is not None:
            try:
                set_error_log("Error checking the cookbook")
                remove_all('./cookbooks/')
            except Exception:
                pass
            return r
        try:
            set_info_log("Deleting the repository from our system")
            remove_all('./cookbooks/')
            set_info_log("Repository deleted from our system")
        except Exception:
            set_error_log("Cannot delete the repository from out system")
        set_debug_log("Correctly checked the software")

        #3.Update chef_server o al puppet master
        chef_puppet = None
        if who == 'chef':
            chef_puppet = MIChef(name, cookbook_url)
        elif who == 'pupet':
            chef_puppet = MIPuppetMaster(name, repo, cookbook_url)
        r = chef_puppet.update_master_server
        if r is not None:
            return r

        #4.Ahora test the recipe
        hour = "".join(
            "".join("".join(
                "".join(str(datetime.datetime.now()).split(":")).split(
                    "-")).split(" ")).split("."))

        for so in sos:
            #Eliminamos los puntos del nombre de la VM, por un bug del
            #puppet wrappet
            try:
                vm_name = "".join(get_image(so).split(".")) + hour
            except Exception:
                vm_name = get_image(so) + hour
            #Realizamos las operaciones de despliegue etc
            openest = OpenstackActions(vm_name, so, name, version, who, token)
            r = openest.test()
            if r is not None:
                try:
                    chef_puppet.remove_master_server()
                except Exception:
                    pass
                return r

        #5. Add the product to the SDC Catalog
        r = catalog.add_catalog()
        if r is not None:
            try:
                set_error_log("Error adding the catalog to the SDC")
                #chef_puppet.remove_master_server(request)
            except Exception:
                pass
            return r
        set_info_log("WELL DONE")
        return final_error('final', 0, request)
