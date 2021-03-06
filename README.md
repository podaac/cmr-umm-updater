# cmr-publish-umms-action
Github Action to publish UMM-S and UMM-T collection associations to CMR.

## Project Structure

The UMM-S JSON file should be in a folder called `cmr` in the root 
directory of the repo. Collection association files should be in the 
`cmr` folder and should be named `${env}_associations.txt` where 
`${env}` is the name of the environment (`uat`, `ops`, ...)

## Inputs

### `umm-s-json`

**Required** The name of the JSON UMM-S file.

### `provider`

**Required** The CMR provider ID.

### `env`

**Required** The name of the environment to publish this UMM-S change 
to. Should be `uat`, `sit`, or `ops`

### `version`

**Required** The version of the service. Will be substituted in to the 
UMM-S JSON before pushing to CMR.

### `timeout`
**Optional** API request timeout length in seconds.

## Environment variables

**Required** Either cmr_user and cmr_pass or token for each environment `sit` `uat` `ops`

### `cmr_user`

A Github secret containing CMR username. We recommend this 
is stored in a Github Secret.

### `cmr_pass`

A Github secret containing CMR password. We recommend this 
is stored in a Github Secret.

### `LAUNCHPAD_TOKEN_SIT`

A Github secret containing Launchpad token for sit. We recommend this 
is stored in a Github Secret.

### `LAUNCHPAD_TOKEN_UAT`

A Github secret containing Launchpad token for uat. We recommend this 
is stored in a Github Secret.

### `LAUNCHPAD_TOKEN_OPS`

A Github secret containing Launchpad token for ops. We recommend this 
is stored in a Github Secret.

## Example usage

```yaml
- uses: actions/checkout@v2
- name: UMM-S Updater Step
  id: umm-s-updater
  uses: podaac/cmr-umm-updater@0.0.1
  with:
    umm-s-json: 'cmr/umm_s.json'
    provider: 'POCLOUD'
    env: 'uat'
    version: '1.2.3'
  env:
    cmr_user: ${{secrets.CMR_USER}}
    cmr_pass: ${{secrets.CMR_PASS}}
    LAUNCHPAD_TOKEN_SIT: ${{secrets.LAUNCHPAD_TOKEN_SIT}}
    LAUNCHPAD_TOKEN_UAT: ${{secrets.LAUNCHPAD_TOKEN_UAT}}
    LAUNCHPAD_TOKEN_OPS: ${{secrets.LAUNCHPAD_TOKEN_OPS}}
```
