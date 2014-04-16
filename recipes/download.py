# coding=utf-8
from git import *
from pysvn import *
from recipes.loggers import *
import os


class Download:
    """

    """

    def __init__(self, url, repo, cookbook_name, version, who):
        """
        Initial parameters
        @param url: The url of the repository
        @param repo: kind os repository
        @param cookbook_name: software name
        @param version: software version
        @param who: configuration management type
        @return: None if all OK or an error on failure
        """
        self.url = url
        self.repo = repo
        self.name = cookbook_name
        self.version = version
        self.manager = who

    def get_cookbook(self):
        """
        Download the repository
        @return: None if all OK or an error on failure
        """
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
                return msg
        elif self.repo == 'git':
            try:
                Git().clone(self.url, folder + self.name)
                set_info_log("Cookbook download")
            except Exception:
                msg += "Error: Cannot download the cookbook from " \
                       "git repository"
                set_error_log(msg)
                return msg
        else:
            msg += "Error: Cannot find the revision control"
            set_error_log(msg)
            return msg
        set_info_log(msg + "Complete Download")
        return None

    def check_cookbook(self):
        """
        Check the correct composition repository file
        @return: None if all OK or an error on failure
        """
        set_info_log("Checking the " + self.manager + " cookbook.....")
        if self.manager == 'chef':
            my_version = './cookbooks/' + self.name + '/recipes/' + \
                         self.version + '_install.rb'
        else:
            my_version = './cookbooks/' + self.name + '/manifests/install.pp'
        if os.path.exists(my_version):
            set_info_log("Exist: " + my_version)
        else:
            msg = "Error: invalid format. Recipe: version_install"
            set_error_log(msg)
            return msg
        return None


def remove_all(dir_name):
    """
    Remove a directory an all the files into it.
    @param dir_name: directory name
    @return: Nothing
    """
    for root, dirs, files in os.walk(dir_name, topdown=False):
        for name_cookbook in files:
            os.remove(os.path.join(root, name_cookbook))
        for name_cookbook in dirs:
            os.rmdir(os.path.join(root, name_cookbook))
