from recipes.error import final_error
from recipes.models import Data
from recipes.http import post
from recipes.loggers import *


class PuppetMaster:
    def __init__(self, name, repo, cookbook_url):
        self.name = name
        self.repo = repo
        self.cookbook_url = cookbook_url
        self.headers = {'Accept': "application/xml",
                        "Content-Type": "application/x-www-form-urlencoded"}
        self.puppet_master_url = Data.objects.get(key="puppet_master_url")

    def update_master_server(self, request):
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
        set_info_log("No necesary to remove from puppet " + self.name)
        return None
