"""
==============
svc_update.py
==============

Helper script for calling CMR UMM-S for:
return current UMM-S profile (getCurrentService)
create a new or update UMM-S profile (createService)
remove current UMM-S profile (deleteService)
"""

import logging
import backoff
from requests import put, get, delete, exceptions

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
def get_current_service(cmr_env, concept_id):
    """
    Pull current UMM-S profile
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
        req = get(url_prefix + f"/search/"
                  f"services.umm_json"
                  f"?concept_id={concept_id}&pretty=true")
        LOGGER.debug("Response text from get_current_service: %s", req.text)
        current_umms = req.json()
    except exceptions.HTTPError as err:
        raise SystemExit(err) from err
    try:
        current_umms = current_umms['items'][0]['umm']
    except (IndexError, KeyError) as inderr:
        LOGGER.debug("%s, CMR has no service with a UMM-S record containing "
                     "this concept_id, one will be created.", inderr)
        current_umms = None
    return current_umms


def create_service(cmr_env, local_umms, provider, native_id, header):
    """
    Creates new UMM-S Service and returns confirmation xml
    Parameters
    ----------
    cmr_env : string
    local_umms : json object
    provider : string
    native_id : string
    header : json object

    Returns
    -------
    XML
    """

    url_prefix = cmr_environment_url(cmr_env)
    LOGGER.debug("Environment url-prefix"
                 " used to create_service: %s", url_prefix)
    url = url_prefix + f"/ingest/providers/" \
                       f"{provider}/services/{native_id}"
    LOGGER.debug("URL used to create_service: %s", url)
    try:
        req = put(url, json=local_umms, headers=header)
        LOGGER.info("Response from create_service: %s", req.text)
        req.raise_for_status()
    except exceptions.HTTPError as err:
        LOGGER.exception("Error creating service")
        raise SystemExit(err) from err
    return req


def delete_service(cmr_env, provider, native_id, header):
    """
    Deletes existing UMM-S Service and returns confirmation xml
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
    LOGGER.debug("Environment url-prefix used to delete_service: %s",
                 url_prefix)
    url = url_prefix + f"/ingest/providers/" \
                       f"{provider}/services/{native_id}"
    LOGGER.info("URL used to delete_service: %s", url)
    try:
        req = delete(url, headers=header)
        LOGGER.info("Response from delete_service: %s", req.text)
        req.raise_for_status()
    except exceptions.HTTPError as err:
        LOGGER.exception("Error deleting service")
        raise SystemExit(err) from err
