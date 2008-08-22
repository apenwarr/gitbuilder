#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

#ls ../out/pass/* |
#	sed -e 's,^\(.*/\)*\([0-9a-f]*\).*$,^\2^,g' |
git rev-list --first-parent --pretty=oneline "$@" |
	while read commit comment; do
		echo "$commit $comment"
		if [ -f ../out/pass/$commit -o -f ../out/ignore/$commit ]; then
			exit 0;
		fi
	done
