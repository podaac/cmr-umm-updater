#!/bin/bash -l

set -Exo pipefail
set +x

file=$1
provider=$2
env=$3
version=$4
timeout=${5:-30}
disable_removal=$6

# Replace version placeholder with actual version
jq --arg a $version '.Version = $a' $file > "cmr/cmr.json"

# Replace Harmony URL placeholder with Harmony URL based on env
if [[ $env == "sit" || $env == "uat" ]]; then
  jq --arg a "https://harmony.uat.earthdata.nasa.gov" '.URL.URLValue = $a' cmr/cmr.json > cmr/cmr.json.tmp && mv cmr/cmr.json.tmp cmr/cmr.json
fi

if disable_removal == 'true'; then
  if [[ "${LAUNCHPAD_TOKEN_SIT}" ]] && [[ $env == "sit" ]]; then
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_SIT -to $timeout -r
  elif [[ "${LAUNCHPAD_TOKEN_UAT}" ]] && [[ $env == "uat" ]]; then
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_UAT -to $timeout -r
  elif [[ "${LAUNCHPAD_TOKEN_OPS}" ]] && [[ $env == "ops" ]]; then
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_OPS -to $timeout -r
  else
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -cu $cmr_user -cp $cmr_pass -to $timeout -r
  fi
else
  if [[ "${LAUNCHPAD_TOKEN_SIT}" ]] && [[ $env == "sit" ]]; then
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_SIT -to $timeout
  elif [[ "${LAUNCHPAD_TOKEN_UAT}" ]] && [[ $env == "uat" ]]; then
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_UAT -to $timeout
  elif [[ "${LAUNCHPAD_TOKEN_OPS}" ]] && [[ $env == "ops" ]]; then
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_OPS -to $timeout
  else
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -cu $cmr_user -cp $cmr_pass -to $timeout
  fi
fi

set -x
