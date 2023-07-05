#!/usr/bin/env bash

set -Eeo pipefail

file=$1
provider=$2
env=$3
version=$4
timeout=${5:-30}
disable_removal=$6
umm_type=$7
use_associations=${8:-true}

# Replace version placeholder with actual version
jq --arg a $version '.Version = $a' "$file" > "cmr/cmr.json"

# Replace Harmony URL placeholder with Harmony URL based on env
if [[ $env == "sit" || $env == "uat" ]]; then
  jq --arg a "https://harmony.uat.earthdata.nasa.gov" '.URL.URLValue = $a' cmr/cmr.json > cmr/cmr.json.tmp && mv cmr/cmr.json.tmp cmr/cmr.json
fi

launchpad_token=""
if [[ $env == "sit" && -n "${LAUNCHPAD_TOKEN_SIT}" ]]; then
  launchpad_token=$LAUNCHPAD_TOKEN_SIT
elif [[ $env == "uat" && -n "${LAUNCHPAD_TOKEN_UAT}" ]]; then
  launchpad_token=$LAUNCHPAD_TOKEN_UAT
elif [[ $env == "ops" && -n "${LAUNCHPAD_TOKEN_OPS}" ]]; then
  launchpad_token=$LAUNCHPAD_TOKEN_OPS
fi

# Build the umms_updater/ummt_updater command
command="umms_updater"
if [[ $umm_type == "umm-t" ]]; then
  command="ummt_updater"
fi

# Append additional options based on disable_removal value
#if [[ $disable_removal == "true" ]]; then
#  command+=" -r"
#fi

# Execute the command
if [[ -n $launchpad_token ]]; then
  if [[ $use_associations == "true" ]]; then
    "$command" -r -d -f "cmr/cmr.json" -a "cmr/${env}_associations.txt" -p "$provider" -e "$env" -t "$launchpad_token" -to "$timeout" -cu "$cmr_user" -cp "$cmr_pass"
  else
    "$command" -r -d -f "cmr/cmr.json" -p "$provider" -e "$env" -t "$launchpad_token" -to "$timeout" -cu "$cmr_user" -cp "$cmr_pass"
  fi
else
  if [[ $use_associations == "true" ]]; then
    "$command" -r -d -f "cmr/cmr.json" -a "cmr/${env}_associations.txt" -p "$provider" -e "$env" -cu "$cmr_user" -cp "$cmr_pass" -to "$timeout"
  else
    "$command" -r -d -f "cmr/cmr.json" -p "$provider" -e "$env" -cu "$cmr_user" -cp "$cmr_pass" -to "$timeout"
  fi
fi