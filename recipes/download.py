from git import *
from pysvn import *
from recipes.error import *
import os
from recipes.loggers import *


class Download:
    def __init__(self, url, repo, cookbook_name, version, who):
        """


        @param who: Installation gestor
        @param url: url of the user cookbook
        @param repo: type of revision control: svn/git
        @param cookbook_name: name of the cookbook
        @param version: version of the recipe
        """
        self.url = url
        self.repo = repo
        self.name = cookbook_name
        self.version = version
        self.manager = who

    def get_cookbook(self, request):
        folder = './cookbooks/'
        msg = "En el getCookbook. \n "
        set_info_log("url: " + self.url)
        set_info_log("name: " + folder + self.name)
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
        try:
            set_info_log("Tru to delete the versioned files")
            self.remove_version(folder + self.name)
            set_info_log(msg + "Removed repository files")
        except Exception:
            msg += "Error: Cannot remove the files from our revision control"
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
            my_version = './cookbooks/' + self.name + '/manifests/' + \
                         self.version + '_install.pp'
        if os.path.exists(my_version):
            set_info_log("Exist: " + my_version)
        else:
            msg = "Error: invalid format. Recipe: version_install"
            set_error_log(msg)
            return final_error(msg, 2, request)
        return None

    def remove_version(self, dir_name):
        if self.repo == "git":
            os.remove(dir_name + "/.git")
            os.remove(dir_name + "/.gitignore")
        else:
            fiches = os.listdir(dir_name)
            for fil in fiches:
                if fil == ".svn":
                    remove_all(dir_name + "/" + fil, self.name, self.manager)
                    os.removedirs(dir_name + "/" + fil)
                elif os.path.isdir(dir_name + "/" + fil):
                    self.remove_version(dir_name + "/" + fil)


def remove_all(dir_name, name, manager):
    if manager == 'chef':
        try:
            remove_server(name)
            set_info_log("Chef cookbook removed from svn repository")
        except:
            set_warning_log(
                "Cannot remove the cookbook from the svn repository")
    for root, dirs, files in os.walk(dir_name, topdown=False):
        for name_cookbook in files:
            os.remove(os.path.join(root, name_cookbook))
        for name_cookbook in dirs:
            os.rmdir(os.path.join(root, name_cookbook))


def get_login(realm, username=None, may_save=None):
    return True, '', '', True


def remove_server(name):
    try:
        client = Client()
        client.remove('./cookbooks/' + name)
        client.callback_get_login = get_login
        client.checkin(['./cookbooks/' + name], "Removing the cookbook")
    except:
        set_warning_log("Cannot remove the cookbook from the svn repository")
