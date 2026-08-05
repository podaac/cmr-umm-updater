# cmr-publish-umm-action
Github Action to publish UMM-S and UMM-T collection associations to CMR.

## Project Structure

The UMM JSON file should be in a folder called `cmr` in the root
directory of the repo. Collection association files should be in the
`cmr` folder and should be named `${env}_associations.txt` where
`${env}` is the name of the environment (`uat`, `ops`, ...)

## Inputs

### `umm-json`

**Required** The name of the JSON UMM file.

### `provider`

**Required** The CMR provider ID.

### `env`

**Required** The name of the environment to publish this UMM change
to. Should be `uat`, `sit`, or `ops`

### `version`

**Required** The version of the service. Will be substituted in to the
UMM JSON before pushing to CMR.

### `timeout`
**Optional** API request timeout length in seconds.

### `disable_removal`
Disable CMR association removal during sync event

### `umm_type`
Either update a umm-s or umm-t in umm defaults to umm-s

### `use_associations`
To use a association file to add collections to umm

### `umm_version`
Version of the umm schema to use during updates. Defaults to '1.3.4'

### `url_value`
Value to substitute for the `.URL.URLValue` key in the umm record. Defaults to environment specific harmony URL

## Environment variables

**Required** Either cmr_user and cmr_pass or token for each environment `sit` `uat` `ops`

### `cmr_user`

A Github secret containing CMR username. We recommend this
is stored in a Github Secret.

### `cmr_pass`

A Github secret containing CMR password. We recommend this
is stored in a Github Secret.

### `LAUNCHPAD_TOKEN_SIT`

The Launchpad token for sit.  We recommend using the launchpad_token_dispenser lambda to generate this token.
Example: [Launchpad_token_generator](https://github.com/podaac/l2ss-py/blob/87fe7973ea88192b655ae56b25b2a5af74ffd77b/.github/workflows/build-pipeline.yml#L174)

### `LAUNCHPAD_TOKEN_UAT`

The Launchpad token for uat.  We recommend using the launchpad_token_dispenser lambda to generate this token.
Example: [Launchpad_token_generator](https://github.com/podaac/l2ss-py/blob/87fe7973ea88192b655ae56b25b2a5af74ffd77b/.github/workflows/build-pipeline.yml#L174)

### `LAUNCHPAD_TOKEN_OPS`

The Launchpad token for ops.  We recommend using the launchpad_token_dispenser lambda to generate this token.
Example: [Launchpad_token_generator](https://github.com/podaac/l2ss-py/blob/87fe7973ea88192b655ae56b25b2a5af74ffd77b/.github/workflows/build-pipeline.yml#L174)

## Example usage

```yaml
- uses: actions/checkout@v2
- name: UMM Updater Step
  id: umm-updater
  uses: podaac/cmr-umm-updater@0.0.4
  with:
    umm-s-json: 'cmr/umm.json'
    provider: 'POCLOUD'
    env: 'uat'
    version: '1.2.3'
    umm_type: 'umm-s'
  env:
    cmr_user: ${{secrets.CMR_USER}}
    cmr_pass: ${{secrets.CMR_PASS}}
    LAUNCHPAD_TOKEN_SIT: ${{ steps.launchpad_token_generator.outputs.result }}
    LAUNCHPAD_TOKEN_UAT: ${{ steps.launchpad_token_generator.outputs.result }}
    LAUNCHPAD_TOKEN_OPS: ${{ steps.launchpad_token_generator.outputs.result }}
```
