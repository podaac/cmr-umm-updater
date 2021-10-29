# pylint: disable=import-error, too-many-locals

"""
==============
umms_updater.py
==============

Generic command line tool that updates CMR UMM-S
profiles based on local json schema within a service

See usage information by running umms_updater.py -h

python umms_updater.py
-f netcdf_cmr_umm_s.json -p POCLOUD -e uat -cu cmr_user -cp cmr_pass
"""

import re
import json
import logging
import argparse
import time
import backoff
import requests

from podaac.umms_updater.util import svc_update
from podaac.umms_updater.util import token_req
from podaac.umms_updater.util import create_assoc


def parse_args():
    """
    Parses the program arguments
    Returns
    -------
    args
    """

    parser = argparse.ArgumentParser(
        description='Update CMR with latest profile',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-f', '--jfilename',
                        help='UMM-S file: '
                             'JSON file containing UMM-S profile'
                             'schema to be submitted to CMR for'
                             ' creation or update.',
                        required=True,
                        metavar='filename.json')

    parser.add_argument('-p', '--provider',
                        help='A provider ID identifies a provider and is'
                             'composed of a combination of upper case'
                             ' letters, digits, and underscores.'
                             'The maximum length is 10 characters.'
                             'Concept ID is provided if UMM-S record already'
                             'exists and needs to be updated.',
                        required=True,
                        default='POCLOUD',
                        metavar='POCLOUD')

    parser.add_argument('-e', '--env',
                        help='CMR environment used to request token '
                             'and pull results from.',
                        required=True,
                        metavar='uat or ops')

    parser.add_argument('-cu', '--cmr_user',
                        help='CMR Username to be used to request token.',
                        required=True,
                        metavar='ssm.get_parameter, '
                                'parameter["Parameter"]["urs_user"]')

    parser.add_argument('-cp', '--cmr_pass',
                        help='CMR Username to be used to request token.',
                        required=True,
                        metavar='ssm.get_parameter, '
                                'parameter["Parameter"]["urs_password"]')

    parser.add_argument('-t', '--token',
                        help='CMR UMM token string.',
                        default=None,
                        required=False,
                        metavar='')

    parser.add_argument('-d', '--debug', action='store_true',
                        help='Set logging to debug',
                        required=False)

    parser.add_argument('-a', '--assoc',
                        help='Association concept ID or file containing'
                             ' many concept IDs to be associated'
                             ' with UMM-S provided.',
                        required=False,
                        default=None,
                        metavar='associations.txt')

    args = parser.parse_args()
    return args


def create_native_id(provider, umms_json):
    """
    Assigned native_id based on provider and
    snake_case version of service Name field.

    Parameters
    ----------
    umms_json : json
    provider : string
    Returns
    -------
    new_nid : string
    """
    def snake_case(service_name):
        service_name_ns = re.sub(r"\s+", '_', service_name)
        return service_name_ns.lower()
    # noinspection PyUnresolvedReferences
    svc_name = umms_json['Name']
    new_nid = provider + "_" + snake_case(svc_name)
    return new_nid


@backoff.on_predicate(backoff.fibo, lambda x: x is None, max_tries=10)
def pull_concept_id(cmr_env, provider, native_id):
    """
    Uses constructed native_id, cmr environment and provider string to
    pull concept_id for UMM-S record on CMR.

    Parameters
    ----------
    cmr_env : string
    provider : string
    native_id : string

    Returns
    -------
    """

    url_prefix = svc_update.cmr_environment_url(cmr_env)
    url = url_prefix + f"/search/services.json" \
                       f"?provider={provider}&native_id={native_id}"
    req = requests.get(url)
    service = json.loads(req.text)

    if service['hits'] == 1:
        for svc in service['items']:
            concept_id = svc['concept_id']
            return concept_id
    elif service['hits'] > 1:
        raise Exception('Provider and Native ID are not unique, '
                        'more than 1 service returned.')
    else:
        # No concept-id exists, UMM-S record does not exist within CMR
        return None


# pylint: disable=too-many-statements
def main(args):
    """
    Perfoms update to cmr and logs profile update.
    See `cmr_umms_updater.py -h` for usage information.

    Parameters
    ----------
    args Arguments passed to the program
    Returns
    -------
    """

    if args.debug is True:
        service_log_level = logging.DEBUG
    else:
        service_log_level = logging.INFO
    logging.basicConfig(level=service_log_level)
    logger = logging.getLogger('podaac')
    logger.setLevel(level=service_log_level)
    logging.info("Starting UMM-S update")

    if args.token is None:
        current_token = token_req.token(args.env, args.cmr_user, args.cmr_pass)
    else:
        # For local testing
        current_token = args.token
    provider = args.provider
    header = {
        'Content-type': "application/vnd.nasa.cmr.umm+json;version=1.3.4",
        'Echo-Token': str(current_token),
    }

    with open(args.jfilename) as json_file:
        local_umms = json.load(json_file)

        # construct native ID
        native_id = create_native_id(provider, local_umms)
        logging.info("native_id: %s", native_id)
        # check if UMM-S record is currently within CMR
        concept_id = pull_concept_id(args.env, provider, native_id)
        # concept_id could not be found, UMM-S record is not within CMR
        if concept_id is None:
            logging.info("No CMR profile found. Creating new UMM-S record...")
            svc_update.create_service(
                args.env, local_umms, provider, native_id, header
            )
            new_concept_id = pull_concept_id(args.env, provider, native_id)
            logging.info("concept_id: %s", new_concept_id)
            logging.info("New CMR UMM-S Profile:")
            updated_umms = svc_update.get_current_service(
                args.env, new_concept_id
            )
            logging.info(json.dumps(
                updated_umms,
                sort_keys=True,
                indent=4,
            ))
            # check for associations to be made with UMM-S profile
            if args.assoc is not None:
                create_assoc.create_association(
                    args.env, new_concept_id, current_token, args.assoc
                )
        # concept_id was found,
        # local UMM-S record and CMR UMM-S to be compared for possible update
        else:
            logging.info("concept_id: %s", concept_id)
            # Display current CMR UMM-S profile
            current_umms = svc_update.get_current_service(args.env, concept_id)
            logging.info("CMR UMM-S Profile:")
            logging.info(json.dumps(
                current_umms,
                sort_keys=True,
                indent=4,
            ))
            # Display local UMM-S profile
            logging.info("Local UMM-S Profile:")
            logging.info(json.dumps(
                local_umms,
                sort_keys=True,
                indent=4,
            ))
            # Compare CMR UMM-S to locally maintained UMM-S profile
            if sorted(current_umms.items()) == sorted(local_umms.items()):
                logging.info("CMR and local profiles match, no update needed.")
                logging.info("Synchronize associations...")
                if args.assoc is not None:
                    create_assoc.sync_association(args.env, concept_id, current_token, args.assoc)
            else:
                logging.info("Updating CMR UMM-S profile...")

                svc_update.create_service(
                    args.env, local_umms, provider, native_id, header
                )
                logging.info("Updated CMR Profile:")
                # Need to sleep 10 seconds so there is time for the cmr to update.
                time.sleep(10)
                updated_umms = svc_update.get_current_service(
                    args.env, concept_id
                )
                logging.info(json.dumps(
                    updated_umms,
                    sort_keys=True,
                    indent=4,
                ))
                # check for associations to be made with UMM-S profile
                if args.assoc is not None:
                    create_assoc.sync_association(
                        args.env, concept_id, current_token, args.assoc
                    )


def run():
    """
    Run from command line.

    Returns
    -------
    """

    _args = parse_args()
    main(_args)


if __name__ == '__main__':
    run()
