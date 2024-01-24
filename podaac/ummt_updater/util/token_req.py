# pylint: disable=import-error

"""
==============
token_req.py
==============

Helper script for requesting a CMR token
"""

import json
import logging
import socket
from requests import post, exceptions

from podaac.ummt_updater.util import tool_update

LOGGER = logging.getLogger(__name__)


def token(cmr_env, cmr_user, cmr_pass):
    """
    Function for requesting a CMR token
    Returns
    -------
    current_token : string
    """

    url_prefix = tool_update.cmr_environment_url(cmr_env)
    url = url_prefix + "/legacy-services/rest/tokens"

    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)

    header = {
        'Accept': "application/json",
        'Content-type': "application/json"
    }

    ip_address = str(ip_addr)

    LOGGER.debug("Requesting token...")
    json_payload = f"{{\"token\":{{\"username\":\"{cmr_user}\"," \
                   f"\"password\":\"{cmr_pass}\",\"client_id\":\"client\"," \
                   f"\"user_ip_address\":\"{ip_address}\"}}}}"
    try:
        req = post(url, json=json.loads(json_payload), headers=header, timeout=120)
        LOGGER.debug("Response from request for token: %s", req.text)
        req.raise_for_status()
    except exceptions.HTTPError as err:
        raise SystemExit(err) from err
    token_json = req.json()
    current_token = token_json['token']['id']
    return current_token
