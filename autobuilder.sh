#!/bin/bash

mkdir -p out/pass out/fail out/ignore

( cd build && git remote update )

if [ -n "$*" ]; then
	branches="$*"
else
	branches=$( (cd build && git-branch -r) )
fi

did_something=1
while [ -n "$did_something" ]; do
	did_something=
	for branch in $(./branches.sh | sed 's/^[0-9a-f]* //'); do
		ref=$(./next-rev.sh $branch)
		if [ -z "$ref" ]; then
			echo "$branch: already up to date."
			continue;
		fi
		did_something=1
		echo "Building $branch: $ref"
		set -m
		./run-build.sh $ref &
		XPID=$!
		trap "echo 'Killing (SIGINT)';  kill -TERM -$XPID; exit 1" SIGINT
		trap "echo 'Killing (SIGTERM)'; kill -TERM -$XPID; exit 1" SIGTERM
		wait; wait
	done
	
	sleep 5
done

exit 0
