#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

git show-ref |
	grep -v '^refs/heads/' |
	grep -v '/HEAD$' |
	sed -e 's, [^/]*/[^/]*/, ,'
