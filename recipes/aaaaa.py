import chef.api
import chef.node
from chef.base import ChefObject, ChefAPI
from chef.exceptions import *


class Cookbook(ChefObject):

    url = '/cookbooks'
    api_version = '0.10'
    attributes = {
        'url': str,
        'definitions': list,
        'files': list,
        'libraries': list,
        'metadata': dict,
        'providers': list,
        'recipes': list,
        'resources': list,
        'root_files': list,
        'templates': list,
        'version': str}

    def __init__(self, name, version=None, api=None, skip_load=False):
        self.name = name
        self.api = api or ChefAPI.get_global()
        self._check_api_version(self.api)
        self._versions = Cookbook.versions(name, self.api)
        self.url = (self.__class__.url + '/' + self.name + '/' + "1.0.0")
        data = {}
        if not skip_load:
            try:
                data = self.api[self.url]
            except ChefServerNotFoundError:
                pass
            else:
                self.exists = True
        self._populate(data)

    @property
    def latest_version(self):
        return self._versions[-1] if self._versions else None

    @classmethod
    def versions(cls, name, api=None):
        """Return a :list: of versions for the specified cookbook
        """
        api = api or ChefAPI.get_global()
        cls._check_api_version(api)
        try:
            data = api[Cookbook.url + '/' + name].get(name)
        except ChefServerNotFoundError:
            return "1.0.0"
        items = data.get('versions', []) if data else []
        return sorted([item['version'] for item in items])

    def delete(self, api=None):
        """Delete this object from the server."""
        api = api or self.api
        url = "/%s/%s/%s" % ("cookbooks", self.name, self._versions[0])
        api.api_request('DELETE', url)

    def save(self, api=None):
        """Save this object to the server. If the object does not exist it
        will be created.
        """
        api = api or self.api
        try:
            print(api.api_request('DELETE', "/cookbooks/mahout/0.1.0"))
            #api.api_request('PUT', self.url, data=self)
        except ChefServerNotFoundError:
            # If you get a 404 during a save, just create it instead
            # This mirrors the logic in the Chef code
            api.api_request('POST', self.__class__.url, data=self)


def chef_test():
    with ChefAPI('http://130.206.80.113:4000', '/etc/chef/client.pem',
                 'dhcp-17-155.imdea'):
        # Tenemos que coger el nombre de la maquina
        # Hay que registrarla en el chef-server
        #Hay que dar permisos 777 a client.pem
        # knife client edit "dhcp-17-155.imdea" y ponemos admin a true
        #export EDITOR=$(which vi)
        cookbook_name = "bea"
        #Para agregar las recetas al nodo

        name = "bmmneworion1001.novalocal"
        #my_node = chef.node.Node(name)
        my_node = chef.node.Node(name)
        print(my_node)
        print(my_node.run_list)

        my_node.run_list.append("recipe[orion::0.10.1_install]")
        print(my_node.run_list)
        print(str(my_node.attributes))
        my_node.save()

        #Listar los cookbooks del chef-server
        '''
        for cookbook in Cookbook.list():
            print(cookbook)
        '''
        #Cargamos un cookbook que ya esta o creamos uno nuevo
        '''
        my_cookbook = Cookbook(cookbook_name, version)
        print(my_cookbook._versions)
        '''

        #print("fuera del for: " + my_cookbook.name)
        '''
        my_cookbook = Cookbook("mahout", "0.1.0")
        print(my_cookbook)
        my_cookbook.delete()
        '''
        '''
        my_cookbook = Cookbook("mahout")
        #knife cookbook upload mahout -o
        #knife cookbook list | grep mahout
        my_cookbook.delete()
        '''
