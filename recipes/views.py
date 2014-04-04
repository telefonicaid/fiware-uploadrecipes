import datetime
from django.http import HttpResponseNotAllowed
from recipes.download import *
from recipes.mchef import MIChef
from recipes.openstack import OpenstackActions
from recipes.data_input import *
from recipes.sdccatalog import *
from recipes.mpuppet import MIPuppetMaster
from recipes.error import *
import xml.etree.ElementTree as TheElementTree
#Incluir descripcion en los atributos


def home(request):
    init_log()
    if (request.method != 'GET') and (request.method != 'POST'):
        set_error_log(request.method + ": Status -> 403. Method not allowed.")
        HttpResponseNotAllowed("Methods are GET or POST")

    if request.method == 'POST':
        set_info_log(request.method + " request in home")
        requestt = TheElementTree.parse(
            "/Users/beatriz.munoz/xifi-uploadrecipes/recipes/xmltest.xml")
        #requestt = TheElementTree.parse(
        # "/root/xifi-uploadrecipe/recipes/xmltest.xml")
        #requestt = TheElementTree.parse(request)
        root = requestt.getroot()
        name = get_name(root)
        version = get_version(root)
        cookbook_url = get_cookbook(root)
        desc = get_description(root)
        dependencies, depends_string = get_dependencies(root)
        sos = get_sos(root)
        who, chef_manager, pupet = get_manager(root)
        svn, git, repo = get_repository(root)
        ports = get_ports(root)
        attr = get_attr(root)
        token = get_token_request(request)
        #En el remove para chef, borramos cliente y nodo
        cookbook = Download(cookbook_url, repo, name, version, who)
        catalog = Catalog(name, version, desc, token)
        catalog.get_metadata(who, cookbook_url, sos, depends_string,
                             ports, repo, token)

        if attr != "":
            catalog.set_attributes(attr)

        print("Antes del DESCARGAR COOKBOOK")
        ##1.Descargamos el Cookbook
        set_debug_log("Antes del GET COOKBOOK")
        r = cookbook.get_cookbook(request)
        if r is not None:
            set_error_log("Error downloading the cookbook from the repository")
            return r
        ##2.Check the install
        set_debug_log("Antes del CHECK COOKBOOK")
        r = cookbook.check_cookbook(request)
        if r is not None:
            try:
                set_error_log("Error checking the cookbook")
                remove_all('./cookbooks/')
            except Exception:
                pass
            return r
        set_debug_log("Antes del UPDATE en el server")
        #4.Update chef_server o al puppet master
        chef_puppet = None
        if who == 'chef':
            chef_puppet = MIChef(name, cookbook_url)
        elif who == 'pupet':
            chef_puppet = MIPuppetMaster(name, repo, cookbook_url)

        r = chef_puppet.update_master_server(request)
        if r is not None:
            try:
                remove_all('./cookbooks/')
            except Exception:
                pass
            return r
        #5.Ahora test the recipe
        hour = "".join(
            "".join("".join(
                "".join(str(datetime.datetime.now()).split(":")).split(
                    "-")).split(" ")).split("."))
        for so in sos:
            vm_name = get_image(so) + hour
            openest = OpenstackActions(vm_name, so, name, version, who,
                                       tenant_name)
            r = openest.test(request)
            if r is not None:
                try:
                    remove_all('./cookbooks/')
                    chef_puppet.remove_master_server(request)
                except Exception:
                    pass
                return r
        #6. Add the product to the SDC Catalog
        r = catalog.add_catalog(request)
        if r is not None:
            try:
                set_error_log("Error adding the catalog to the SDC")
                remove_all('./cookbooks/')
                chef_puppet.remove_master_server(request)
            except Exception:
                pass
            return r
        remove_all('./cookbooks/')
        #chef_puppet.remove_master_server(request)
        set_info_log("WELL DONE")
        return final_error('final', 0, request)
