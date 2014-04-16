# coding=utf-8
from mockito import *
from django.test import TestCase
from recipes import mpuppet, models, loggers, http

'''
class MIPuppetMasterTest(TestCase):

    def test_update_master_server(self):
        self.my_key = "key"
        self.my_value = "value"
        self.value_mocked = mock()
        uri = "update_uri"
        headers = {"Content-Type": "application/json"}
        payload = "payload"
        msg = mock()
        response = mock()
        self.data_mocked = mock()
        mocked_query = models.Data.objects.create(key=self.my_key,
                                                  value=self.my_value)
        when(self.data_mocked).get(key=self.my_key).thenReturn(
            self.value_mocked)
        when(self.data_mocked).objects.thenReturn(mocked_query)
        when(loggers).set_info_log(msg).thenReturn(None)
        when(loggers).set_error_log(msg).thenReturn(None)
        when(http).post(uri, headers, payload).thenReturn(response)
        when(response).status().thenReturn(200)
        self.pupet = mpuppet.MIPuppetMaster("test_name", "svn", uri)
        result = self.pupet.update_master_server
        self.assertEqual(result, None)
'''
