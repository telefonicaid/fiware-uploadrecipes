import datetime
from django.http import HttpResponseNotAllowed
from django.core.context_processors import csrf
from setuptools.compat import unicode
from recipes.download import *
from recipes.mchef import Mychef
from recipes.openstack import OpenstackActions
from recipes.inputtest import *
from recipes.sdccatalog import *
from recipes.puppet import *
from recipes.error import *


def home(request):
    init_log()
    if (request.method != 'GET') and (request.method != 'POST'):
        set_error_log(request.method + ": Status -> 403. Method not allowed.")
        HttpResponseNotAllowed("Methods are GET or POST")
    c = {}
    c.update(csrf(request))

    if request.method == 'GET':
        set_info_log("")
        set_info_log(request.method + " request in home")
        err, dep = my_list_catalog(request)
        #set_info_log(get_images_sdc_aware())
        if err is not None:
            set_error_log("Error listing the SDC Products")
            return dep
        template = get_template('form.html')
        return HttpResponse(
            template.render(RequestContext(request, {'dependslist': dep})))

    if request.method == 'POST':
        set_info_log(request.method + " request in home")
        name = request.POST.get('name')
        version = request.POST.get('version')
        cookbook_url = request.POST.get('url')
        desc = request.POST.get('desc')
        dependencies, depends_string = get_dependencies(request)
        meta = request.POST.get('meta')
        sos, centos, ubuntu = get_sos(request)
        who, chef, pupet = get_installator(request)
        svn, git, repo = get_repository(request)
        attr = request.POST.get('attr')
        ports = request.POST.get('ports')
        err, my_error = is_error(cookbook_url, svn, git, name, version,
                                 centos, ubuntu, chef, pupet)
        if err == 1:
            my_error = "Required Fields: " + my_error
            err, dep = my_list_catalog(request)
            if err is not None:
                set_error_log("Error listing the SDC Products")
                return dep
            for i in dependencies:
                try:
                    dep.remove(i)
                except ValueError:
                    pass
            template = get_template('form.html')
            return HttpResponse(template.render(
                RequestContext(request,
                               dict(centos=centos, ubuntu=ubuntu, err=my_error,
                                    name=name, git=git, svn=svn, desc=desc,
                                    ports=ports, meta=meta, chef=chef,
                                    pupet=pupet, attr=attr, version=version,
                                    url=cookbook_url, dependslist=dep,
                                    mydependslist=dependencies))))

        cookbook = Download(cookbook_url, repo, name, version, who)
        catalog = Catalog(name, version, desc)

        if (ports is None) or (ports == ""):
            ports = ""
        else:
            ports = process_data(ports)

        catalog.get_metadata(who, cookbook_url, ubuntu, centos, depends_string,
                             ports, repo)

        if attr != "":
            catalog.set_attributes(attr)
        chef_puppet = None

        if who == 'chef':
            chef_puppet = Mychef(name, repo, cookbook_url)
        elif who == 'pupet':
            chef_puppet = PuppetMaster(name, repo, cookbook_url)

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
                remove_all('./cookbooks/', name, who)
            except Exception:
                pass
            return r
        set_debug_log("Antes del UPDATE en el server")
        #4.Update chef_server o al puppet master
        chef_puppet.update_server(request)
        r = chef_puppet.update_master_server(request)
        if r is not None:
            try:
                remove_all('./cookbooks/', name, who)
            except Exception:
                pass
            return r
        #5.Ahora test the recipe
        recipe = version + "_install"
        hour = "".join(
            "".join("".join(
                "".join(unicode(datetime.datetime.now()).split(":")).split(
                    "-")).split(" ")).split("."))
        for so in sos:
            vm_name = so + hour
            openest = OpenstackActions(vm_name, so, name, recipe, who)
            r = openest.test(request)
            if r is not None:
                try:
                    remove_all('./cookbooks/', name, who)
                    chef_puppet.remove_master_server(request)
                except Exception:
                    pass
                return r
        r = catalog.add_catalog(request)
        if r is not None:
            try:
                set_error_log("Error adding the catalog to the SDC")
                remove_all('./cookbooks/', name, who)
                chef_puppet.remove_master_server(request)
            except Exception:
                pass
            return r
        remove_all('./cookbooks/', name, who)
        chef_puppet.remove_master_server(request)
        set_info_log("WELL DONE")
        return final_error('final', 0, request)
