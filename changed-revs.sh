#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

git rev-list --first-parent --pretty='format:%H %ce %s' "$@" |
	while read commit email comment; do
		[ "$commit" = "commit" ] && continue
		if [ -f ../out/lastlog/$commit ]; then
			# we've already printed a changelog for this one
			break;
		fi
		echo "$commit $email $comment"
	done
