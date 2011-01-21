#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

if [ -x ../branches-local ]; then
    exec ../branches-local "$@"
fi

if [ "$1" = "-v" ]; then
	VERBOSE=1
else
	VERBOSE=
fi

git show-ref -d |
	grep -v ' refs/heads/' |
	grep -v '/HEAD$' |
	sed -e 's, [^/]*/[^/]*/, ,' -e 's,\^{},,' |
	tac |
	while read commit branch; do
		pb="$lb"
		lb="$branch"
		if [ -e ../out/ignore/$commit -o "$pb" = "$branch" ]; then
			continue;
		fi
		[ -n "$VERBOSE" ] && echo -n "$commit "
		echo "$branch"
	done |
	tac
