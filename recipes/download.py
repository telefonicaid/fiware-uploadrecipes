from git import *
from pysvn import *
from recipes.error import *
import os
from recipes.loggers import *
from recipes.models import *

url_repo = str(Data.objects.get(key="url_repository"))


class Download:
    def __init__(self, url, repo, cookbook_name, version, who):
        self.url = url
        self.repo = repo
        self.name = cookbook_name
        self.version = version
        self.manager = who

    def get_cookbook(self, request):
        folder = './cookbooks/'
        msg = "En el getCookbook. \n "
        set_info_log("url: " + self.url + ". name: " + folder + self.name)
        if self.repo == 'svn':
            try:
                Client().checkout(self.url, folder + self.name)
                set_info_log('Cookbook download in local')
            except Exception:
                msg += "Error: Cannot download the cookbook from " \
                       "svn repository"
                set_error_log(msg)
                return final_error(msg, 1, request)
        elif self.repo == 'git':
            try:
                Git().clone(self.url, folder + self.name)
                set_info_log("Cookbook download")
            except Exception:
                msg += "Error: Cannot download the cookbook from " \
                       "git repository"
                set_error_log(msg)
                return final_error(msg, 1, request)
        else:
            msg += "Error: Cannot find the revision control"
            set_error_log(msg)
            return final_error(msg, 1, request)
        set_info_log(msg + "Complete Download")
        return None

    def check_cookbook(self, request):
        set_info_log("Checking the " + self.manager + " cookbook.....")
        if self.manager == 'chef':
            my_version = './cookbooks/' + self.name + '/recipes/' + \
                         self.version + '_install.rb'
        else:
            my_version = './cookbooks/' + self.name + '/manifests/install.pp'
            print(my_version)
        if os.path.exists(my_version):
            set_info_log("Exist: " + my_version)
        else:
            msg = "Error: invalid format. Recipe: version_install"
            set_error_log(msg)
            return final_error(msg, 2, request)
        return None


def remove_all(dir_name):
    for root, dirs, files in os.walk(dir_name, topdown=False):
        for name_cookbook in files:
            os.remove(os.path.join(root, name_cookbook))
        for name_cookbook in dirs:
            os.rmdir(os.path.join(root, name_cookbook))


def get_login(realm, username=None, may_save=None):
    return True, '', '', True
