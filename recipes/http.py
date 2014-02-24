from urlparse import urlparse
import httplib


def __do_http_req(method, url, headers, payload):
    """

    @rtype : response
    """
    parsed_url = urlparse(url)
    con = httplib.HTTPConnection(parsed_url.netloc)
    con.request(method, parsed_url.path, payload, headers)
    return con.getresponse()


def get(url, headers):
    """

    @rtype : response
    """
    return __do_http_req("GET", url, headers, None)


def delete(url, headers):
    """

    @rtype : response
    """
    return __do_http_req("DELETE", url, headers, None)


def __put(url, headers):
    """

    @rtype : response
    """
    return __do_http_req("PUT", url, headers, None)


def post(url, headers, payload):
    """

    @rtype : response
    """
    return __do_http_req("POST", url, headers, payload)
