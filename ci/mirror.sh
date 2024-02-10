#!/usr/bin/env bash

REPO_PATH="${HOME_PROJECT}/cmd-api/"

cd "${REPO_PATH}" && git pull origin main || :
git push github main 
git push pgitlab main
exit 0
