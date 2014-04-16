# coding=utf-8
class IServer:

    def remove_master_server(self):
        """
        Remove the software from puppet-master or chef-server
        @return: None if all OK or an error on failure
        """
        raise NotImplementedError

    def update_master_server(self):
        """
        Add the software into puppet-master or chef-server
        @return: None if all OK or an error on failure
        """
        raise NotImplementedError


class INode:

    def delete_node_client(self):
        """
        Delete the node from chef-server or puppet-master
        @return: None if all OK or an error on failure
        """
        raise NotImplementedError

    def add_node_run_list(self, software):
        """
        add the software to install into the list of the node
        @param software: The software
        @return: None if all OK or an error on failure
        """
        raise NotImplementedError
