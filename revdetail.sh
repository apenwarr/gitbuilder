#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

git log --first-parent --name-only --pretty=raw --no-walk "$@" -- | cat
