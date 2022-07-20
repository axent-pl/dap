#!/usr/bin/bash
set -e
docker build . -t dap-tests
docker run --network="host" dap-tests 