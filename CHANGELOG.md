# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Add UMM version argument**
  - Add umm version argument to set the desired umm version
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.5.0]

### Added
- **Add Association file optional**
  - Make association file optional when using umm updater

## [0.4.0]

### Added
- **Add UMM-T**
  - Add umm-t updater as an option when calling umm updater
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.3.0]

### Added
### Changed
- [issues/16](https://github.com/podaac/cmr-umm-updater/issues/16) Switched to using multi container Docker build so `gcc` can be used during build but is not included in final image
### Deprecated
### Removed
### Fixed
### Security

## [0.2.3]

### Added
### Changed
- **fix-push-tag**
  - Build pipeline manually pushes tag rather than use action-push-tag
### Deprecated
### Removed
### Fixed
### Security

## [0.2.2]

### Added
- **PODAAC-4657**
  - Added argument to disable association removal from CMR during association sync
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.2.1]

### Added
- Timeout argument in umm updater to control api request timeout
- [issue-9](https://github.com/podaac/cmr-umm-updater/issues/9): Change token header to Authorization

### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.2.0]

### Added
- Updated dev tool for launchpad token made cli accept user and pass or token

## [0.1.1]

### Changed
- Removed poetry from docker image of action
- Use python slim as base Docker image instead of alpine


## [0.1.0]

### Added
- Initial commit of UMM-S updater Github Action
### Changed
### Deprecated
### Removed
### Fixed
### Security
