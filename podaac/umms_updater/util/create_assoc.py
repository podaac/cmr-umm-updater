# pylint: disable=import-error

"""
==============
token_req.py
==============

Helper script for building UMM-S associations
"""

import json
import logging
from requests import delete, get, post

from podaac.umms_updater.util import svc_update

LOGGER = logging.getLogger(__name__)


def get_association(association):
    """
    Get list of association concept ids from association file
    Parameters
    ----------
    association : string file with all associations
    Returns
    -------
    List string concept ids in association file
    """

    concept_ids = []
    if ".txt" in association:
        with open(association) as afile:
            assoc_concept_ids = afile.readlines()
        for assoc_concept_id in assoc_concept_ids:
            concept_ids.append(assoc_concept_id.strip('\n'))
    concept_ids.sort()
    return concept_ids


def current_association(concept_id, url_prefix, header, timeout=30):
    """
    Get list of association concept ids currently in CMR for a service
    Parameters
    ----------
    cmr_env : string environment of cmr
    concept_id : string concept id of service
    url_prefix : string url prefix
    Returns
    -------
    List of string with concept id or None
    """

    url = "{}/search/collections.umm_json?service_concept_id={}&page_size=2000".format(url_prefix, concept_id)
    resp = get(url, headers=header, timeout=timeout)
    if resp.status_code == 200:
        resp_json = json.loads(resp.text)
        concept_ids = []
        for item in resp_json.get('items'):
            concept_ids.append(item['meta']['concept-id'])
        concept_ids.sort()
        return concept_ids
    return None


def sync_association(cmr_env, concept_id, current_token, association, timeout=30, remove_association: bool=True):
    """
    Synchronize association file with cmr associations
    Parameters
    ----------
    cmr_env : string environment of cmr
    concept_id : string concept id of service
    current_token : string cmr token
    association : string file with all associations
    remove_association : bool to remove associations from cmr or not during sync
    Returns
    -------
    None
    """

    LOGGER.info("Synchronize associations...")
    url_prefix = svc_update.cmr_environment_url(cmr_env)
    header = {
        'Authorization': str(current_token),
    }

    current = current_association(concept_id, url_prefix, header, timeout=timeout)
    header["Content-type"] = "application/json"

    if current is None:
        LOGGER.info("Unable to get associations for concept_id: %s", concept_id)
        return
    new = get_association(association)

    if current != new:
        add = list(set(new) - set(current))
        remove = list(set(current) - set(new))

        for assoc_concept_id in add:
            resp = add_association(url_prefix, concept_id, assoc_concept_id, header, timeout=timeout)
            LOGGER.info("Add Association %s: response status: %s",
                        assoc_concept_id, resp.status_code)
            LOGGER.info("Response text from add_associations: %s", resp.text)
            if resp.status_code != 200:
                LOGGER.info("Failed add association: concept_id being associated "
                            "may not be valid: %s", assoc_concept_id)

        LOGGER.info("Allow association removal: %s", remove_association)
        for assoc_concept_id in remove and remove_association:
            resp = remove_association(url_prefix, concept_id, assoc_concept_id, header, timeout=timeout)
            LOGGER.info("Remove Association %s: response status: %s",
                        assoc_concept_id, resp.status_code)
            LOGGER.info("Response text from remove_associations: %s", resp.text)
            if resp.status_code != 200:
                LOGGER.info("Failed remove association: concept_id being associated "
                            "may not be valid: %s", assoc_concept_id)
    else:
        LOGGER.info("All association is the same")


def add_association(url_prefix, c_id, ac_id, header, timeout=30):
    """
    Add associations between
    Parameters
    ----------
    url_prefix : string url prefix
    c_id : string concept id of service
    ac_id : string association id
    header : string of head for request
    Returns
    -------
    Request response
    """

    url = url_prefix + f"/search/services/{c_id}/associations"
    assoc_concept_id_payload = f'[{{"concept_id": "{ac_id}"}}]'
    assoc_concept_id_payload = assoc_concept_id_payload.replace("\n", "")
    resp = post(url, json=json.loads(assoc_concept_id_payload),
                headers=header, timeout=timeout)
    return resp


def remove_association(url_prefix, c_id, ac_id, header, timeout=30):
    """
    Remove associations between
    Parameters
    ----------
    url_prefix : string url prefix
    c_id : string concept id of service
    ac_id : string association id
    header : string of head for request
    Returns
    -------
    Request response
    """

    url = url_prefix + f"/search/services/{c_id}/associations"
    assoc_concept_id_payload = f'[{{"concept_id": "{ac_id}"}}]'
    assoc_concept_id_payload = assoc_concept_id_payload.replace("\n", "")
    resp = delete(url, json=json.loads(assoc_concept_id_payload),
                  headers=header, timeout=timeout)
    return resp


def create_association(cmr_env, concept_id, current_token, association, timeout=30):
    """
    Create associations between
    Parameters
    ----------
    cmr_env : string
    concept_id : string
    current_token : string
    association : string
    Returns
    -------
    JSON object or None
    """

    header = {
        'Content-type': "application/json",
        'Authorization': str(current_token),
    }

    url_prefix = svc_update.cmr_environment_url(cmr_env)

    if ".txt" in association:
        with open(association) as afile:
            assoc_concept_ids = afile.readlines()
        for i, assoc_concept_id in enumerate(assoc_concept_ids, start=1):
            req = add_association(url_prefix, concept_id, assoc_concept_id, header, timeout=timeout)
            LOGGER.info("Association %s: %s, response status: %s",
                        i, assoc_concept_id, req.status_code)
            LOGGER.debug("Response text from build_associations: %s", req.text)
            if req.status_code != 200:
                LOGGER.info("Failed association: concept_id being associated "
                            "may not be valid: %s", assoc_concept_id)
    else:
        req = add_association(url_prefix, concept_id, association, header, timeout=timeout)
        LOGGER.info("Association response status: %s", req.status_code)
        LOGGER.debug("Response text from build_associations: %s", req.text)
    LOGGER.info("Associations complete")
