# DAP (Data Analytics Platform)

## Services

### datastore-api

This service is an abstraction layer over S3 (and can be used over other storages like filesystem or data lake of some kind). It provides a simple API for datasets and ensures that they follow a common convention:
* `Dataset` has many `Variants` and `Variant` can not exist without a `Dataset`
* `Variant` has many `Dataparts` and `Datapart` can not exist without a `Variant`

Additionally the datastore-api serves the representations of the Dataset resource providing uri for each of its parts. It is meant to test [some concenpts described by Roy T. Fielding](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven) like the one blow:
> A REST API must not define fixed resource names or hierarchies (an obvious coupling of client and server). Servers must have the freedom to control their own namespace. Instead, allow servers to instruct clients on how to construct appropriate URIs, such as is done in HTML forms and URI templates, by defining those instructions within media types and link relations. [Failure here implies that clients are assuming a resource structure due to out-of band information, such as a domain-specific standard, which is the data-oriented equivalent to RPC’s functional coupling].

For validating such concept the *datastore-api* provides full URL for any related resources so there is no need for client to know how to construct the URLs and a *datastore-api* has a freedom of changing the URL structures.

### datastore-s3-config-job

This service is designed to configure the S3 datastore:
* create bucket
* create user and add readwrite policy to that user

When successful should finish with exit(0) statu.