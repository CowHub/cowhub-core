#!/bin/bash

docker build -t cowhub/cowhub-core . && \
docker tag cowhub/cowhub-core cowhub/cowhub-core:latest
