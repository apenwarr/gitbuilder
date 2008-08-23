#!/bin/bash
DIR=$(dirname $0)
cd "$DIR/build"

git show-ref |
	grep -v ' refs/heads/' |
	grep -v '/HEAD$' |
	sed -e 's, [^/]*/[^/]*/, ,' |
	while read commit branch; do
		if [ -e ../out/ignore/$commit ]; then
			continue;
		fi
		echo "$branch"
	done
