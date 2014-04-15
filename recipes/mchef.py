# coding=utf-8
from recipes.loggers import *
import os
import recipes.imanagement as im


class MIChef(im.IServer):
    def __init__(self, name, cookbook_url):
        """
        Initial parameters
        @param name: cookbook name
        @param cookbook_url: url from repository
        """
        self.name = name
        self.cookbook_url = cookbook_url

    def update_master_server(self):
        """
        Add the software into puppet-master or chef-server
        @return: None if all OK or an error on failure
        """
        my_cook = 'cookbooks'
        output = os.system(
            "knife cookbook upload " + self.name + " -o " + my_cook)
        if output > 0:
            msg = "Error uploading the cookbook into chef_server"
            set_error_log(msg)
            return msg
        set_info_log("Correctly upload the cookbook " + self.name)
        return None

    def remove_master_server(self):
        """
        Remove the software from puppet-master or chef-server
        @return: None if all OK or an error on failure
        """
        output = os.system("knife cookbook delete " + self.name + " -y")
        if output > 0:
            msg = "Error downloading the cookbook from chef_server"
            set_error_log(msg)
            return msg
        set_info_log("Correctly deleted the cookbook " + self.name)
        return None


class MINode(im.IServer):
    def __init__(self, name):
        """
        Initial parameters
        @param name: Name of the node
        """
        self.name = name

    def delete_node_client(self):
        """
        Delete the node from chef-server or puppet-master
        @return: None if all OK or an error on failure
        """
        output = os.system("knife client delete " + self.name + " -y")
        if output > 0:
            msg = "Error deleting " + self.name + " client from chef_server"
            set_error_log(msg)
            return msg
        output2 = os.system("knife node delete " + self.name + " -y")
        set_info_log(
            "Client " + self.name + " correctly deleted from chef-server")
        if output2 > 0:
            msg = "Error deleting " + self.name + " node from chef_server"
            set_error_log(msg)
            return msg
        set_info_log(
            "Node " + self.name + " correctly deleted from chef-server")
        return None

    def add_node_run_list(self, software):
        """
        add the software to install into the list of the node
        @param software: The software
        @return: None if all OK or an error on failure
        """
        output = os.system(
            "knife node run_list add " + self.name + " " + software)
        if output > 0:
            msg = "Error adding the recipe: " + software + "into the node " \
                  + self.name
            set_error_log(msg)
            return msg
        set_info_log(
            "Added the recipe: " + software + "into the node " + self.name)
        return None
