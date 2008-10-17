#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

if [ "$1" = "-v" ]; then
	VERBOSE=1
else
	VERBOSE=
fi

git show-ref -d |
	grep -v ' refs/heads/' |
	grep -v '/HEAD$' |
	sort -rk 2 |
	sed -e 's, [^/]*/[^/]*/, ,' -e 's,\^{},,' |
	while read commit branch; do
		pb="$lb"
		lb="$branch"
		if [ -e ../out/ignore/$commit -o "$pb" = "$branch" ]; then
			continue;
		fi
		[ -n "$VERBOSE" ] && echo -n "$commit "
		echo "$branch"
	done
