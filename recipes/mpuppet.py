# coding=utf-8
from recipes import http, loggers, models
import recipes.imanagement as im


class MIPuppetMaster(im.IServer):
    """
    Class etc
    """
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

    @property
    def update_master_server(self):
        """
        Add the software into puppet-master or chef-server
        @return: None if all OK or an error on failure
        """
        puppet_master_url = models.Data.objects.get(key="puppet_master_url")
        if self.repo == 'svn':
            uri = '%s/%s/%s' % (
                puppet_master_url, 'download/svn', self.name)
            loggers.set_info_log("update puppet_master url: " + uri)
        elif self.repo == 'git':
            uri = u'{0:s}/{1:s}/{2:s}'.format(puppet_master_url,
                                              'download/git', self.name)
            loggers.set_info_log("update puppet_master url: " + uri)
        else:
            msg = "The repository is not svn or git. "
            loggers.set_error_log(msg)
            return msg
        payload = "url=" + self.cookbook_url
        loggers.set_info_log("update puppet_master payload: " + payload)
        response = http.post(uri, self.headers, payload)
        if response.status is not 200:
            msg = "Error downloading the puppet module into the puppet master"
            loggers.set_error_log(str(response.status) + ": "
                                  + msg + ": " + response.read())
            return msg
        loggers.set_info_log(str(
            response.status) + ": Correctly download the module into the "
                               "puppet master")
        return None

    def remove_master_server(self):
        """
        Remove the software from puppet-master or chef-server
        @return: None if all OK or an error on failure
        """
        puppet_master_url = models.Data.objects.get(key="puppet_master_url")
        uri = u'{0:s}/{1:s}/{2:s}'.format(puppet_master_url,
                                          'delete/module', self.name)
        response = http.delete(uri, self.headers)
        if response.status is not 200:
            msg = "Error deleting the puppet module from the puppet master"
            loggers.set_error_log(str(response.status) + ": "
                                  + msg + ": " + response.read())
            return msg
        loggers.set_info_log(
            str(response.status) + ": Correctly deleting the module from the "
                                   "puppet master")
        return None


class MINode(im.INode):
    """
    Class to manage puppet agents
    """

    def __init__(self, name, tenant):
        """
        Initial parameters
        @param name: Name of the node
        @param tenant: Tenant-id
        """
        self.name = name
        self.headers = {"Content-Type": "application/json"}
        self.tenant = tenant

    def delete_node_client(self):
        """
        Delete the node from chef-server or puppet-master
        @return: None if all OK or an error on failure
        """
        puppet_master_url = models.Data.objects.get(key="puppet_master_url")
        uri = '%s/%s/%s' % (puppet_master_url, 'delete/node', self.name)
        loggers.set_info_log("delete node: puppet_master url: " + uri)
        response = http.delete(uri, self.headers)
        if response.status is not 200:
            msg = "Error deleting node from puppet"
            loggers.set_error_log(str(response.status) + ": "
                                  + msg + ": " + response.read())
            return "Error"
        return None

    def add_node_run_list(self, software):
        """
        add the software to install into the list of the node
        @param software: The software
        @return: None if all OK or an error on failure
        """
        puppet_master_url = models.Data.objects.get(key="puppet_master_url")
        software_name = software[0]
        version = software[1]
        uri = '%s/%s/%s/%s/%s/%s' % (puppet_master_url, 'install',
                                     self.tenant, self.name, software_name,
                                     version)
        loggers.set_info_log(uri)
        response = http.post(uri, self.headers, None)
        if response.status is not 200:
            msg = "Error adding the software to puppet"
            loggers.set_error_log(str(response.status) + ": "
                                  + msg + ": " + response.read())
            return "Error"
        uri = '%s/%s/%s' % (puppet_master_url, 'generate', self.name)
        loggers.set_info_log(uri)
        response = http.post(uri, self.headers, "")
        if response.status is not 200:
            msg = "Error adding the software to puppet"
            loggers.set_error_log(str(response.status) + ": "
                                  + msg + ": " + response.read())
            return "Error"
        return None
