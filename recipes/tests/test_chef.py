# coding=utf-8
from mockito import *
from django.test import TestCase
from recipes import mchef, loggers, http
from recipes.models import Data
import os


class MIChefTest(TestCase):

    def setUp(self):
        self.name = "name"
        self.cookbook_url = "cookbook_url"
        msg = mock()
        when(loggers).set_info_log(msg).thenReturn(None)
        when(loggers).set_error_log(msg).thenReturn(None)
        self.chef = mchef.MIChef(self.name, self.cookbook_url)

    def test_update_master_server_no_ok(self):
        when(os).system(any()).thenReturn(0)
        result = self.chef.update_master_server()
        self.assertIsNone(result)


    def test_update_master_server_200(self):
        when(os).system(any()).thenReturn(1)
        result = self.chef.update_master_server()
        self.assertIsNotNone(result)

    def test_remove_master_server(self):
        when(os).system(any()).thenReturn(0)
        result = self.chef.update_master_server()
        self.assertIsNone(result)

    def test_remove_master_server_fail(self):
        when(os).system(any()).thenReturn(1)
        result = self.chef.update_master_server()
        self.assertIsNotNone(result)


class MINodeTest(TestCase):

    def setUp(self):
        msg = mock()
        when(loggers).set_info_log(msg).thenReturn(None)
        when(loggers).set_error_log(msg).thenReturn(None)
        self.name = "name"
        self.chef = mchef.MINode(self.name)

    def test_delete_node_client(self):
        when(os).system(any()).thenReturn(0)
        result = self.chef.delete_node_client()
        self.assertIsNone(result)

    def test_delete_node_client_no_200(self):
        when(os).system(any()).thenReturn(1)
        result = self.chef.delete_node_client()
        self.assertIsNotNone(result)

    def test_add_node_run_list(self):
        when(os).system(any()).thenReturn(0)
        result = self.chef.delete_node_client()
        self.assertIsNone(result)

    def test_add_node_run_list_no_200(self):
        when(os).system(any()).thenReturn(1)
        result = self.chef.delete_node_client()
        self.assertIsNotNone(result)
