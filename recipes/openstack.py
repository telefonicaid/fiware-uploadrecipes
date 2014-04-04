import time
import paramiko
from recipes.error import *
from recipes.kingstion import *
from recipes.http import *
from recipes.models import *
from recipes.loggers import *
import recipes.mchef as chef_management
import recipes.mpuppet as puppet_management
import json


class OpenstackActions:
    def __init__(self, name, so, cookbook, version, manager, tenant):
        self.tenant = tenant
        self.name = name
        self.so = so
        self.cookbook = cookbook
        self.version = version
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
        """

        @param vm_id:
        @return:
        """
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

    def deploy_vm(self):
        the_url = "%s/%s" % (self.url_openstack, "servers")
        set_info_log("Deploy VM url: " + the_url)
        #self.so es un numero de imagen
        payload = '{"server": ' \
                  '{"name": " ' + self.name + '", "imageRef": "' \
                  + self.so + '", "flavorRef": "2"}}'
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
            ssh.connect(ip, username=self.sdc_user, password=str(
                Data.objects.get(key="ubuntu_password")))
        except Exception:
            try:
                ssh.connect(ip, username=self.sdc_user, password=str(
                    Data.objects.get(key="centos_password")))
            except Exception:
                msg = 'Error connecting to the Chef-server for recipe ' \
                      'execution'
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
        set_info_log("*************")
        chef_puppet = None
        software_install = ''
        if self.manager == 'chef':
            chef_puppet = chef_management.MINode(self.name)
            software_install = self.cookbook + '::' + self.version + "_install"

        if self.manager == 'pupet':
            chef_puppet = puppet_management.MINode(self.name, self.tenant)
            software_install = [self.cookbook, self.version]

        if self.token is None:
            msg = "Error: Cannot obtained the token"
            set_error_log(msg)
            return final_error(msg, 5, request)

        ip, server_id = self.deploy_vm()
        if ip is None:
            msg = server_id + ". Image id: " + self.so
            set_error_log(msg)
            return final_error(msg, 5, request)
        set_info_log("Correctly deployed VM withb image id: " + self.so)
        fip, fip_id = self.add_floating_ip(server_id)

        if fip is None:
            self.delete_vm(server_id)
            set_error_log(fip_id)
            return final_error(fip_id, 5, request)
        time.sleep(60)

        r = chef_puppet.add_node_run_list(software_install)
        if r is not None:
            self.rem_floating_ip(fip, server_id, fip_id)
            self.delete_vm(server_id)
            msg = 'Error installing software in a VM with image id: ' + \
                  self.so + '. Error: ' + r
            set_error_log(msg)
            return final_error(msg, 5, request)

        r = self.connect_ssh(fip)
        if r is not None:
            self.rem_floating_ip(fip, server_id, fip_id)
            self.delete_vm(server_id)
            chef_puppet.delete_node_client()
            msg = "Error testing the software:  " + r
            set_error_log(msg)
            return final_error(msg, 5, request)

        set_info_log("Antes del delete")
        r = self.delete_vm(server_id)
        chef_puppet.delete_node_client()
        if r is not None:
            msg = "Error deleting the testing VM: " + r
            set_error_log(msg)
            return final_error(msg, 5, request)
        self.rem_floating_ip(fip, server_id, fip_id)

        return None
