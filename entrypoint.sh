#!/bin/bash -l

set -Exo pipefail
set +x

file=$1
provider=$2
env=$3
version=$4

# Replace version placeholder with actual version
jq --arg a $version '.Version = $a' $file > "cmr/cmr.json"

# Replace Harmony URL placeholder with Harmony URL based on env
if [[ $env == "sit" || $env == "uat" ]]; then
  jq --arg a "https://harmony.uat.earthdata.nasa.gov" '.URL.URLValue = $a' cmr/cmr.json > cmr/cmr.json.tmp && mv cmr/cmr.json.tmp cmr/cmr.json
fi

umms_updater -d -f cmr/cmr.json -a cmr/${env}_associations.txt -p POCLOUD -e ${env} -cu $cmr_user -cp $cmr_pass

set -x
