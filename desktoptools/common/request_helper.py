import logging
from pprint import pformat

__author__ = 'jbean'
import requests

logger = logging.getLogger(__name__)


def get_json(url, **kwargs):
    r = _get(url, **kwargs)
    return r.json()


def post_json(url, **kwargs):
    r = _post(url, **kwargs)
    return r.json()


def _process_request(kwargs, request):
    logger.debug("{} url: [{}]".format(request.request.method, request.url))
    if kwargs:
        logger.debug("{} kwargs: [{}]".format(request.request.method, pformat(kwargs)))
    # TODO: don't do this all the time, bring this up a few layers.
    request.raise_for_status()
    return request


def _post(url, **kwargs):
    """
    Post request
    @param url: url to send the request to
    @param args: arguments to append to the url
    @return: dictionary form of the response
    """
    request = requests.post(url, data=kwargs)
    return _process_request(kwargs, request)


def _get(url, **kwargs):
    """
    Post request
    @param url: url to send the request to
    @param args: arguments to append to the url
    @return: dictionary form of the response
    """
    request = requests.get(url, data=kwargs)
    return _process_request(kwargs, request)

