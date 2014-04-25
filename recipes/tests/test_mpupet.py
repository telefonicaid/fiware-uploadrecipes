# coding=utf-8
from mockito import *
from django.test import TestCase
from recipes import mpuppet, loggers, http
from recipes.models import Data


class MIPuppetMasterTest(TestCase):

    def setUp(self):
        self.name = "name"
        self.repo = "svn"
        self.cookbook_url = "cookbook_url"
        self.headers = {"Content-Type": "application/json"}
        self.key = "puppet_master_url"
        self.value = "value"
        self.value_mocked = mock()
        self.data_mocked = mock()
        mockedQuery = Data.objects.create(key=self.key, value=self.value)
        when(self.data_mocked).get(key__exact=self.key).thenReturn(mockedQuery)
        when(self.data_mocked).objects().thenReturn(self.data_mocked)
        msg = mock()
        when(loggers).set_info_log(msg).thenReturn(None)
        when(loggers).set_error_log(msg).thenReturn(None)
        self.pupet = mpuppet.MIPuppetMaster(self.name, self.repo, self.cookbook_url)

    def test_update_master_server_no_repo(self):
        response = mock()
        pupet = mpuppet.MIPuppetMaster(self.name, "no_svn", self.cookbook_url)
        when(http).post(any(), self.headers, any()).thenReturn(response)
        when(response).status().thenReturn(200)
        result = pupet.update_master_server()
        self.assertIsNotNone(result)


    def test_update_master_server_200(self):
        response = mock()
        when(http).post(any(), self.headers, any()).thenReturn(response)
        when(response).status().thenReturn(200)
        result = self.pupet.update_master_server()
        self.assertIsNone(result)

    def test_update_master_server_no_200(self):
        response = mock()
        when(http).post(any(), self.headers, any()).thenReturn(response)
        when(response).status().thenReturn(404)
        when(response).read().thenReturn("Error")
        error = "Error downloading the puppet module into the puppet master"
        result = self.pupet.update_master_server()
        self.assertIsNotNone(result)
        self.assertEqual(result, error)

    def test_remove_master_server(self):
        response = mock()
        when(http).delete(any(), self.headers).thenReturn(response)
        when(response).status().thenReturn(200)
        result = self.pupet.remove_master_server()
        self.assertIsNone(result)

    def test_remove_master_server_fail(self):
        response = mock()
        when(http).delete(any(), self.headers).thenReturn(response)
        when(response).status().thenReturn(400)
        when(response).read().thenReturn("Error")
        result = self.pupet.remove_master_server()
        self.assertIsNotNone(result)


class MINodeTest(TestCase):

    def setUp(self):
        msg = mock()
        self.name = "name"
        self.headers = {"Content-Type": "application/json"}
        self.tenant = "tenant"
        self.data_mocked = mock()
        self.key = "puppet_master_url"
        self.value = "value"
        when(loggers).set_info_log(msg).thenReturn(None)
        when(loggers).set_error_log(msg).thenReturn(None)
        mockedQuery = Data.objects.create(key=self.key, value=self.value)
        when(self.data_mocked).get(key__exact=self.key).thenReturn(mockedQuery)
        when(self.data_mocked).objects().thenReturn(self.data_mocked)
        self.mpupet = mpuppet.MINode(self.name, self.tenant)

    def test_delete_node_client(self):
        response = mock()
        when(http).delete(any(), self.headers).thenReturn(response)
        when(response).status().thenReturn(200)
        result = self.mpupet.delete_node_client()
        self.assertIsNone(result)

    def test_delete_node_client_no_200(self):
        response = mock()
        when(http).delete(any(), self.headers).thenReturn(response)
        when(response).status().thenReturn(400)
        when(response).read().thenReturn("Error")
        result = self.mpupet.delete_node_client()
        self.assertIsNotNone(result)
        self.assertEqual(result, "Error")

    def test_add_node_run_list(self):
        response = mock()
        software = ["software", "version"]
        when(http).post(any(), self.headers, any()).thenReturn(response)
        when(response).status().thenReturn(200)
        result = self.mpupet.add_node_run_list(software)
        self.assertIsNone(result)

    def test_add_node_run_list_no_200(self):
        response = mock()
        software = ["software", "version"]
        when(http).post(any(), self.headers, any()).thenReturn(response)
        when(response).status().thenReturn(500)
        when(response).read().thenReturn("Error")
        result = self.mpupet.add_node_run_list(software)
        self.assertEqual(result, "Error")
        self.assertIsNotNone(result)
