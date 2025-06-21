#!/bin/bash

python -m grpc_tools.protoc -I protos/ \
    --python_out=./server/generated/ \
    --grpc_python_out=./server/generated/ \
    protos/tracking.proto