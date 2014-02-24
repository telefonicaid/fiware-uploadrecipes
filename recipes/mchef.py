import paramiko
from recipes.download import *
from recipes.error import final_error
from recipes.models import Data
from recipes.loggers import *

url_repo = str(Data.objects.get(key="url_repository"))


class Mychef:
    def __init__(self, name, repo, cookbook_url):
        self.name = name
        self.folder = str(Data.objects.get(key="chef_server_folder"))
        self.ip = str(Data.objects.get(key="chef_server_ip"))
        self.password = str(Data.objects.get(key="chef_server_password"))
        self.repo = repo
        self.cookbook_url = cookbook_url

    def update_master_server(self, request):
        try:
            self.update_server(request)
            set_info_log("Cookbook upload into chef-server")
        except:
            msg = "Error uploading the repository into the chef-server"
            set_error_log(msg)
            return final_error(msg, 4, request)
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(self.ip, 22, 'root', self.password)
        except Exception:
            msg = "Error connecting with the chef server"
            set_error_log(msg)
            return final_error(msg, 4, request)
        try:
            set_info_log(self.folder)
            uentrada, usalida, uerror = ssh_client.exec_command(
                'svn update ' + self.folder)
            set_info_log(usalida.read())
        except Exception:
            ssh_client.close()
            msg = "Error updating the test repository into chef server"
            return final_error(msg, 4, request)
        try:
            entrada2, salida2, error2 = ssh_client.exec_command(
                'knife cookbook upload ' + self.name + ' -o ' + self.folder)
            set_info_log(salida2.read())
        except Exception:
            ssh_client.close()
            msg = "Error updating cookbook into the chef server" + self.folder
            return final_error(msg, 4, request)
        ssh_client.close()
        return None

    def remove_master_server(self, request):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(self.ip, 22, 'root', self.password)
        except Exception:
            msg = "Error connecting with the chef server"
            return final_error(msg, 4, request)
        try:
            command = 'knife cookbook delete ' + self.name + ' -y'
            rentrada, rsalida, rerror = ssh_client.exec_command(command)
            set_info_log(rsalida.read())
            ssh_client.close()
        except Exception:
            msg = "Error deleting the cookbook from the chef_server"
            return final_error(msg, 4, request)
        return None

    def update_server(self, request):
        my_cook = './cookbooks/'
        client = Client()
        try:
            set_info_log("url: " + url_repo)
            set_info_log("cookbook: " + my_cook)
            client.checkout(url_repo, my_cook)
            set_info_log("Download Tester repository")
        except Exception:
            set_info_log("The cookbook is already into the repository")
        try:
            client.add(my_cook + self.name)
            client.callback_get_login = get_login
            client.checkin([my_cook + self.name],
                           "Adding the cookbook " + self.name)
            set_info_log("Commit in Tester folder")
        except Exception:
            msg = "Error: Cannot commit to the repository"
            set_error_log(msg)
            return final_error(msg, 3, request)
        return None
