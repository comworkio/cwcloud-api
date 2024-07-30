# Contribution Guidelines

👋 Welcome to comwork cloud API! We're thrilled that you're interested in contributing to our project.

## Development

See the [README.md](./README.md) to see how to build and start the project.

## Versioning

In order to bump the version, you'll have to upgrade the [VERSION](./VERSION) file (only on the `main` branch when we're merging a set of new features and fix coming from the `develop` branch).

The docker images tags are the following:
* `develop-{sha}`: for the merge in the `develop` branch
* `ce-{semver}` and `ce-{semver}-{sha}`: for the merge un the `main` branch for the community edition

Semver stands for "Semantic versioning" which is explained [here](https://semver.org/)
