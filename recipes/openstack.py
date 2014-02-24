import sys
import time
from recipes.error import *
import paramiko
from recipes.kingstion import *
from recipes.http import *
import json
from recipes.models import *
from recipes.loggers import *


class OpenstackActions:
    def __init__(self, name, so, cookbook, recipe, manager):
        self.name = name
        self.so = so
        self.cookbook = cookbook
        self.recipe = recipe
        self.delete = True
        self.manager = manager
        self.url_openstack = get_openstack()
        self.keystone_url = get_keystone()
        self.token = get_token()
        self.sdc_ip = str(Data.objects.get(key="sdc_ip"))
        self.sdc_password = str(Data.objects.get(key="sdc_password"))
        self.header = {"X-Auth-Token": self.token,
                       "Content-Type": "application/json"}
        self.sdc_user = str(Data.objects.get(key="sdc_user"))

    def get_vm(self, vm_id):
        the_url = "%s/%s/%s" % (self.url_openstack, "servers", vm_id)
        response = get(the_url, self.header)
        if response.status is not 200 and response.status is not 202:
            set_error_log(str(response.status) + ': error to add the product')
            return None
        else:
            info = response.read()
            set_info_log(info)
            return info

    def while_till_deployed(self, vm_id):
        vm_info = self.get_vm(vm_id)
        if vm_info is None:
            return None
        server = json.loads(vm_info)
        status = server['server']['status']

        while status != 'ACTIVE' and status != 'ERROR':
            vm_info = self.get_vm(vm_id)
            if vm_info is None:
                return None
            server = json.loads(vm_info)
            status = server['server']['status']
        vm_info = self.get_vm(vm_id)
        server = json.loads(vm_info)
        try:
            addresses = server['server']['addresses']['private']
            ip = addresses[0]['addr']
        except KeyError:
            addresses = server['server']['addresses']['shared-net']
            ip = addresses[0]['addr']
        return ip

    def delete_vm(self, vm_id):
        the_url = "%s/%s/%s" % (self.url_openstack, "servers", vm_id)
        response = delete(the_url, self.header)
        if response.status != 204:
            return 'error deleting vm' + str(response.status) + response.reason
        else:
            set_info_log('Deleting VM ........')
        return None

    def install_software_in_node(self, product_name):
        global ssh_client
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(self.sdc_ip, 22, self.sdc_user,
                               self.sdc_password)
        except Exception:
            ssh_client.close()
            return "Error connecting with the Chef-server " \
                   "for installing the recipe"
        try:
            ssh_client.exec_command("knife node run_list add " + self.name
                                    + " " + product_name)
        except Exception:
            ssh_client.close()
            return "Error: associating the recipe into the chef-server node"
        ssh_client.close()
        return None

    def delete_node(self):
        global delete_ssh_client
        try:
            delete_ssh_client = paramiko.SSHClient()
            delete_ssh_client.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            delete_ssh_client.connect(self.sdc_ip, 22, 'root',
                                      self.sdc_password)
        except Exception:
            delete_ssh_client.close()
            return "Error connecting with the Chef-server during " \
                   "installation process"
        try:
            ssh_client.exec_command("knife node delete " + self.name)
        except Exception:
            ssh_client.close()
            return "Error deleting node from chef-server"
        ssh_client.close()
        return None

    def deploy_vm(self):
        the_url = "%s/%s" % (self.url_openstack, "servers")
        set_info_log("Deploy VM url: " + the_url)
        if self.so == 'ubuntu':
            payload = '{"server"' \
                      ': {"name": " ' \
                      + self.name + '", "imageRef": "' \
                      + get_image(self.so) + '", "flavorRef": "2"}}'
        else:
            payload = '{"server": ' \
                      '{"name": " ' + self.name + '", "imageRef": "' \
                      + get_image(self.so) + '", "flavorRef": "2"}}'
        response = post(the_url, self.header, payload)
        if response.status is not 200 and response.status is not 202:
            msg = str(response.status) + '. Error deploying the VM: ' + str(
                response.reason)
            return None, msg
        else:
            var = response.read()
            server = json.loads(var)
            vm_id = server['server']['id']
        ip = self.while_till_deployed(vm_id)
        return ip, vm_id

    @staticmethod
    def remove_node(my_node):
        my_node.delete()

    def rem_floating_ip(self, floating_ip, server_id, fip_id):
        the_url = "%s/%s/%s/%s" % (
            self.url_openstack, "servers", server_id, "action")
        payload = '{ "removeFloatingIp": {"address": "' + floating_ip + '" } }'
        set_info_log(the_url)
        set_info_log(payload)
        response = post(the_url, self.header, payload)
        set_info_log(response.status)
        if response.status != 202:
            msg = "Error: Cannot un-assign the floating IP"
            return None, msg
        the_url = "%s/%s/%s" % (self.url_openstack, "os-floating-ips", fip_id)
        response = delete(the_url, self.header)
        set_info_log("Deleted the floating IP")
        if response.status != 202:
            msg = "Error deleting the floating IP"
            return None, msg
        return floating_ip, None

    def add_floating_ip(self, vm_id):
        my_url = "%s/%s" % (self.url_openstack, "os-floating-ip-pools")
        response = get(my_url, self.header)
        if response.status != 200:
            msg = "Error: Cannot obtain the pools"
            return None, msg
        var = response.read()
        pool = json.loads(var)
        pools = []
        for my_pool in pool['floating_ip_pools']:
            pools.append(my_pool['name'])
        if len(pools) < 1:
            msg = "No exits any pools"
            return None, msg
        my_url = "%s/%s" % (self.url_openstack, "os-floating-ips")
        response = None
        for pol in pools:
            payload = '{ "pool": "' + pol + '"}'
            response = post(my_url, self.header, payload)
            if response.status is 200:
                set_info_log("IP from pool: " + pol)
                break
        if response.status != 200:
            msg = "Error: cannot create a floating IP in any pool"
            return None, msg
        floating = json.loads(response.read())
        floating_ip = floating['floating_ip']['ip']
        floating_ip_id = floating['floating_ip']['id']
        set_info_log(floating_ip)
        my_url = "%s/%s/%s/%s" % (
            self.url_openstack, "servers", vm_id, "action")
        payload = '{ "addFloatingIp": {"address": "' + floating_ip + '" } }'
        set_info_log(my_url)
        response = post(my_url, self.header, payload)
        set_info_log(response.read())
        if response.status is not 202:
            msg = "Error: Cannot assign the floating IP to the VM"
            return None, msg
        return floating_ip, floating_ip_id

    def connect_ssh(self, ip):
        set_info_log("En el ssh")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            if self.so == 'ubuntu':
                ssh.connect(ip, username=self.sdc_user, password=str(
                    Data.objects.get(key="ubuntu_password")))
            else:
                ssh.connect(ip, username=self.sdc_user, password=str(
                    Data.objects.get(key="centos_password")))
        except Exception:
            msg = 'Error connecting to the Chef-server for recipe execution'
            set_error_log(msg)
            return msg
        stdin, stdout, stderr = ssh.exec_command('chef-client')
        stdin.flush()
        result = ''
        for line in stdout:
            result += line.strip('\n')
            set_info_log(line.strip('\n'))
        ssh.close()
        if "FATAL" in result:
            msg = 'ERROR to execute the recipe'
            set_error_log(msg)
            return msg
        return None

    def test(self, request):
        set_info_log("En el test de openstack")
        set_info_log("*************")
        set_info_log(self.name)
        set_info_log(self.so)
        set_info_log(self.cookbook)
        set_info_log(self.recipe)
        set_info_log("*************")

        parts = self.recipe.split('.')
        if self.manager == 'chef' and parts[len(parts) - 1] == 'rb':
            msg = "Error. Recipe not well formed"
            set_error_log(msg)
            return final_error(msg, 5, request)

        if self.manager == 'pupet' and parts[len(parts) - 1] == 'pp':
            msg = "Error. Recipe not well formed"
            set_error_log(msg)
            return final_error(msg, 5, request)

        if self.recipe == '':
            software_install = sys.argv[3]
        else:
            software_install = self.cookbook + '::' + self.recipe
        token = get_token()
        if token is None:
            msg = "Error: Cannot obtained the token"
            set_error_log(msg)
            return final_error(msg, 5, request)
        ip, server_id = self.deploy_vm()
        if ip is None:
            msg = server_id + ". Operating System: " + self.so
            set_error_log(msg)
            return final_error(msg, 5, request)
        set_info_log("Correctly deployed VM " + self.so)
        fip, fip_id = self.add_floating_ip(server_id)
        if fip is None:
            self.delete_vm(server_id)
            set_error_log(fip_id)
            return final_error(fip_id, 5, request)
        time.sleep(60)
        r = self.install_software_in_node(software_install)
        if r is not None:
            self.rem_floating_ip(fip, server_id, fip_id)
            self.delete_vm(server_id)
            msg = 'Error installing software in a VM with: ' + self.so + \
                  '. Error: ' + r
            set_error_log(msg)
            return final_error(msg, 5, request)
        r = self.connect_ssh(fip)
        if r is not None:
            self.rem_floating_ip(fip, server_id, fip_id)
            self.delete_vm(server_id)
            self.delete_node()
            msg = "Error testing the software:  " + r
            set_error_log(msg)
            return final_error(msg, 5, request)
        set_info_log("Antes del delete")
        r = self.delete_vm(server_id)
        self.delete_node()
        if r is not None:
            msg = "Error deleting the testing VM: " + r
            set_error_log(msg)
            return final_error(msg, 5, request)
        self.rem_floating_ip(fip, server_id, fip_id)
        return None
