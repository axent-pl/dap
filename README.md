# DAP (Data Analytics Platform)

## Services

### datastore-api

This service is an abstraction layer over S3 (and can be used over other storages like filesystem). It provides a simple API for datasets and ensures that they follow a common convention:
* `Dataset` has many `Variants` and `Variant` can not exist without a `Dataset`
* `Variant` has many `Dataparts` and `Datapart` can not exist without a `Variant`

For example `Dataset` *instagram-posts* may have following contents:
* *instagram-posts*

Additionally the datastore-api serves the representations of the Dataset resource providing uri for each of its parts. It is meant to test [some concenpts described by Roy T. Fielding](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven).

### datastore-s3-config-job

This service is designed to configure the S3 datastore:
* create bucket
* create user and add readwrite policy to that user

When successful should finish with exit(0) statu.