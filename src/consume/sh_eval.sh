#!/usr/bin/env bash

chmod +x "/functions/${1}.sh"
bash "/functions/${1}.sh" 2>&1
