__author__ = 'beatriz.munoz'


class IServer:
    def remove_master_server(self, request):
        raise NotImplementedError

    def update_master_server(self, request):
        raise NotImplementedError


class INode:
    def delete_node_client(self):
        raise NotImplementedError

    def add_node_run_list(self, software):
        raise NotImplementedError
