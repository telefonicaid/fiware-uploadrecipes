#from recipes.download import Download
#from recipes.error import final_error
#from recipes.models import Data
#from recipes.loggers import *
import os
import recipes.imanagement as im


class MIChef(im.IServer):
    def __init__(self, name, cookbook_url):
        self.name = name
        self.cookbook_url = cookbook_url

    def update_master_server(self, request):
        my_cook = 'cookbooks'
        output = os.system(
            "knife cookbook upload " + self.name + " -o " + my_cook)
        print(output)
        #if salida contiene la palabra: ERROR
        #msg = "Error updating cookbook into the chef server" + self.folder
        #    return final_error(msg, 4, request)
        return None

    def remove_master_server(self, request):
        output = os.system("knife cookbook delete " + self.name + " -y")
        print(output)
        #if salida contiene la palabra: ERROR
        #msg = "Error deleting the cookbook from the chef_server: " + self.name
        #    return final_error(msg, 4, request)
        return None


class MINode(im.IServer):
    def __init__(self, name):
        self.name = name

    def delete_node_client(self):
        output = os.system("knife client delete " + self.name + " -y")
        output2 = os.system("knife node delete " + self.name + " -y")
        print(output)
        print(output2)
        #if error return error
        return None

    def add_node_run_list(self, software):
        output = os.system(
            "knife node run_list add " + self.name + " " + software)
        print(output)
        #if Error: return error
        return None
