"""
==============
tool_update.py
==============

Helper script for calling CMR UMM-T for:
return current UMM-T profile (getCurrentService)
create a new or update UMM-T profile (createService)
remove current UMM-T profile (deleteService)
"""

import logging
from requests import put, get, delete, exceptions
import backoff

LOGGER = logging.getLogger(__name__)


def cmr_environment_url(env):
    """
    Determine ops or uat url prefix based on env string
    Parameters
    ----------
    env : string

    Returns
    -------
    url_prefix : string
    """
    # CMR OPS (Operations, also known as Production or PROD)
    if env.lower() == 'ops':
        url_prefix = "https://cmr.earthdata.nasa.gov"
    # CMR UAT (User Acceptance Testing)
    elif env.lower() == 'uat':
        url_prefix = "https://cmr.uat.earthdata.nasa.gov"
    else:
        raise Exception('CMR environment selection not recognized;'
                        ' Select uat or ops.')
    return url_prefix


@backoff.on_predicate(backoff.fibo, lambda x: x is None, max_tries=10)
def get_current_tool(cmr_env, concept_id, timeout=30):
    """
    Pull current UMM-T profile
    Parameters
    ----------
    cmr_env : string
    concept_id : string

    Returns
    -------
    JSON object or None
    """

    url_prefix = cmr_environment_url(cmr_env)
    try:
        url = "{}/search/tools.umm_json?concept_id={}&pretty=true".format(url_prefix, concept_id)
        req = get(url, timeout=timeout)
        LOGGER.debug("Response text from get_current_tool: %s", req.text)
        current_ummt = req.json()
    except exceptions.HTTPError as err:
        raise SystemExit(err) from err
    try:
        current_ummt = current_ummt['items'][0]['umm']
    except (IndexError, KeyError) as inderr:
        LOGGER.debug("%s, CMR has no tool with a UMM-T record containing "
                     "this concept_id, one will be created.", inderr)
        current_ummt = None
    return current_ummt


def create_tool(cmr_env, local_ummt, provider, native_id, header, timeout=30):
    """
    Creates new UMM-T Service and returns confirmation xml
    Parameters
    ----------
    cmr_env : string
    local_ummt : json object
    provider : string
    native_id : string
    header : json object

    Returns
    -------
    XML
    """

    url_prefix = cmr_environment_url(cmr_env)
    LOGGER.debug("Environment url-prefix"
                 " used to create_tool: %s", url_prefix)
    url = "{}/ingest/providers/{}/tools/{}".format(url_prefix, provider, native_id)
    LOGGER.debug("URL used to create_tool: %s", url)
    try:
        req = put(url, json=local_ummt, headers=header, timeout=timeout)
        LOGGER.info("Response from create_tool: %s", req.text)
        req.raise_for_status()
    except exceptions.HTTPError as err:
        LOGGER.exception("Error creating tool")
        raise SystemExit(err) from err
    return req


def delete_tool(cmr_env, provider, native_id, header, timeout=30):
    """
    Deletes existing UMM-T Service and returns confirmation xml
    Parameters
    ----------
    cmr_env : string
    provider : string
    native_id : string
    header : json object

    Returns
    -------
    XML
    """

    url_prefix = cmr_environment_url(cmr_env)
    LOGGER.debug("Environment url-prefix used to delete_tool: %s",
                 url_prefix)
    url = "{}/ingest/providers/{}/tools/{}".format(url_prefix, provider, native_id)
    LOGGER.info("URL used to delete_tool: %s", url)
    try:
        req = delete(url, headers=header, timeout=timeout)
        LOGGER.info("Response from delete_tool: %s", req.text)
        req.raise_for_status()
    except exceptions.HTTPError as err:
        LOGGER.exception("Error deleting tool")
        raise SystemExit(err) from err
