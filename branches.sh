#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

if [ -e ../branches-local ]; then
    exec ../branches-local "$@"
fi

if [ "$1" = "-v" ]; then
	VERBOSE=1
else
	VERBOSE=
fi

refs=$(git show-ref -d)

(echo "$refs" | grep -E 'main|master';  # build main and master first
 echo "$refs" | grep -vE 'main|master') |
	grep -v ' refs/heads/' |
	grep -v '/HEAD$' |
	grep -v '\.trac$' |
	grep -v ' refs/stash$' |
	sed -e 's, [^/]*/[^/]*/, ,' -e 's,\^{},,' |
	tac |
	while read commit branch; do
		pb="$lb"
		lb="$branch"
		if [ -e ../out/ignore/$commit -o "$pb" = "$branch" ]; then
			continue
		fi
		[ -n "$VERBOSE" ] && echo -n "$commit "
		echo "$branch"
	done |
	tac
