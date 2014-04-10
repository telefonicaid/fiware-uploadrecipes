from urlparse import urlparse
import httplib


def __do_http_req(method, url, headers, payload):
    """
    Generate an http request
    @rtype : response obtained
    """
    parsed_url = urlparse(url)
    con = httplib.HTTPConnection(parsed_url.netloc)
    con.request(method, parsed_url.path, payload, headers)
    return con.getresponse()


def get(url, headers):
    """
    GET request
    @rtype : response obtained
    """
    return __do_http_req("GET", url, headers, None)


def delete(url, headers):
    """
    DELETE request
    @rtype : response obtained
    """
    return __do_http_req("DELETE", url, headers, None)


def put(url, headers, payload):
    """
    PUT request
    @rtype : response obtained
    """
    return __do_http_req("PUT", url, headers, payload)


def post(url, headers, payload):
    """
    POST request
    @rtype : response obtained
    """
    return __do_http_req("POST", url, headers, payload)
