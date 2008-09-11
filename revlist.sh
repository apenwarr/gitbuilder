#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

#ls ../out/pass/* |
#	sed -e 's,^\(.*/\)*\([0-9a-f]*\).*$,^\2^,g' |
git rev-list --first-parent --pretty='format:%H %ce %s' "$@" |
	while read commit email comment; do
		[ "$commit" = "commit" ] && continue
		if [ -f ../out/ignore/$commit ]; then
			# never print an ignored commit
			exit 0;
		fi
		echo "$commit $email $comment"
		if [ -f ../out/pass/$commit ]; then
			# print the first passing commit, then done
			exit 0;
		fi
	done
