#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

if [ "$1" = "-v" ]; then
	VERBOSE=1
else
	VERBOSE=
fi

git show-ref |
	grep -v ' refs/heads/' |
	grep -v '/HEAD$' |
	sed -e 's, [^/]*/[^/]*/, ,' |
	while read commit branch; do
		if [ -e ../out/ignore/$commit ]; then
			continue;
		fi
		[ -n "$VERBOSE" ] && echo -n "$commit "
		echo "$branch"
	done
