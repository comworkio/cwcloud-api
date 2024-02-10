#!/usr/bin/env bash

cd /functions
go run "${1}.go" 2>&1
