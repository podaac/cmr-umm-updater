#!/usr/bin/env bash

set -Eeo pipefail

file=$1
provider=$2
env=$3
version=$4
# ":-30" means If not set, use 30 as default
timeout=${5:-30}
disable_removal=$6
umm_type=$7

# Replace version placeholder with actual version
jq --arg a $version '.Version = $a' $file > "cmr/cmr.json"

# Replace Harmony URL placeholder with Harmony URL based on env
if [[ $env == "sit" || $env == "uat" ]]; then
  jq --arg a "https://harmony.uat.earthdata.nasa.gov" '.URL.URLValue = $a' cmr/cmr.json > cmr/cmr.json.tmp && mv cmr/cmr.json.tmp cmr/cmr.json
fi

if [[ $disable_removal == "true" && $umm_type == "umm-s" ]]; then
  if [[ "${LAUNCHPAD_TOKEN_SIT}" ]] && [[ $env == "sit" ]]; then
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_SIT -to $timeout -r
  elif [[ "${LAUNCHPAD_TOKEN_UAT}" ]] && [[ $env == "uat" ]]; then
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_UAT -to $timeout -r
  elif [[ "${LAUNCHPAD_TOKEN_OPS}" ]] && [[ $env == "ops" ]]; then
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_OPS -to $timeout -r
  else
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -cu $cmr_user -cp $cmr_pass -to $timeout -r
  fi
elif [[ $disable_removal == "false" && $umm_type == "umm-s" ]]; then
  if [[ "${LAUNCHPAD_TOKEN_SIT}" ]] && [[ $env == "sit" ]]; then
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_SIT -to $timeout
  elif [[ "${LAUNCHPAD_TOKEN_UAT}" ]] && [[ $env == "uat" ]]; then
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_UAT -to $timeout
  elif [[ "${LAUNCHPAD_TOKEN_OPS}" ]] && [[ $env == "ops" ]]; then
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_OPS -to $timeout
  else
    umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -cu $cmr_user -cp $cmr_pass -to $timeout
  fi
elif [[ $disable_removal == "true" && $umm_type == "umm-t" ]]; then
  if [[ "${LAUNCHPAD_TOKEN_SIT}" ]] && [[ $env == "sit" ]]; then
    ummt_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_SIT -to $timeout -r
  elif [[ "${LAUNCHPAD_TOKEN_UAT}" ]] && [[ $env == "uat" ]]; then
    ummt_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_UAT -to $timeout -r
  elif [[ "${LAUNCHPAD_TOKEN_OPS}" ]] && [[ $env == "ops" ]]; then
    ummt_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_OPS -to $timeout -r
  else
    ummt_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -cu $cmr_user -cp $cmr_pass -to $timeout -r
  fi
elif [[ $disable_removal == "false" && $umm_type == "umm-t" ]]; then
  if [[ "${LAUNCHPAD_TOKEN_SIT}" ]] && [[ $env == "sit" ]]; then
    ummt_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_SIT -to $timeout
  elif [[ "${LAUNCHPAD_TOKEN_UAT}" ]] && [[ $env == "uat" ]]; then
    ummt_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_UAT -to $timeout
  elif [[ "${LAUNCHPAD_TOKEN_OPS}" ]] && [[ $env == "ops" ]]; then
    ummt_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -t $LAUNCHPAD_TOKEN_OPS -to $timeout
  else
    ummt_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p ${provider} -e ${env} -cu $cmr_user -cp $cmr_pass -to $timeout
  fi
fi
