from recipes.error import final_error
from recipes.models import Data
from recipes.http import post, delete
from recipes.loggers import *
import recipes.imanagement as im


class MIPuppetMaster(im.IServer):
    def __init__(self, name, repo, cookbook_url):
        """
        Initial parameters
        @param name: module name
        @param repo: type of repository (svn or git)
        @param cookbook_url: url of the repository
        """
        self.name = name
        self.repo = repo
        self.cookbook_url = cookbook_url
        self.headers = {"Content-Type": "application/json"}
        self.puppet_master_url = Data.objects.get(key="puppet_master_url")

    def update_master_server(self, request):
        """
        Add the software into puppet-master or chef-server
        @param request: request of the user
        @return: None if all OK or an error on failure
        """
        if self.repo == 'svn':
            uri = '%s/%s/%s' % (
                self.puppet_master_url, 'download/svn', self.name)
            set_info_log("update puppet_master url: " + uri)
        elif self.repo == 'git':
            uri = u'{0:s}/{1:s}/{2:s}'.format(self.puppet_master_url,
                                              'download/git', self.name)
            set_info_log("update puppet_master url: " + uri)
        else:
            msg = "The repository is not svn or git. "
            set_error_log(msg)
            return final_error(msg, 4, request)
        payload = "url=" + self.cookbook_url
        set_info_log("update puppet_master payload: " + payload)
        response = post(uri, self.headers, payload)
        if response.status is not 200:
            msg = "Error downloading the puppet module into the puppet master"
            set_error_log(str(response.status) + ": "
                          + msg + ": " + response.read())
            return final_error(msg, 4, request)
        set_info_log(str(response.status) +
                     ": Correctly download the module into the puppet master")
        return None

    def remove_master_server(self, request):
        """
        Remove the software from puppet-master or chef-server
        @param request: request of the user
        @return: None if all OK or an error on failure
        """
        uri = u'{0:s}/{1:s}/{2:s}'.format(self.puppet_master_url,
                                          'delete/module', self.name)
        response = delete(uri, self.headers)
        if response.status is not 200:
            msg = "Error deleting the puppet module from the puppet master"
            set_error_log(str(response.status) + ": "
                          + msg + ": " + response.read())
            return final_error(msg, 4, request)
        set_info_log(str(response.status) +
                     ": Correctly deleting the module from the puppet master")
        return None


class MINode(im.INode):
    def __init__(self, name, tenant):
        """
        Initial parameters
        @param name: Name of the node
        @param tenant: Tenant-id
        """
        self.name = name
        self.puppet_master_url = Data.objects.get(key="puppet_master_url")
        self.headers = {"Content-Type": "application/json"}
        self.tenant = tenant

    def delete_node_client(self):
        """
        Delete the node from chef-server or puppet-master
        @return: None if all OK or an error on failure
        """
        uri = '%s/%s/%s' % (self.puppet_master_url, 'delete/node', self.name)
        set_info_log("delete node: puppet_master url: " + uri)
        response = delete(uri, self.headers)
        if response.status is not 200:
            msg = "Error deleting node from puppet"
            set_error_log(str(response.status) + ": "
                          + msg + ": " + response.read())
            return "Error"
        return None

    def add_node_run_list(self, software):
        """
        add the software to install into the list of the node
        @param software: The software
        @return: None if all OK or an error on failure
        """
        software_name = software[0]
        version = software[1]
        uri = '%s/%s/%s/%s/%s/%s' % (self.puppet_master_url, 'install',
                                     self.tenant, self.name, software_name,
                                     version)
        set_info_log(uri)
        response = post(uri, self.headers, None)
        if response.status is not 200:
            msg = "Error adding the software to puppet"
            set_error_log(str(response.status) + ": "
                          + msg + ": " + response.read())
            return "Error"
        uri = '%s/%s/%s' % (self.puppet_master_url, 'generate', self.name)
        set_info_log(uri)
        response = post(uri, self.headers, "")
        if response.status is not 200:
            msg = "Error adding the software to puppet"
            set_error_log(str(response.status) + ": "
                          + msg + ": " + response.read())
            return "Error"
        return None
