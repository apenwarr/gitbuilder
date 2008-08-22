#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

git show-ref |
	sed -e 's, [^/]*/[^/]*/, ,'
