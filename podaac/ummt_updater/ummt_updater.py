# pylint: disable=import-error, too-many-locals

"""
==============
ummt_updater.py
==============

Generic command line tool that updates CMR UMM-T
profiles based on local json schema within a tool

See usage information by running ummt_updater.py -h

python ummt_updater.py
-f netcdf_cmr_umm_t.json -p POCLOUD -e uat -cu cmr_user -cp cmr_pass
"""

import re
import json
import logging
import argparse
import time
import backoff
import requests

from podaac.ummt_updater.util import tool_update
from podaac.ummt_updater.util import token_req
from podaac.ummt_updater.util import create_assoc


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
                        help='UMM-T file: '
                             'JSON file containing UMM-T profile'
                             'schema to be submitted to CMR for'
                             ' creation or update.',
                        required=True,
                        metavar='filename.json')

    parser.add_argument('-p', '--provider',
                        help='A provider ID identifies a provider and is'
                             'composed of a combination of upper case'
                             ' letters, digits, and underscores.'
                             'The maximum length is 10 characters.'
                             'Concept ID is provided if UMM-T record already'
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
                             ' with UMM-T provided.',
                        required=False,
                        default=None,
                        metavar='associations.txt')

    args = parser.parse_args()
    return args


def create_native_id(provider, ummt_json):
    """
    Assigned native_id based on provider and
    snake_case version of tool Name field.

    Parameters
    ----------
    ummt_json : json
    provider : string
    Returns
    -------
    new_nid : string
    """
    def snake_case(tool_name):
        tool_name_ns = re.sub(r"\s+", '_', tool_name)
        return tool_name_ns.lower()
    # noinspection PyUnresolvedReferences
    tool_name = ummt_json['Name']
    new_nid = provider + "_" + snake_case(tool_name)
    return new_nid


@backoff.on_predicate(backoff.fibo, lambda x: x is None, max_tries=10)
def pull_concept_id(cmr_env, provider, native_id):
    """
    Uses constructed native_id, cmr environment and provider string to
    pull concept_id for UMM-T record on CMR.

    Parameters
    ----------
    cmr_env : string
    provider : string
    native_id : string

    Returns
    -------
    """

    url_prefix = tool_update.cmr_environment_url(cmr_env)
    url = url_prefix + f"/search/tools.json" \
                       f"?provider={provider}&native_id={native_id}"
    req = requests.get(url)
    tool = json.loads(req.text)

    if tool['hits'] == 1:
        for svc in tool['items']:
            concept_id = svc['concept_id']
            return concept_id
    elif tool['hits'] > 1:
        raise Exception('Provider and Native ID are not unique, '
                        'more than 1 tool returned.')
    else:
        # No concept-id exists, UMM-T record does not exist within CMR
        return None


LOGGER = logging.getLogger(__name__)


# pylint: disable=too-many-statements
def main(args):
    """
    Perfoms update to cmr and logs profile update.
    See `cmr_ummt_updater.py -h` for usage information.

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
    logging.info("Starting UMM-T update")

    if args.token is None:
        current_token = token_req.token(args.env, args.cmr_user, args.cmr_pass)
    else:
        # For local testing
        current_token = args.token
    provider = args.provider
    header = {
        'Content-type': "application/vnd.nasa.cmr.umm+json;version=1.0",
        'Echo-Token': str(current_token),
    }

    with open(args.jfilename) as json_file:
        local_ummt = json.load(json_file)

        # construct native local_ummt
        native_id = create_native_id(provider, local_ummt)
        logging.info("native_id: %s", native_id)

        concept_id = pull_concept_id(args.env, provider, native_id)

        if concept_id is None:

            logging.info("No CMR profile found. Creating new UMM-T record...")

            tool_update.create_tool(
                args.env, local_ummt, provider, native_id, header
            )
            new_concept_id = pull_concept_id(args.env, provider, native_id)

            logging.info("concept_id: %s", concept_id)
            logging.info("New CMR UMM-T Profile:")

            updated_ummt = tool_update.get_current_tool(
                args.env, new_concept_id
            )

            logging.info(json.dumps(
                updated_ummt,
                sort_keys=True,
                indent=4,
            ))

            # check for associations to be made with UMM-T profile
            if args.assoc is not None:
                create_assoc.create_association(
                    args.env, new_concept_id, current_token, args.assoc
                )
        else:
            logging.info("concept_id: %s", concept_id)

            # Display current CMR UMM-T profile
            current_ummt = tool_update.get_current_tool(args.env, concept_id)
            logging.info("CMR UMM-T Profile:")
            logging.info(json.dumps(
                current_ummt,
                sort_keys=True,
                indent=4,
            ))
            # Display local UMM-T profile
            logging.info("Local UMM-T Profile:")
            logging.info(json.dumps(
                local_ummt,
                sort_keys=True,
                indent=4,
            ))
            # Compare CMR UMM-T to locally maintained UMM-T profile
            if sorted(current_ummt.items()) == sorted(local_ummt.items()):
                logging.info("CMR and local profiles match, no update needed.")
                logging.info("Synchronize associations...")
                if args.assoc is not None:
                    create_assoc.sync_association(args.env, concept_id, current_token, args.assoc)
            else:
                logging.info("Updating CMR UMM-T profile...")

                tool_update.create_tool(
                    args.env, local_ummt, provider, native_id, header
                )
                logging.info("Updated CMR Profile:")

                # Need to sleep 10 seconds so there is time for the cmr to update.
                time.sleep(10)
                updated_ummt = tool_update.get_current_tool(
                    args.env, concept_id
                )

                logging.info(json.dumps(
                    updated_ummt,
                    sort_keys=True,
                    indent=4,
                ))

                # check for associations to be made with UMM-T profile
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
