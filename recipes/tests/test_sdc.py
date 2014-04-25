# coding=utf-8
from django.test import TestCase
from recipes import kingstion, loggers, sdc, productrequest
from mockito import *


class ProductRequestTest(TestCase):
    def setUp(self):
        self.name = "name"
        self.version = "version"
        self.desc = "desc"
        self.token = "token"
        self.tenant = mock()
        self.attr = mock()
        self.meta = mock()
        msg = mock()
        when(loggers).set_info_log(msg).thenReturn(None)
        when(loggers).set_error_log(msg).thenReturn(None)
        when(kingstion).get_tenant_from_token(self.token).thenReturn(
            self.tenant)
        self.sdc = sdc.Catalog(self.name, self.version, self.desc, self.token)

    def test_set_attributes(self):
        attr = mock()
        result = self.sdc.set_attributes(attr)
        self.assertEqual(result, attr)

    def test_get_metadata(self):
        metadata = "installator=manager;open_ports=22 tcp;cloud=yes;" \
                   "open_ports_udp=udp;repository=repo;public=no;" \
                   "cookbook_url=uri;tenant_id=tenant;image=sos sos2;" \
                   "dependencies=depends"
        manager = "manager"
        uri = "uri"
        sos = ["sos", "sos2"]
        depend = "dependencies=depends"
        tcp = "tcp"
        udp = "udp"
        repo = "repo"
        token = "token"
        when(kingstion).get_tenant_from_token(token).thenReturn("tenant")
        result = self.sdc.get_metadata(manager, uri, sos, depend, tcp, udp,
                                       repo, token)
        self.assertEqual(result, metadata)

    def test_remove_catalog_error_release(self):
        g = mock()
        gr = mock()
        err = mock()
        when(productrequest).ProductRequest(self.token,
                                            self.tenant).thenReturn(g)
        when(productrequest).ProductReleaseRequest(self.token,
                                                   self.tenant).thenReturn(gr)
        when(gr).delete_product_release(self.name, self.version).thenReturn(
            err)
        when(g).delete_product(self.name).thenReturn(None)
        result = self.sdc.remove_catalog()
        self.assertIsNotNone(result)

    def test_remove_catalog_error_product(self):
        g = mock()
        gr = mock()
        err = mock()
        when(productrequest).ProductRequest(self.token,
                                            self.tenant).thenReturn(g)
        when(productrequest).ProductReleaseRequest(self.token,
                                                   self.tenant).thenReturn(gr)
        when(gr).delete_product_release(self.name, self.version).thenReturn(
            None)
        when(g).delete_product(self.name).thenReturn(err)
        result = self.sdc.remove_catalog()
        self.assertIsNotNone(result)

    def test_remove_catalog_error(self):
        g = mock()
        gr = mock()
        err = mock()
        when(productrequest).ProductRequest(self.token,
                                            self.tenant).thenReturn(g)
        when(productrequest).ProductReleaseRequest(self.token,
                                                   self.tenant).thenReturn(gr)
        when(gr).delete_product_release(self.name, self.version).thenReturn(
            err)
        when(g).delete_product(self.name).thenReturn(err)
        result = self.sdc.remove_catalog()
        self.assertIsNotNone(result)

    def test_remove_catalog(self):
        g = mock()
        gr = mock()
        when(productrequest).ProductRequest(self.token,
                                            self.tenant).thenReturn(g)
        when(productrequest).ProductReleaseRequest(self.token,
                                                   self.tenant).thenReturn(gr)
        when(gr).delete_product_release(self.name, self.version).thenReturn(
            None)
        when(g).delete_product(self.name).thenReturn(None)
        result = self.sdc.remove_catalog()
        self.assertIsNone(result)


    def test_add_catalog_exception(self):
        g = mock()
        gr = mock()
        product = mock()
        when(productrequest).ProductRequest(self.token,
                                            self.tenant).thenReturn(g)
        when(productrequest).ProductReleaseRequest(self.token,
                                                   self.tenant).thenReturn(gr)
        when(g).add_product(self.name, self.desc, self.attr,
                            self.meta).thenReturn(None, product)
        when(gr).add_product_release(product, self.name,
                                     self.version).thenReturn(None)
        result = self.sdc.add_catalog()
        self.assertIsNotNone(result)


    def test_add_catalog_error_product(self):
        gc = mock()
        grr = mock()
        product = mock()
        when(productrequest).ProductRequest(self.token,
                                            self.tenant).thenReturn(gc)
        when(productrequest).ProductReleaseRequest(self.token,
                                                   self.tenant).thenReturn(grr)

        when(kingstion).get_tenant_from_token("token").thenReturn("tenant")

        when(gc).add_product(any(), any(), any(), any()).thenReturn((mock(), product))
        when(grr).add_product_release(product, self.name,
                                     self.version).thenReturn(None)
        result = self.sdc.add_catalog()
        self.assertIsNotNone(result)

    def test_add_catalog_error_request(self):
        gc = mock()
        grr = mock()
        product = mock()
        when(productrequest).ProductRequest(self.token,
                                            self.tenant).thenReturn(gc)
        when(productrequest).ProductReleaseRequest(self.token,
                                                   self.tenant).thenReturn(grr)

        when(kingstion).get_tenant_from_token("token").thenReturn("tenant")

        when(gc).add_product(any(), any(), any(), any()).thenReturn((None, product))
        when(grr).add_product_release(product, self.name,
                                     self.version).thenReturn(mock())
        result = self.sdc.add_catalog()
        self.assertIsNotNone(result)

    def test_add_catalog(self):
        gc = mock()
        grr = mock()
        product = mock()
        when(productrequest).ProductRequest(self.token,
                                            self.tenant).thenReturn(gc)
        when(productrequest).ProductReleaseRequest(self.token,
                                                   self.tenant).thenReturn(grr)

        when(kingstion).get_tenant_from_token("token").thenReturn("tenant")

        when(gc).add_product(any(), any(), any(), any()).thenReturn((None, product))
        when(grr).add_product_release(product, self.name,
                                     self.version).thenReturn(None)
        result = self.sdc.add_catalog()
        self.assertIsNone(result)
